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

**Runtime Environment**: DVA parses manifest files (package.json, requirements.txt, pubspec.yaml) and lockfiles directly without requiring package managers (npm, pip, flutter) to be installed. Dependency resolution is performed by reading the lockfile contents and querying the OSV API. If no lockfile is present, only direct dependencies from the manifest are analyzed.

## Quality Assurance Agent (QAA)

Synthesizes all analyses:

- **Quality Score**: Global score (0-100)
- **Dimensions**: Security, Maintainability, Architecture
- **Action Plan**: Prioritized improvements
- **Roadmap**: Improvement timeline

## Data Security

Before sending code to external AI providers, Aetheris applies **automatic sensitive data filtering** to protect secrets and intellectual property.

### Pre-processing (Scrubbing)

The following data types are automatically masked before AI analysis:

| Data Type | Pattern Examples | Replacement |
|-----------|------------------|-------------|
| API Keys | `AKIA...`, `sk-...`, `ghp_...` | `[REDACTED_API_KEY]` |
| Passwords | `password=`, `pwd=`, `secret=` | `[REDACTED_SECRET]` |
| Connection Strings | `mongodb://`, `postgres://` | `[REDACTED_CONNECTION_STRING]` |
| Private Keys | `-----BEGIN RSA PRIVATE KEY-----` | `[REDACTED_PRIVATE_KEY]` |
| JWT Tokens | `eyJ...` (base64 JWT format) | `[REDACTED_TOKEN]` |
| AWS Credentials | `aws_access_key_id`, `aws_secret_access_key` | `[REDACTED_AWS_CREDENTIAL]` |
| PII Patterns | Email addresses, phone numbers | `[REDACTED_PII]` |

### Configuration

Control sensitive data filtering via `config.json`:

```json
{
  "security": {
    "scrub_secrets": true,
    "custom_patterns": [
      {
        "name": "internal_token",
        "pattern": "MYCOMPANY_[A-Z0-9]{32}",
        "replacement": "[REDACTED_INTERNAL_TOKEN]"
      }
    ],
    "exclude_files": ["**/*.env", "**/secrets/**"]
  }
}
```

### Best Practices

1. **Never commit secrets** - Use `.env` files excluded from analysis
2. **Review before analysis** - Check what files will be sent to AI
3. **Use `--dry-run`** - Preview analysis scope without sending data
4. **Custom patterns** - Add company-specific secret formats to config
5. **Audit logging** - Enable `audit_log_path` to track all AI interactions

### File Exclusions

By default, these files are excluded from AI analysis:

- `.env`, `.env.*` - Environment files
- `**/secrets/**` - Secret directories
- `**/*.pem`, `**/*.key` - Certificate files
- `**/credentials*` - Credential files

## Agent Configuration

Agents inherit from `BaseAgent` class and use:

```python
await self._call_ai_with_retry(prompt)      # Standard call
await self._call_ai_with_reasoning(prompt)  # With reasoning display
await self._call_ai_structured(prompt, Schema)  # Structured output (see below)
```

### Structured Output with Pydantic Schemas

The `_call_ai_structured` method requires a Pydantic model to validate and parse AI responses:

```python
from pydantic import BaseModel, Field
from typing import List

# Define your response schema
class SecurityIssue(BaseModel):
    severity: str = Field(description="Issue severity: critical, high, medium, low")
    description: str = Field(description="Detailed description of the issue")
    cwe_id: str | None = Field(default=None, description="CWE identifier if applicable")

class SecurityAnalysisResult(BaseModel):
    issues: List[SecurityIssue] = Field(default_factory=list)
    risk_score: int = Field(ge=0, le=100, description="Overall risk score 0-100")

# Use in agent
result = await self._call_ai_structured(prompt, SecurityAnalysisResult)
# result is now a validated SecurityAnalysisResult instance
```

**Key points:**
- Schemas must inherit from `pydantic.BaseModel`
- Use `Field()` with descriptions to guide AI response formatting
- The method returns a validated instance of your schema
- Invalid responses raise `ValidationError` (handled by retry logic)

## Adding Custom Agents

1. Create `src/agents/my_agent.py`
2. Inherit from `BaseAgent`
3. Implement analysis logic
4. Register in `CodeAnalyzer`
5. Add workflow step in `AnalysisOrchestrator`

See [PLUGINS.md](./PLUGINS.md) for extensibility details.
