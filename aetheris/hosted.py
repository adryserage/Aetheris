"""Hosted mode: the MCP server over streamable HTTP, published behind MCP Hub.

This app is an OAuth resource server only (RFC 9728). Executor (OAUTH_EMETTEUR) registers the
clients, runs the consent and issues the tokens. A token passes when it equals the service key
(MCP_TOKEN) or when Executor's get-session returns an active session for it. The verdict is kept
60 s under the token's SHA-256: a revoked token stays accepted for at most one minute. An
Executor outage refuses without being kept. get-session does not say which account the token was
issued for, so any valid Executor session opens this server: the hub is private, one account.

Same design as CV Builder (adryserage/cv-builder-mcp, src/executor.ts and src/application.ts).
Traefik publishes the app under a path prefix (/aetheris); the prefix is removed when it reaches
the app, so both router settings serve the same routes.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import math
import os
import sys
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

import anyio
import httpx2
from starlette.applications import Starlette
from starlette.datastructures import Headers
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from aetheris.server import build_server

SESSION_PATH = "/api/auth/mcp/get-session"
VERDICT_SECONDS = 60.0
MAX_VERDICTS = 1000
SESSION_TIMEOUT_SECONDS = 10.0
MIN_KEY_LENGTH = 32
MAX_BODY_BYTES = 4 * 1024 * 1024

log = logging.getLogger("aetheris")


class ConfigError(ValueError):
    """A missing or invalid environment variable. The message names it, never its value."""


@dataclass(frozen=True)
class HostedConfig:
    base: str
    """Public base as clients see it, no trailing slash: https://mcp.allowebs.app/aetheris."""
    prefix: str
    """Path of the base (/aetheris), removed from requests when it reaches the app."""
    issuer: str
    """Executor's origin, the authorization server: https://mcp.allowebs.app."""
    service_key: str
    allowed_hosts: frozenset[str]
    port: int
    sentry_dsn: str | None
    sentry_environment: str


