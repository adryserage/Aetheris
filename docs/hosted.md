# Hosted mode

`aetheris serve --http` runs the same six tools over MCP streamable HTTP, so one instance can serve several people or machines. A hosted server never reads a disk: your assistant sends the contents of the files it wants checked.

Use the [stdio server](installation.md) on your own machine. Run hosted mode only when you operate a shared instance behind a reverse proxy.

## Install

Install the package with the `hosted` extra, which adds the Sentry SDK for error reporting. The HTTP server itself comes with the `mcp` dependency.

```bash
pip install "adryserage-aetheris[hosted]"
aetheris serve --http
```

Or build the Docker image from a checkout of the repository:

```bash
docker build -t aetheris-hosted .
docker run --env-file aetheris.env -p 8080:8080 aetheris-hosted
```

The image runs `aetheris serve --http` as an unprivileged user (UID 10001) and listens on port 8080. It includes `curl` for container health checks.

## Configuration

The server reads its configuration from environment variables when it starts. A missing or invalid variable stops it with exit code 2 and a message that names the variable, never its value.

| Variable | Required | Meaning |
| --- | --- | --- |
| `AETHERIS_BASE_PUBLIQUE` | yes | Public URL of the server as clients see it, such as `https://mcp.example.com/aetheris`. It must use `https`, except on `localhost` or `127.0.0.1`, and have no query or fragment. |
| `AETHERIS_HOTES_AUTORISES` | yes | Comma-separated host names accepted in the `Host` and `Origin` headers, such as `mcp.example.com,localhost`. |
| `MCP_TOKEN` | yes | Service key, at least 32 characters. A request that sends it as its bearer token is accepted. |
| `OAUTH_EMETTEUR` | yes | Origin of the OAuth authorization server, such as `https://mcp.example.com`. Same URL rules as `AETHERIS_BASE_PUBLIQUE`. |
| `PORT` | no | Port to listen on. Default: `8080`. |
| `SENTRY_DSN` | no | Turns on error reporting to Sentry or a compatible service. Off when unset. |
| `SENTRY_ENVIRONMENT` | no | Environment name sent with errors. Default: `production`. |

The path of `AETHERIS_BASE_PUBLIQUE` (`/aetheris` in the example) is removed from incoming requests. The server answers the same routes whether your proxy keeps that prefix or strips it.

## Routes

| Route | Authentication | Response |
| --- | --- | --- |
| `GET /sante` | none | `{"statut": "ok"}`, for health checks |
| `GET /.well-known/oauth-protected-resource` | none | Protected resource metadata ([RFC 9728](https://www.rfc-editor.org/rfc/rfc9728)) |
| `GET /.well-known/oauth-protected-resource/mcp` | none | The same metadata |
| `/mcp` | bearer token | The MCP endpoint, stateless, with JSON responses |

The metadata names `<base>/mcp` as the resource and `OAUTH_EMETTEUR` as the only authorization server.

## Authentication

Every request to `/mcp` needs an `Authorization: Bearer <token>` header. The server accepts the token in two cases:

- It equals `MCP_TOKEN`. The comparison takes constant time.
- The authorization server confirms an active session for it. The server calls `GET <OAUTH_EMETTEUR>/api/auth/mcp/get-session` with the token and accepts a JSON answer that has a `userId` and no `accessTokenExpiresAt` in the past.

The answer is cached for 60 seconds under the SHA-256 hash of the token, so a revoked token can still pass for up to one minute. When the authorization server times out after 10 seconds or answers with a 5xx status, the request is refused and nothing is cached.

The session check does not say which account the token belongs to: any active session on the authorization server opens the hosted instance. Keep that server limited to the people who should use Aetheris.

A request without a valid token gets a 401 response with `WWW-Authenticate: Bearer resource_metadata="<base>/.well-known/oauth-protected-resource"`, so an MCP client can discover where to sign in.

## Tools in hosted mode

The six tools keep their names, and the [review flow](review-flow.md) stays the same. Two tools take file contents instead of paths on disk:

| Tool | Hosted arguments | Difference from stdio |
| --- | --- | --- |
| `plan_review` | `files` (each with a `path`), `preset`, `agents` | No `scope`, `base` or `paths`: there is no git and no disk. Agents are chosen from the file names you send. |
| `run_checks` | `agent`, `files` (each with a `path` and its full `content`) | Checks run on the contents you send. |

`list_agents`, `get_rules`, `get_playbook` and `synthesize_report` take the same arguments as in [Tools](tools.md).

A path you send is only a label. It must be relative, with no `..`, no NUL byte and no drive letter. The same path twice in one call is refused.

## Limits

- At most 100 files per call to `plan_review` or `run_checks`.
- At most 1 MiB per file. A file whose content looks binary is skipped.
- At most 4 MiB per request body. A larger request gets a 413 response.

Split a larger review into several `run_checks` calls.

## Request checks

- A `Host` header that is not in `AETHERIS_HOTES_AUTORISES` gets a 421 response, which blocks DNS rebinding.
- A browser `Origin` header that is not in the list gets a 403 response.

## What the server keeps and logs

- Nothing is stored. Each request is handled on its own, and the file contents are dropped once the answer is sent.
- Logs never contain file contents or paths. For each `run_checks` call, the server logs the agent, the number of files, their total size and the duration. The access log is off.
- Error reports, when `SENTRY_DSN` is set, keep only the HTTP method and the URL without its query string. They carry no user, no breadcrumbs and no local variables, so the files you sent never reach them.
- As in stdio mode, the only outgoing call apart from the session check is the `osv_lookup` check of the dependency agent, which sends package names, ecosystems and versions to the [OSV API](https://osv.dev).
