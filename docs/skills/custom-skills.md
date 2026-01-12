# Custom Skills

Define your own skills via YAML configuration files.

## Overview

Custom skills allow you to extend Aetheris with project-specific or organization-specific capabilities. They are defined in YAML files and can execute shell commands with parameter substitution.

## Quick Start

1. Create a skills directory:
   ```bash
   mkdir aetheris-skills
   ```

2. Create a skills file:
   ```yaml
   # aetheris-skills/my-skills.yaml
   skills:
     - name: run_tests
       description: Run project tests
       command: pytest {path}
       parameters:
         - name: path
           type: string
           description: Test path
           default: tests/
   ```

3. Configure Aetheris:
   ```json
   {
     "skills": {
       "custom_skills_path": "./aetheris-skills/"
     }
   }
   ```

4. Use the skill:
   ```
   aetheris[gemini]> Run the tests for src/
   ```

## Skill Definition Schema

```yaml
skills:
  - name: string              # Required: Unique skill name
    description: string       # Required: What the skill does
    command: string           # Required: Shell command template
    requires_confirmation: boolean  # Optional: Ask before executing
    parameters:               # Optional: Input parameters
      - name: string          # Required: Parameter name
        type: string          # Required: string|integer|number|boolean
        description: string   # Optional: Parameter description
        required: boolean     # Optional: Is it required? (default: false)
        default: any          # Optional: Default value
        enum: [...]          # Optional: Allowed values
```

## Parameter Substitution

Use `{param_name}` in your command template:

```yaml
skills:
  - name: git_checkout
    description: Checkout a git branch
    command: git checkout {branch}
    parameters:
      - name: branch
        type: string
        required: true
        description: Branch name to checkout
```

The AI can then invoke:
```json
{
  "skill": "git_checkout",
  "arguments": {"branch": "feature/new-feature"}
}
```

Which executes: `git checkout feature/new-feature`

## Examples

### Run Tests with Coverage

```yaml
skills:
  - name: test_with_coverage
    description: Run tests with coverage report
    command: pytest {path} --cov={module} --cov-report=html
    requires_confirmation: false
    parameters:
      - name: path
        type: string
        description: Test directory
        default: tests/
      - name: module
        type: string
        description: Module to measure coverage for
        required: true
```

### Deploy to Environment

```yaml
skills:
  - name: deploy
    description: Deploy to specified environment
    command: ./scripts/deploy.sh {environment}
    requires_confirmation: true  # Always ask first!
    parameters:
      - name: environment
        type: string
        description: Target environment
        required: true
        enum:
          - staging
          - production
```

### Database Migration

```yaml
skills:
  - name: migrate_db
    description: Run database migrations
    command: alembic upgrade {revision}
    requires_confirmation: true
    parameters:
      - name: revision
        type: string
        description: Target revision
        default: head
```

### Docker Commands

```yaml
skills:
  - name: docker_build
    description: Build Docker image
    command: docker build -t {image}:{tag} {context}
    parameters:
      - name: image
        type: string
        required: true
        description: Image name
      - name: tag
        type: string
        default: latest
        description: Image tag
      - name: context
        type: string
        default: .
        description: Build context path

  - name: docker_run
    description: Run Docker container
    command: docker run -d --name {name} {image}
    requires_confirmation: true
    parameters:
      - name: name
        type: string
        required: true
      - name: image
        type: string
        required: true
```

### Linting and Formatting

```yaml
skills:
  - name: lint
    description: Run linter on files
    command: ruff check {path} {fix_flag}
    parameters:
      - name: path
        type: string
        default: src/
      - name: fix_flag
        type: string
        default: ""
        enum:
          - ""
          - "--fix"

  - name: format
    description: Format code with black
    command: black {path}
    requires_confirmation: true
    parameters:
      - name: path
        type: string
        default: src/
```

## Loading Multiple Files

All `.yaml` and `.yml` files in the custom skills path are loaded:

```
aetheris-skills/
├── devops.yaml      # DevOps-related skills
├── testing.yaml     # Testing skills
└── database.yaml    # Database management skills
```

## Security Considerations

### Use `requires_confirmation` for Dangerous Operations

```yaml
skills:
  - name: cleanup_temp
    description: Remove temporary files
    command: rm -rf {path}
    requires_confirmation: true  # ALWAYS for destructive commands!
    parameters:
      - name: path
        type: string
        required: true
```

### Validate Input with Enums

```yaml
parameters:
  - name: environment
    type: string
    enum:
      - dev
      - staging
      - prod  # Limits what the AI can pass
```

### Avoid Shell Injection

Don't use skills for commands where user input could be dangerous. The parameter substitution is simple string replacement without escaping.

**Bad:**
```yaml
command: bash -c "{user_script}"  # Dangerous!
```

**Good:**
```yaml
command: python scripts/safe_runner.py --action {action}
```

## Debugging Custom Skills

### List Loaded Skills

```
aetheris[gemini]> /help skills
Custom skills loaded:
  - run_tests (from testing.yaml)
  - deploy (from devops.yaml)
  ...
```

### Test Manually

You can test your command templates manually:

```bash
# Replace {path} manually
pytest tests/ --cov=src --cov-report=html
```

### Check YAML Syntax

```bash
python -c "import yaml; yaml.safe_load(open('my-skills.yaml'))"
```

## Error Handling

If a skill fails:

```json
{
  "status": "error",
  "error": "Command failed with exit code 1",
  "output": "pytest: error: no tests found"
}
```

The AI will see this error and can:
1. Report the failure to you
2. Suggest corrections
3. Try an alternative approach
