"""Manifest parsing and the OSV lookup (the only network call in Aetheris)."""

import json
import logging
import re
from pathlib import Path
from typing import Any

import requests
import yaml

from aetheris.checks.base import CheckContext, make_finding
from aetheris.domain import Finding

log = logging.getLogger(__name__)

OSV_URL = "https://api.osv.dev/v1/querybatch"
OSV_TIMEOUT_SECONDS = 15
MAX_PACKAGES = 500
BATCH_SIZE = 500

_EXACT = re.compile(r"^[0-9][\w.+\-]*$")
_PY_PIN = re.compile(r"([A-Za-z0-9][A-Za-z0-9_.\-]*)(?:\[[^\]]*\])?\s*==\s*([0-9][\w.+\-]*)")
_PY_PIN_QUOTED = re.compile(
    r"""["']([A-Za-z0-9][A-Za-z0-9_.\-]*)(?:\[[^\]]*\])?\s*==\s*([0-9][\w.+\-]*)["']"""
)

Package = tuple[str, str, str]  # (ecosystem, name, version)


def _clean(version: object) -> str | None:
    if not isinstance(version, str):
        return None
    cleaned = version.strip().lstrip("^~=v ")
    return cleaned if _EXACT.match(cleaned) else None


def parse_package_json(text: str) -> list[Package]:
    data = json.loads(text)
    out: list[Package] = []
    for section in ("dependencies", "devDependencies"):
        for name, spec in (data.get(section) or {}).items():
            version = _clean(spec)
            if version:
                out.append(("npm", name, version))
    return out


def parse_pubspec(text: str) -> list[Package]:
    data = yaml.safe_load(text) or {}
    out: list[Package] = []
    for section in ("dependencies", "dev_dependencies"):
        for name, spec in (data.get(section) or {}).items():
            version = _clean(spec)
            if version:
                out.append(("Pub", name, version))
    return out


def parse_requirements(text: str) -> list[Package]:
    out: list[Package] = []
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if not line or line.startswith("-") or "@" in line:
            continue
        match = _PY_PIN.match(line)
        if match:
            out.append(("PyPI", match.group(1), match.group(2)))
    return out


def parse_pyproject(text: str) -> list[Package]:
    return [("PyPI", m.group(1), m.group(2)) for m in _PY_PIN_QUOTED.finditer(text)]


_PARSE_ERRORS = (ValueError, yaml.YAMLError, AttributeError, TypeError)

_PARSERS = {
    "package.json": parse_package_json,
    "pubspec.yaml": parse_pubspec,
    "requirements.txt": parse_requirements,
    "pyproject.toml": parse_pyproject,
}


def manifest_parse(ctx: CheckContext) -> list[Finding]:
    """Reports the manifests that could not be parsed (the packages feed osv_lookup)."""
    findings: list[Finding] = []
    for rel in ctx.files:
        parser = _PARSERS.get(Path(rel).name)
        content = ctx.read(rel) if parser else None
        if parser and content is not None:
            try:
                parser(content)
            except _PARSE_ERRORS as exc:
                findings.append(
                    make_finding(
                        "manifest_parse",
                        "dependency",
                        "low",
                        f"cannot parse {Path(rel).name}: {exc}"[:200],
                        rel,
                    )
                )
    return findings


def query_osv(payload: dict[str, Any]) -> dict[str, Any]:
    """One POST to OSV. Sends package name, ecosystem and version only."""
    response = requests.post(OSV_URL, json=payload, timeout=OSV_TIMEOUT_SECONDS)
    response.raise_for_status()
    result: dict[str, Any] = response.json()
    return result


def _collect_packages(ctx: CheckContext) -> list[tuple[str, Package]]:
    seen: set[tuple[str, Package]] = set()
    ordered: list[tuple[str, Package]] = []
    for rel in ctx.files:
        parser = _PARSERS.get(Path(rel).name)
        content = ctx.read(rel) if parser else None
        if not parser or content is None:
            continue
        try:
            packages = parser(content)
        except _PARSE_ERRORS:
            continue
        for package in packages:
            if (rel, package) not in seen:
                seen.add((rel, package))
                ordered.append((rel, package))
    return ordered


def osv_lookup(ctx: CheckContext) -> list[Finding]:
    entries = _collect_packages(ctx)[:MAX_PACKAGES]
    findings: list[Finding] = []
    for start in range(0, len(entries), BATCH_SIZE):
        chunk = entries[start : start + BATCH_SIZE]
        queries = [
            {"package": {"name": name, "ecosystem": eco}, "version": version}
            for _, (eco, name, version) in chunk
        ]
        try:
            results = query_osv({"queries": queries}).get("results", [])
        except (requests.RequestException, ValueError) as exc:
            ctx.errors.append(f"osv_lookup: OSV unreachable ({type(exc).__name__}); not checked")
            return findings
        for (rel, (_, name, version)), result in zip(chunk, results):
            ids = [v.get("id", "?") for v in (result or {}).get("vulns", [])]
            if ids:
                shown = ", ".join(ids[:5]) + (f" (+{len(ids) - 5} more)" if len(ids) > 5 else "")
                findings.append(
                    make_finding(
                        "osv_lookup",
                        "dependency",
                        "high",
                        f"{name}@{version} has known vulnerabilities: {shown}; "
                        "see https://osv.dev/vulnerability/<id> for severity and the fixed version",
                        rel,
                    )
                )
    return findings
