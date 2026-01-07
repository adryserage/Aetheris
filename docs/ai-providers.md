# AI Providers

Aetheris supports three AI providers: Google Gemini, OpenAI, and Anthropic Claude.

## Configuration

Set the provider in `.env`:
```env
AI_PROVIDER=gemini  # or openai, claude
```

### API Keys

| Provider | Variable | Get Key |
|----------|----------|---------|
| Gemini | `GEMINI_API_KEY` | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| OpenAI | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) |
| Claude | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) |

## Available Models

### Gemini
| Model | Notes |
|-------|-------|
| `gemini-3-pro-preview` | Latest, thinking mode |
| `gemini-2.5-pro` | Recommended |
| `gemini-2.0-flash-exp` | Fast |
| `gemini-1.5-pro` | Stable |
| `gemini-1.5-flash` | Budget-friendly |

### OpenAI
| Model | Notes |
|-------|-------|
| `gpt-4o` | Recommended |
| `gpt-4-turbo` | Fast |
| `o1-preview` | Reasoning model |
| `o1-mini` | Reasoning, faster |
| `gpt-3.5-turbo` | Budget-friendly |

### Claude
| Model | Notes |
|-------|-------|
| `claude-3-5-sonnet-20241022` | Recommended |
| `claude-3-opus-20240229` | Best quality |
| `claude-3-haiku-20240307` | Fast, cheap |

## Gemini Advanced Features

Available with Gemini models:

| Feature | Variable | Description |
|---------|----------|-------------|
| Structured Outputs | `ENABLE_STRUCTURED_OUTPUTS=true` | JSON validated via Pydantic |
| Thinking Mode | `ENABLE_THINKING=true` | Show reasoning process |
| Code Execution | `ENABLE_CODE_EXECUTION=true` | Python sandbox |
| Context Caching | `ENABLE_CONTEXT_CACHING=true` | 50% cost reduction |
| Batch API | `ENABLE_BATCH_MODE=true` | 50% cost reduction |

## Pricing Comparison (per 1M tokens)

| Provider | Model | Input | Output |
|----------|-------|-------|--------|
| Gemini | 2.5 Pro | $3.50 | $10.50 |
| Gemini | 1.5 Flash | $0.35 | $1.05 |
| OpenAI | GPT-4o | $2.50 | $10.00 |
| OpenAI | GPT-3.5 | $0.50 | $1.50 |
| Claude | 3.5 Sonnet | $3.00 | $15.00 |
| Claude | 3 Haiku | $0.25 | $1.25 |

## Cost Estimation

| Project Size | Files | Gemini Pro | GPT-4o | Claude Sonnet |
|--------------|-------|------------|--------|---------------|
| Small | 10 | $0.10 | $0.25 | $0.27 |
| Medium | 50 | $0.52 | $1.25 | $1.35 |
| Large | 100 | $1.03 | $2.50 | $2.70 |

## Recommendations

| Use Case | Recommended |
|----------|-------------|
| Budget-friendly | Gemini 1.5 Flash, GPT-3.5 |
| Best value | Gemini 2.5 Pro, GPT-4o |
| Highest quality | Claude Opus, GPT-4 |
| Code analysis | GPT-4o, Claude Sonnet |

## Reasoning Display

For models with reasoning (OpenAI o1-*):
```env
SHOW_REASONING=true
AI_MODEL=o1-preview
```

For Gemini thinking mode:
```env
ENABLE_THINKING=true
THINKING_BUDGET=2048
```
