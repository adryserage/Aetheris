# Analysis Agents

Aetheris uses **6 specialized AI agents** that work together to analyze your code.

## Agent Overview

| Agent | Abbreviation | Purpose |
|-------|--------------|---------|
| Code Analysis Expert | CAE | Individual file analysis |
| Architect Analysis Agent | AAA | Architecture overview |
| Security Analysis Agent | SSA | Vulnerability detection |
| Code Metrics Agent | CMA | Code metrics and complexity |
| Dependency Vulnerability Agent | DVA | CVE scanning |
| Quality Assurance Agent | QAA | Final synthesis |

## Code Analysis Expert (CAE)

Analyzes each file individually to identify:

- **Objectives**: Main purpose and functions
- **Strengths**: Good practices and patterns
- **Dependencies**: Relationships between files
- **Risks**: Technical debt and issues
- **Suggestions**: Improvement recommendations

## Architect Analysis Agent (AAA)

Produces architecture-level analysis:

- **Overview**: Global system structure
- **Patterns**: Architectural patterns identified
- **Cohesion**: Inter-module consistency
- **Dependencies**: Coupling and dependencies
- **Refactoring**: Optimization plan

## Security Analysis Agent (SSA)

Detects security vulnerabilities:

- **Injections**: SQL, XSS, command injection
- **Secrets**: Hardcoded credentials and keys
- **Cryptography**: Weak crypto implementations
- **Authentication**: Auth/authz issues
- **CWE/OWASP**: Standard classifications

## Code Metrics Agent (CMA)

Calculates code metrics:

- **Complexity**: Cyclomatic complexity
- **Duplication**: Code clone detection
- **Nesting**: Depth of nested blocks
- **Maintainability**: Maintainability index
- **Size**: Lines of code, functions count

## Dependency Vulnerability Agent (DVA)

Analyzes dependency vulnerabilities via OSV API:

- **npm**: package.json, package-lock.json
- **PyPI**: requirements.txt, Pipfile
- **Pub**: pubspec.yaml (Dart/Flutter)

Identifies:
- CVE identifiers
- Severity levels
- Fixed versions available

## Quality Assurance Agent (QAA)

Synthesizes all analyses:

- **Quality Score**: Global score (0-100)
- **Dimensions**: Security, Maintainability, Architecture
- **Action Plan**: Prioritized improvements
- **Roadmap**: Improvement timeline

## Agent Configuration

Agents inherit from `BaseAgent` class and use:

```python
await self._call_ai_with_retry(prompt)      # Standard call
await self._call_ai_with_reasoning(prompt)  # With reasoning display
await self._call_ai_structured(prompt, Schema)  # Structured output
```

## Adding Custom Agents

1. Create `src/agents/my_agent.py`
2. Inherit from `BaseAgent`
3. Implement analysis logic
4. Register in `CodeAnalyzer`
5. Add workflow step in `AnalysisOrchestrator`

See [PLUGINS.md](./PLUGINS.md) for extensibility details.
