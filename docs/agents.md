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

## How Agents Work

### Analysis Process

Each agent performs a multi-step analysis:

1. **Initial Scan** - Quick identification of potential issues
2. **Deep Analysis** - Detailed examination of flagged areas
3. **Cross-Reference** - Correlation with other agent findings
4. **Synthesis** - Final prioritized recommendations

### Output Quality

All agents produce structured findings with:

| Element | Description |
|---------|-------------|
| **Severity** | Critical, High, Medium, Low |
| **Location** | File path and line numbers |
| **Description** | Clear explanation of the issue |
| **Recommendation** | Actionable fix suggestion |
| **References** | CWE, OWASP, or best practice links |

## Extending Aetheris

Aetheris supports custom agents through its plugin system. See the [Plugin Guide](./PLUGINS.md) for details on:

- Creating custom analysis agents
- Registering hooks into the workflow
- Building specialized analysis pipelines

## Related Documentation

- [Features](./features.md) - Full feature reference
- [Configuration](./configuration.md) - Customizing agent behavior
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions
