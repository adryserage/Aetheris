# AI Providers

Aetheris supports three AI providers: Google Gemini, OpenAI, and Anthropic Claude.

## Configuration

Set the provider in `.env`:
```env
AI_PROVIDER=gemini  # or openai, claude
```

> ⚠️ **Security Warning**: Never commit your `.env` file to version control. Ensure `.env` is listed in your `.gitignore` to prevent accidental credential leakage.

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
| `gemini-2.5-pro` | Recommended, thinking mode (default) |
| `gemini-2.5-flash` | Fast, cost-effective |
| `gemini-2.5-flash-lite` | Ultra-fast, lowest cost |
| `gemini-2.0-flash` | Budget-friendly |
| `gemini-2.0-flash-lite` | Simple high-frequency tasks |

> **Note**: Gemini 1.5 and 1.0 models have been retired (404 error). Use `gemini-2.0-flash` for budget options or `gemini-2.5-flash` for better performance.

### OpenAI
| Model | Notes |
|-------|-------|
| `gpt-4o` | Recommended (default) |
| `gpt-4-turbo` | Fast |
| `gpt-4-turbo-preview` | Preview version |
| `gpt-4` | Stable |
| `o1-preview` | Reasoning model |
| `o1-mini` | Reasoning, faster |
| `gpt-3.5-turbo` | Budget-friendly |

### Claude
| Model | Notes |
|-------|-------|
| `claude-3-5-sonnet-20241022` | Recommended (default) |
| `claude-3-opus-20240229` | Best quality |
| `claude-3-haiku-20240307` | Fast, cheap |

## Gemini Advanced Features

Available with Gemini models. These are **configuration options** set in `AnalysisConfig` or `config.json`:

| Feature | Config Key | Default | Description |
|---------|------------|---------|-------------|
| Structured Outputs | `enable_structured_outputs` | `true` | JSON validated via Pydantic |
| Thinking Mode | `enable_thinking` | `false` | Show reasoning process |
| Thinking Budget | `thinking_budget` | `1024` | Token budget for reasoning (min 128) |
| Code Execution | `enable_code_execution` | `false` | Python sandbox execution |
| Context Caching | `enable_context_caching` | `true` | ~50% cost reduction |
| Cache TTL | `cache_ttl_seconds` | `3600` | Cache duration in seconds |
| Batch API | `enable_batch_mode` | `true` | ~50% cost reduction |
| Google Search | `enable_google_search` | `false` | Web search grounding |
| Function Calling | `enable_function_calling` | `false` | Call Python functions |

**Example `config.json`:**
```json
{
  "enable_thinking": true,
  "thinking_budget": 2048,
  "enable_context_caching": true,
  "enable_google_search": false
}
```

## Pricing

Prices change frequently. Consult official pricing pages for current rates:

| Provider | Pricing Page |
|----------|--------------|
| Gemini | [Google AI Pricing](https://ai.google.dev/pricing) |
| OpenAI | [OpenAI Pricing](https://openai.com/api/pricing/) |
| Claude | [Anthropic Pricing](https://www.anthropic.com/pricing) |

### Cost Factors

Typical analysis costs depend on:
- **Project size**: Number and length of files analyzed
- **Model choice**: Premium models cost more than budget options
- **Token usage**: Input (code) + Output (analysis) tokens

**Budget-friendly options**: Gemini Flash, GPT-3.5 Turbo, Claude Haiku
**Premium options**: Gemini Pro, GPT-4o, Claude Sonnet/Opus

## Recommendations

| Use Case | Recommended |
|----------|-------------|
| Budget-friendly | Gemini 2.0 Flash, GPT-3.5 |
| Best value | Gemini 2.5 Pro, GPT-4o |
| Highest quality | Claude 3 Opus, GPT-4o |
| Code analysis | GPT-4o, Claude 3.5 Sonnet |

## Reasoning Display

To display model reasoning when available, set the `show_reasoning` config option:

```json
{
  "show_reasoning": true
}
```

### OpenAI Reasoning (o1-* models)

OpenAI o1-preview and o1-mini models include built-in reasoning. Set:
```json
{
  "ai_model": "o1-preview",
  "show_reasoning": true
}
```

### Gemini Thinking Mode

Gemini models (2.5+) support explicit thinking mode with configurable token budget:
```json
{
  "enable_thinking": true,
  "thinking_budget": 2048
}
```

> **Note**: Minimum thinking budget is 128 tokens. Budget is automatically capped at this minimum.