def _url(name: str, value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        raise ConfigError(f"{name} is required")
    parts = urlsplit(raw)
    loopback = parts.hostname in ("localhost", "127.0.0.1")
    secure = parts.scheme == "https" or (loopback and parts.scheme == "http")
    if not secure or not parts.hostname or parts.query or parts.fragment or parts.username:
        raise ConfigError(f"{name} must be an https URL without query or fragment")
    return f"{parts.scheme}://{parts.netloc}{parts.path.rstrip('/')}"


def read_config(env: Mapping[str, str]) -> HostedConfig:
    """The only place that reads the environment. Refuses to start rather than guess."""
    base = _url("AETHERIS_BASE_PUBLIQUE", env.get("AETHERIS_BASE_PUBLIQUE"))
    hosts = frozenset(
        h.strip().lower() for h in env.get("AETHERIS_HOTES_AUTORISES", "").split(",") if h.strip()
    )
    if not hosts:
        raise ConfigError("AETHERIS_HOTES_AUTORISES is required (e.g. mcp.allowebs.app,localhost)")
    key = env.get("MCP_TOKEN", "").strip()
    if not key:
        raise ConfigError("MCP_TOKEN is required")
    if len(key) < MIN_KEY_LENGTH:
        raise ConfigError(f"MCP_TOKEN must be at least {MIN_KEY_LENGTH} characters long")
    try:
        port = int(env.get("PORT", "8080"))
    except ValueError:
        port = 0
    if port <= 0:
        raise ConfigError("PORT must be a positive integer")
    return HostedConfig(
        base=base,
        prefix=urlsplit(base).path.rstrip("/"),
        issuer=_url("OAUTH_EMETTEUR", env.get("OAUTH_EMETTEUR")),
        service_key=key,
        allowed_hosts=hosts,
        port=port,
        sentry_dsn=env.get("SENTRY_DSN", "").strip() or None,
        sentry_environment=env.get("SENTRY_ENVIRONMENT", "").strip() or "production",
    )


FetchSession = Callable[[str, str], Awaitable[tuple[int, Any]]]
"""(url, token) -> (HTTP status, JSON body when 2xx else None). May raise."""


async def fetch_session(url: str, token: str) -> tuple[int, Any]:
    async with httpx2.AsyncClient() as client:
        response = await client.get(
            url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
        )
    return response.status_code, response.json() if response.is_success else None


def _expiry(raw: Any) -> float | None:
    """accessTokenExpiresAt as epoch seconds; None when absent; NaN when unreadable."""
    if raw is None or raw == "":
        return None
    try:
        if isinstance(raw, bool):
            raise TypeError
        if isinstance(raw, (int, float)):
            return float(raw) / 1000  # a JavaScript timestamp, in milliseconds
        when = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return float("nan")
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when.timestamp()


class SessionVerifier:
    """Asks Executor whether a token holds an active session, and keeps the verdict 60 s."""

    def __init__(
        self,
        issuer: str,
        fetch: FetchSession = fetch_session,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._url = issuer + SESSION_PATH
        self._fetch = fetch
        self._clock = clock
        self._verdicts: dict[str, tuple[bool, float]] = {}

    async def __call__(self, token: str) -> bool:
        key = hashlib.sha256(token.encode()).hexdigest()
        now = self._clock()
        known = self._verdicts.get(key)
        if known and known[1] > now:
            return known[0]

        try:
            with anyio.fail_after(SESSION_TIMEOUT_SECONDS):
                status, body = await self._fetch(self._url, token)
        except Exception:
            return False
        if status >= 500:
            return False
        session = body if 200 <= status < 300 and isinstance(body, dict) else {}

        end = _expiry(session.get("accessTokenExpiresAt"))
        expired = end is not None and (math.isnan(end) or end <= now)
        valid = bool(session.get("userId")) and not expired

        self._verdicts.pop(key, None)
        while len(self._verdicts) >= MAX_VERDICTS:
            del self._verdicts[next(iter(self._verdicts))]
        # As in JavaScript's Math.min, an unreadable expiry (NaN) is stored but is never fresh.
        until = now + VERDICT_SECONDS
        if end is not None:
            until = end if math.isnan(end) else min(until, end)
        self._verdicts[key] = (valid, until)
        return valid


def resource_metadata(base: str, issuer: str) -> dict[str, Any]:
    return {
        "resource": f"{base}/mcp",
        "authorization_servers": [issuer],
        "scopes_supported": ["openid", "profile", "email", "offline_access"],
        "bearer_methods_supported": ["header"],
        "resource_name": "Aetheris",
    }


def _same(a: str, b: str) -> bool:
    return hmac.compare_digest(
        hashlib.sha256(a.encode()).digest(), hashlib.sha256(b.encode()).digest()
    )


def _bearer(header: str | None) -> str | None:
    if not header or "\n" in header or header[:7].lower() != "bearer " or len(header) == 7:
        return None
    return header[7:].strip()


class RequireToken:
    """401 with the resource metadata link unless the token is the service key or a session."""

    def __init__(
        self, app: ASGIApp, base: str, service_key: str, verify: Callable[[str], Awaitable[bool]]
    ) -> None:
        self.app = app
        self.service_key = service_key
        self.verify = verify
        self.challenge = f'Bearer resource_metadata="{base}/.well-known/oauth-protected-resource"'

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        token = _bearer(Headers(scope=scope).get("authorization"))
        if token is not None and (_same(token, self.service_key) or await self.verify(token)):
            await self.app(scope, receive, send)
            return
        challenge = self.challenge if token is None else f'{self.challenge}, error="invalid_token"'
        response = JSONResponse(
            {"error": "authentication required"},
            status_code=401,
            headers={"WWW-Authenticate": challenge},
        )
        await response(scope, receive, send)


class StripPrefix:
    def __init__(self, app: ASGIApp, prefix: str) -> None:
        self.app = app
        self.prefix = prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = scope.get("path", "")
        if self.prefix and scope["type"] == "http":
            if path == self.prefix or path.startswith(self.prefix + "/"):
                scope = dict(scope, path=path[len(self.prefix) :] or "/")
                scope.pop("raw_path", None)
        await self.app(scope, receive, send)


def _hostname(value: str) -> str:
    """Hostname of a Host header (host[:port]) or of an Origin (scheme://host[:port])."""
    netloc = value.split("://", 1)[1] if "://" in value else value
    try:
        return (urlsplit("//" + netloc).hostname or "").lower()
    except ValueError:
        return ""


class AllowedHosts:
    """421 when Host is not allowed (DNS rebinding), 403 when a browser Origin is not allowed."""

    def __init__(self, app: ASGIApp, hosts: frozenset[str]) -> None:
        self.app = app
        self.hosts = hosts

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            origin = headers.get("origin")
            if _hostname(headers.get("host", "")) not in self.hosts:
                await JSONResponse({"error": "host not allowed"}, 421)(scope, receive, send)
                return
            if origin is not None and _hostname(origin) not in self.hosts:
                await JSONResponse({"error": "origin not allowed"}, 403)(scope, receive, send)
                return
        await self.app(scope, receive, send)


class BodyLimit:
    """413 past MAX_BODY_BYTES. The body is read up front, then replayed to the app."""

    def __init__(self, app: ASGIApp, limit: int = MAX_BODY_BYTES) -> None:
        self.app = app
        self.limit = limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        too_big = JSONResponse({"error": f"request body over {self.limit} bytes"}, 413)
        try:
            declared = int(Headers(scope=scope).get("content-length", "0"))
        except ValueError:
            declared = 0
        if declared > self.limit:
            await too_big(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] != "http.request":
                await self.app(scope, _replay([message], receive), send)
                return
            body.extend(message.get("body", b""))
            if len(body) > self.limit:
                await too_big(scope, receive, send)
                return
            if not message.get("more_body", False):
                break
        whole: Message = {"type": "http.request", "body": bytes(body), "more_body": False}
        await self.app(scope, _replay([whole], receive), send)


def _replay(messages: list[Message], receive: Receive) -> Receive:
    pending = list(messages)

    async def replayed() -> Message:
        return pending.pop(0) if pending else await receive()

    return replayed


def build_app(
    config: HostedConfig, verify: Callable[[str], Awaitable[bool]] | None = None
) -> Starlette:
    mcp = build_server(hosted=True)
    endpoint = RequireToken(
        mcp.streamable_http_app(
            host="0.0.0.0",  # Host and Origin are checked by AllowedHosts, not by the SDK
            stateless_http=True,
            json_response=True,
        ),
        config.base,
        config.service_key,
        verify or SessionVerifier(config.issuer),
    )
    metadata = resource_metadata(config.base, config.issuer)

    async def health(_: Request) -> Response:
        return JSONResponse({"statut": "ok"})

    async def protected_resource(_: Request) -> Response:
        return JSONResponse(metadata, headers={"Cache-Control": "no-store"})

    return Starlette(
        routes=[
            Route("/sante", health, methods=["GET"]),
            Route("/.well-known/oauth-protected-resource", protected_resource, methods=["GET"]),
            Route("/.well-known/oauth-protected-resource/mcp", protected_resource, methods=["GET"]),
            Route("/mcp", endpoint),
        ],
        middleware=[
            Middleware(StripPrefix, prefix=config.prefix),
            Middleware(AllowedHosts, hosts=config.allowed_hosts),
            Middleware(BodyLimit),
        ],
        lifespan=lambda _app: mcp.session_manager.run(),
    )


def _scrub(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any]:
    """Keep only the method and the URL without query; drop the user and the breadcrumbs."""
    request = event.get("request")
    if request:
        url = str(request.get("url") or "").split("?", 1)[0].split("#", 1)[0]
        event["request"] = {"method": request.get("method"), "url": url}
    event.pop("user", None)
    event.pop("breadcrumbs", None)
    return event


def start_error_reporting(config: HostedConfig) -> bool:
    """Bugsink (Sentry protocol), off until SENTRY_DSN is set. Errors only, no personal data."""
    if not config.sentry_dsn:
        return False
    import sentry_sdk

    sentry_sdk.init(
        dsn=config.sentry_dsn,
        environment=config.sentry_environment,
        release=os.environ.get("SOURCE_COMMIT", "").strip() or None,
        server_name="mcphub-aetheris",
        send_default_pii=False,
        include_local_variables=False,  # frame locals would carry the files sent
        max_breadcrumbs=0,
        before_send=_scrub,  # type: ignore[arg-type]
    )
    return True


def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    log.setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    try:
        config = read_config(os.environ)
    except ConfigError as exc:
        print(f"aetheris: cannot start the hosted server: {exc}", file=sys.stderr)
        sys.exit(2)
    start_error_reporting(config)
    import uvicorn

    uvicorn.run(
        build_app(config),
        host="0.0.0.0",
        port=config.port,
        log_config=None,
        access_log=False,
        server_header=False,
    )
