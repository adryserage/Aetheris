# Aetheris Developer Documentation

> **Internal documentation for contributors and developers.**
>
> For public documentation, see [https://adryserage.github.io/aetheris/](https://adryserage.github.io/aetheris/)

## Quick Links

- [Architecture](./architecture.md) - System design and components
- [Agent Development](./agents.md) - Creating custom agents
- [API Reference](./api-reference.md) - Internal APIs and models
- [Contributing](./contributing.md) - Development workflow

## Development Setup

```bash
# Clone repository
git clone https://github.com/adryserage/aetheris.git
cd aetheris

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Format code
black src/ main.py --line-length 100

# Type check
mypy src/
```

## Project Structure

```
aetheris/
├── src/
│   ├── agents/           # AI analysis agents
│   │   ├── base_agent.py       # Base class for all agents
│   │   ├── code_expert.py      # File analysis agent
│   │   ├── security_agent.py   # Security analysis
│   │   ├── architect_agent.py  # Architecture analysis
│   │   ├── metrics_agent.py    # Code metrics
│   │   ├── vulnerability_agent.py  # CVE scanning
│   │   └── qa_agent.py         # QA synthesis
│   ├── core/             # Core infrastructure
│   │   ├── analyzer.py         # Main CodeAnalyzer class
│   │   ├── orchestrator.py     # Workflow orchestration
│   │   ├── ai_providers.py     # AI provider abstraction
│   │   ├── config.py           # Configuration management
│   │   ├── cache.py            # Caching layer
│   │   ├── progress.py         # Terminal progress UI
│   │   └── circuit_breaker.py  # Error resilience
│   ├── models/           # Data models (Pydantic)
│   ├── services/         # Business logic services
│   └── cli.py            # CLI entry point
├── tests/                # Test suite
├── docs/                 # Public documentation (GitHub Pages)
├── docs-dev/             # Developer documentation (internal)
├── config/               # Configuration files
└── main.py               # Application entry point
```

## Code Standards

- **Python 3.9+** required
- **Black** for formatting (line length: 100)
- **Type hints** throughout
- **Async/await** for all I/O operations
- **Pydantic** for data validation

## Git Workflow

```
main        ← Production releases (protected)
  ↑
develop     ← Integration branch (auto-promotes to main)
  ↑
feature/*   ← Feature development
```

## Release Process

1. All changes merged to `develop`
2. CI quality gates run automatically
3. On pass: auto-promote to `main`
4. Tag release: `git tag v2.6.1`
5. Push tag: `git push origin v2.6.1`
6. PyPI publish workflow triggers automatically
