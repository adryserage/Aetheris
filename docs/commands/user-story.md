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

### Frontend
- fetch
- axios
- SWR
- React Query
- dio (Dart)
- requests
- httpx

### Backend
- Express.js
- Next.js API Routes
- FastAPI
- Flask
- Django
- NestJS

## Output

Analysis generates:
- Flow diagrams (Mermaid/PlantUML)
- Issues by severity
- Orphan endpoints list
- Missing handlers list
- JSON report (optional)
