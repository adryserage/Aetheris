# User Story Command

The `aetheris user-story` command analyzes user flows and traces frontend-backend interactions.

## Usage

```bash
aetheris user-story [options]
```

## Input Modes (Required, mutually exclusive)

| Option | Description |
|--------|-------------|
| `--text TEXT` | User story as text description |
| `--file FILE` | Markdown file with user stories |
| `--entry FILE` | Code file as entry point (e.g., LoginButton.tsx) |
| `--auto` | Auto-detect all user flows |

## Output Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output-format` | `markdown`, `json`, or `both` | `both` |
| `--diagram` | `mermaid`, `plantuml`, `both`, or `none` | `mermaid` |
| `--output-file` | Output file path | `docs/user-stories/analysis.md` |
| `--severity` | Minimum severity for issues | `low` |

## Examples

### From Text Description
```bash
aetheris user-story --text "When user clicks Login, redirect to dashboard"
```

### From Markdown File
```bash
aetheris user-story --file docs/user-stories.md
```

### From Code Entry Point
```bash
aetheris user-story --entry src/components/LoginButton.tsx
```

### Auto-Detect All Flows
```bash
aetheris user-story --auto
```

### With Diagram Format
```bash
aetheris user-story --auto --diagram mermaid
aetheris user-story --auto --diagram plantuml
```

### JSON Output Only
```bash
aetheris user-story --auto --output-format json
```

### Filter High Severity
```bash
aetheris user-story --auto --severity high
```

## Configuration File

Instead of passing CLI flags repeatedly, you can persist settings in a `config.json` file. Aetheris follows this priority order (highest to lowest):

1. **CLI flags** - Override everything
2. **Local `config.json`** - Project-specific settings
3. **Global `~/.aetheris/config.json`** - User-wide defaults
4. **Environment variables** - From `.env`
5. **Built-in defaults**

### Example Configuration

```json
{
  "user_story": {
    "output_format": "both",
    "diagram": "mermaid",
    "output_file": "docs/user-stories/analysis.md",
    "severity": "low"
  }
}
```

### Configuration Options

| JSON Key | CLI Equivalent | Description |
|----------|----------------|-------------|
| `user_story.output_format` | `--output-format` | `markdown`, `json`, or `both` |
| `user_story.diagram` | `--diagram` | `mermaid`, `plantuml`, `both`, or `none` |
| `user_story.output_file` | `--output-file` | Output file path |
| `user_story.severity` | `--severity` | Minimum severity threshold |

See [Configuration Guide](../configuration.md) for all options and the full `config.json` schema.

## Issues Detected

| Type | Description |
|------|-------------|
| `orphan_endpoint` | Endpoint defined but never called |
| `missing_handler` | API call without corresponding endpoint |
| `missing_error_handling` | API call without try/catch |
| `race_condition` | Concurrent calls on same state |
| `missing_auth` | Sensitive endpoint without authentication |
| `dead_code` | Code never executed in the flow |

## Supported Frameworks

> **Note**: Versions listed are minimum supported. Syntax detection may not work correctly for older versions due to breaking API changes.

### Frontend

| Library | Min Version | Notes |
|---------|-------------|-------|
| fetch | (native) | Browser/Node.js native API |
| axios | 0.21+ | Earlier versions have different interceptor syntax |
| SWR | 1.0+ | v1.0 introduced new API patterns |
| React Query / TanStack Query | 3.0+ | v3/v4/v5 supported; v2 syntax differs significantly |
| dio (Dart) | 4.0+ | v4.0 introduced interceptors redesign |
| requests (Python) | 2.20+ | Session handling standardized |
| httpx (Python) | 0.23+ | Async client API stabilized |

### Backend

| Framework | Min Version | Notes |
|-----------|-------------|-------|
| Express.js | 4.17+ | v5.x also supported; v3.x syntax not detected |
| Next.js | 12.0+ | App Router (Route Handlers, Server Actions) and Pages Router (API Routes) both supported |
| FastAPI | 0.68+ | Depends on Starlette 0.14+; older versions have different routing |
| Flask | 2.0+ | v2.0 introduced async support; v1.x partially supported |
| Django | 3.2+ | Class-based views and path() syntax required |
| NestJS | 8.0+ | Decorator syntax standardized in v8 |

### Version Detection

Aetheris attempts to auto-detect framework versions from:
- `package.json` (Node.js projects)
- `requirements.txt` / `pyproject.toml` (Python projects)
- `pubspec.yaml` (Dart/Flutter projects)

If version detection fails, the latest stable syntax is assumed. Use `--framework-version` to override:

```bash
aetheris user-story --auto --framework-version "nextjs=12,express=4"
```

## Output

Analysis generates:
- Flow diagrams (Mermaid/PlantUML)
- Issues by severity
- Orphan endpoints list
- Missing handlers list
- JSON report (optional)
