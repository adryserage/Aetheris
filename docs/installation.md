# Installation Guide

## Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package manager (included with Python)

### Optional Prerequisites

| Tool | Required For | Installation |
|------|--------------|--------------|
| GitHub CLI (`gh`) | `aetheris pr`, `aetheris issues`, `aetheris pr-gen` | [cli.github.com](https://cli.github.com/) |
| Claude Code | `aetheris fix` | `npm install -g @anthropic-ai/claude-code` |

## Installation from PyPI (Recommended)

```bash
pip install adryserage-aetheris
```

Verify installation:

```bash
aetheris --version
```

## Installation from Source

```bash
git clone https://github.com/adryserage/aetheris.git
cd aetheris
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `google-genai` | Gemini AI SDK with Structured Outputs, Thinking, Code Execution |
| `openai` | OpenAI API for code analysis |
| `anthropic` | Claude (Anthropic) API for code analysis |
| `pydantic` | JSON schema validation for Structured Outputs |
| `pathspec` | .gitignore pattern handling |
| `requests` | HTTP requests for OSV API |
| `pyyaml` | YAML parsing (pubspec.yaml for Dart/Flutter) |
| `ddgs` | Web search for documentation lookup |
| `rich` | Terminal UI with progress bars |

## API Keys

You need at least one AI provider API key:

| Provider | Environment Variable | Get Key |
|----------|---------------------|---------|
| Gemini | `GEMINI_API_KEY` | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| OpenAI | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) |
| Claude | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) |

Create a `.env` file in your project root:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

## Verify Installation

```bash
# Check version
aetheris --version

# View help
aetheris --help

# Test analysis (dry run)
aetheris analysis --help
```

## Next Steps

- [Configuration Guide](./configuration.md) - Customize behavior
- [Commands Reference](./commands/README.md) - Available commands
- [AI Providers](./ai-providers.md) - Provider setup and models
