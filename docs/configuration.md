# Configuration Guide

## Environment Variables

Create a `.env` file in your project root or set environment variables.

> ⚠️ **SECURITY WARNING**: Always add `.env` to your `.gitignore` file to prevent accidentally committing API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) to version control. Exposed API keys can lead to unauthorized usage and significant costs.
>
> ```bash
> echo ".env" >> .gitignore
> ```

### Type Reference

| Type | Description | Examples |
|------|-------------|----------|
| `string` | Text value | `gemini-2.0-flash-exp`, `docs/analyses` |
| `integer` | Whole number (constraints noted in parentheses) | `10`, `3600` |
| `boolean` | True/false flag | `true`, `false` |
| `enum` | Closed set of valid values (listed in description) | `gemini`, `medium` |

### Core Settings

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `AI_PROVIDER` | `enum` | AI provider. **Valid values**: `gemini`, `openai`, `claude` | `gemini` |
| `AI_MODEL` | `string` | Model identifier (provider-specific) | Provider default |
| `GEMINI_API_KEY` | `string` | Gemini API key | - |
| `OPENAI_API_KEY` | `string` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | `string` | Claude API key | - |

### Analysis Settings

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `ROOT_DIR` | `string` | Directory path to analyze | `.` |
| `OUTPUT_DIR` | `string` | Output directory path for reports | `docs/analyses` |
| `ARCHITECTURE_REPORT` | `string` | Architecture report file path | `docs/architecture_overview.md` |
| `BATCH_SIZE` | `integer` | Number of files analyzed in parallel (≥1) | `10` |
| `MAX_RETRIES` | `integer` | Retry attempts on error (≥0) | `3` |
| `TIMEOUT_SECONDS` | `integer` | Request timeout in seconds (≥1) | `60` |

### Feature Toggles

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `ENABLE_WEB_SEARCH` | `boolean` | Enable documentation search | `true` |
| `ENABLE_SECURITY_ANALYSIS` | `boolean` | Enable security analysis | `true` |
| `ENABLE_METRICS_ANALYSIS` | `boolean` | Enable code metrics | `true` |
| `ENABLE_DEPENDENCY_VULNERABILITY` | `boolean` | Enable CVE scanning | `true` |
| `ENABLE_CODE_GENERATION` | `boolean` | Enable code analysis generation | `true` |
| `SHOW_REASONING` | `boolean` | Show AI reasoning process | `false` |

### Cache Settings

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `ENABLE_CACHE` | `boolean` | Enable analysis caching | `true` |
| `CACHE_TTL_SECONDS` | `integer` | Cache lifetime in seconds (≥0) | `604800` (7 days) |

> **Note**: All duration settings use seconds as the unit for consistency. Common values: 1 hour = `3600`, 1 day = `86400`, 7 days = `604800`.

### Dependency Analysis

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `ANALYZE_DEPENDENT_FILES` | `boolean` | Analyze dependent files | `true` |
| `MAX_DEPENDENCY_DEPTH` | `integer` | Max dependency depth (≥0) | `2` |
| `ENABLE_EXPORT_ANALYSIS` | `boolean` | Extract exports | `true` |
| `ENABLE_REVERSE_DEPENDENCY` | `boolean` | Reverse dependency graph | `true` |
| `ENABLE_IMPACT_ANALYSIS` | `boolean` | Bug impact analysis | `true` |
| `MAX_IMPACT_DEPTH` | `integer` | Max impact depth (≥0) | `3` |

### Gemini Advanced Features

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `ENABLE_STRUCTURED_OUTPUTS` | `boolean` | JSON validated via Pydantic | `true` |
| `ENABLE_THINKING` | `boolean` | Show reasoning process | `false` |
| `THINKING_BUDGET` | `integer` | Thinking token budget (≥0) | `1024` |
| `ENABLE_CODE_EXECUTION` | `boolean` | Python sandbox execution | `false` |
| `ENABLE_FUNCTION_CALLING` | `boolean` | Auto function calling | `false` |
| `ENABLE_CONTEXT_CACHING` | `boolean` | Context cache (-50% cost) | `true` |
| `CONTEXT_CACHE_TTL_SECONDS` | `integer` | Context cache TTL in seconds (≥0) | `3600` |
| `ENABLE_BATCH_MODE` | `boolean` | Batch API (-50% cost) | `false` |

### Bug Fixing

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `ENABLE_CLAUDE_CODE_FIX` | `boolean` | Enable Claude Code integration | `true` |
| `FIX_SEVERITY_THRESHOLD` | `enum` | Minimum severity to fix. **Valid values**: `low`, `medium`, `high`, `critical` | `medium` |

## Example `.env` File

```env
# AI Provider
AI_PROVIDER=gemini
GEMINI_API_KEY=   # Set via environment variable or secrets manager
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
CACHE_TTL_SECONDS=604800  # 7 days

# Gemini Advanced
ENABLE_STRUCTURED_OUTPUTS=true
ENABLE_CONTEXT_CACHING=true
```

> **Security Note**: Never commit API keys to version control. Use a `.env` file (added to `.gitignore`) or a secrets manager like HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault.

## Setting Environment Variables

### Linux/macOS

```bash
export AI_PROVIDER=gemini
export GEMINI_API_KEY="$GEMINI_API_KEY"  # Reference from secure source
# Or load from a secrets manager:
# export GEMINI_API_KEY=$(vault kv get -field=api_key secret/aetheris)
```

### Windows (PowerShell)

```powershell
$env:AI_PROVIDER = 'gemini'
$env:GEMINI_API_KEY = $env:GEMINI_API_KEY  # Reference from secure source
# Or use PowerShell SecretManagement:
# $env:GEMINI_API_KEY = Get-Secret -Name 'GeminiApiKey' -AsPlainText
```

### Windows (CMD)

```cmd
set AI_PROVIDER=gemini
set GEMINI_API_KEY=%GEMINI_API_KEY%
rem Reference from another secure source or set interactively
```

## Next Steps

- [AI Providers](./ai-providers.md) - Models and pricing
- [Commands Reference](./commands/README.md) - Available commands
