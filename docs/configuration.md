# Configuration Guide

## Environment Variables

Create a `.env` file in your project root or set environment variables.

### Core Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_PROVIDER` | AI provider (`gemini`, `openai`, `claude`) | `gemini` |
| `AI_MODEL` | Model to use | Provider default |
| `GEMINI_API_KEY` | Gemini API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Claude API key | - |

### Analysis Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `ROOT_DIR` | Directory to analyze | `.` |
| `OUTPUT_DIR` | Output directory for reports | `docs/analyses` |
| `ARCHITECTURE_REPORT` | Architecture report path | `docs/architecture_overview.md` |
| `BATCH_SIZE` | Files analyzed in parallel | `10` |
| `MAX_RETRIES` | Retry attempts on error | `3` |
| `TIMEOUT_SECONDS` | Request timeout | `60` |

### Feature Toggles

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_WEB_SEARCH` | Enable documentation search | `true` |
| `ENABLE_SECURITY_ANALYSIS` | Enable security analysis | `true` |
| `ENABLE_METRICS_ANALYSIS` | Enable code metrics | `true` |
| `ENABLE_DEPENDENCY_VULNERABILITY` | Enable CVE scanning | `true` |
| `ENABLE_CODE_GENERATION` | Enable code analysis generation | `true` |
| `SHOW_REASONING` | Show AI reasoning process | `false` |

### Cache Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_CACHE` | Enable analysis caching | `true` |
| `CACHE_TTL_DAYS` | Cache lifetime in days | `7` |

### Dependency Analysis

| Variable | Description | Default |
|----------|-------------|---------|
| `ANALYZE_DEPENDENT_FILES` | Analyze dependent files | `true` |
| `MAX_DEPENDENCY_DEPTH` | Max dependency depth | `2` |
| `ENABLE_EXPORT_ANALYSIS` | Extract exports | `true` |
| `ENABLE_REVERSE_DEPENDENCY` | Reverse dependency graph | `true` |
| `ENABLE_IMPACT_ANALYSIS` | Bug impact analysis | `true` |
| `MAX_IMPACT_DEPTH` | Max impact depth | `3` |

### Gemini Advanced Features

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_STRUCTURED_OUTPUTS` | JSON validated via Pydantic | `true` |
| `ENABLE_THINKING` | Show reasoning process | `false` |
| `THINKING_BUDGET` | Thinking token budget | `1024` |
| `ENABLE_CODE_EXECUTION` | Python sandbox execution | `false` |
| `ENABLE_FUNCTION_CALLING` | Auto function calling | `false` |
| `ENABLE_CONTEXT_CACHING` | Context cache (-50% cost) | `true` |
| `CONTEXT_CACHE_TTL_SECONDS` | Context cache TTL | `3600` |
| `ENABLE_BATCH_MODE` | Batch API (-50% cost) | `false` |

### Bug Fixing

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_CLAUDE_CODE_FIX` | Enable Claude Code integration | `true` |
| `FIX_SEVERITY_THRESHOLD` | Minimum severity to fix | `medium` |

## Example `.env` File

```env
# AI Provider
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
AI_MODEL=gemini-2.0-flash-exp

# Analysis
BATCH_SIZE=10
TIMEOUT_SECONDS=120
OUTPUT_DIR=docs/analyses

# Features
ENABLE_SECURITY_ANALYSIS=true
ENABLE_METRICS_ANALYSIS=true
ENABLE_DEPENDENCY_VULNERABILITY=true

# Cache
ENABLE_CACHE=true
CACHE_TTL_DAYS=7

# Gemini Advanced
ENABLE_STRUCTURED_OUTPUTS=true
ENABLE_CONTEXT_CACHING=true
```

## Setting Environment Variables

### Linux/macOS

```bash
export AI_PROVIDER=gemini
export GEMINI_API_KEY=your_key_here
```

### Windows (PowerShell)

```powershell
$env:AI_PROVIDER='gemini'
$env:GEMINI_API_KEY='your_key_here'
```

### Windows (CMD)

```cmd
set AI_PROVIDER=gemini
set GEMINI_API_KEY=your_key_here
```

## Next Steps

- [AI Providers](./ai-providers.md) - Models and pricing
- [Commands Reference](./commands/README.md) - Available commands
