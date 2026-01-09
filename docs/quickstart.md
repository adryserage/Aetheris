# Quick Start Guide

Get Aetheris running in under 30 seconds.

## 1. Install

```bash
pip install adryserage-aetheris
```

## 2. Configure

Get a free API key from your preferred provider:

=== "Gemini (Recommended)"

    ```bash
    # Get free key: https://ai.google.dev
    echo "GEMINI_API_KEY=your_key_here" > .env
    echo ".env" >> .gitignore  # Never commit API keys!
    ```

=== "OpenAI"

    ```bash
    # Get key: https://platform.openai.com/api-keys
    echo "OPENAI_API_KEY=your_key_here" > .env
    echo ".env" >> .gitignore
    ```

=== "Claude"

    ```bash
    # Get key: https://console.anthropic.com
    echo "ANTHROPIC_API_KEY=your_key_here" > .env
    echo ".env" >> .gitignore
    ```

## 3. Analyze

```bash
# Navigate to your project
cd your-project

# Run analysis
aetheris analysis
```

That's it! Your analysis report will be generated in `docs/analyses/`.

## Common Workflows

### Full Analysis

```bash
aetheris analysis
```

### Incremental (Changed Files Only)

```bash
# Analyze only files changed since last analysis
aetheris analysis --reanalyze
```

### With Timeout

```bash
# For large codebases, set a timeout
aetheris analysis --timeout 30m
```

### Auto-Fix Issues

```bash
# Automatically fix issues with Claude Code
aetheris fix --analyze-first --auto

# Review changes before committing
git diff
```

### Review a PR

```bash
aetheris pr --url https://github.com/owner/repo/pull/123
```

### Create GitHub Issues

```bash
# Create issues from analysis findings
aetheris issues
```

## What's Next?

- [Full Command Reference](commands/README.md)
- [Configuration Options](configuration.md)
- [Understanding Analysis Agents](agents.md)
- [GitHub Actions Integration](github-actions.md)
