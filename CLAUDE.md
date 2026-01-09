# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aetheris is a multi-agent code analysis system that uses AI (Gemini, OpenAI, or Claude) to analyze codebases for quality, security, architecture, and technical debt. It coordinates 6 specialized agents to produce comprehensive analysis reports.

## SpecKit Workflow Quick Reference

**MANDATORY**: Every code change follows this workflow. No exceptions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SPECKIT WORKFLOW                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /speckit.specify ──► /speckit.clarify ──► /speckit.plan ──► /speckit.tasks │
│        │                    │                   │                  │         │
│        ▼                    ▼                   ▼                  ▼         │
│   spec.md            Resolve Q&A         plan.md +           tasks.md       │
│   (WHAT)             (max 5 Q's)         research.md         (HOW)          │
│                                          data-model.md                       │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  /speckit.analyze ──► IMPLEMENT ──► /speckit.checklist ──► COMMIT           │
│        │                  │                  │                  │            │
│        ▼                  ▼                  ▼                  ▼            │
│   Validate           Write code        Verify tasks      Conventional       │
│   consistency        per tasks.md      completed         commit format      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Command Reference

| Command | Purpose | Output |
|---------|---------|--------|
| `/speckit.specify <description>` | Define feature requirements | `specs/NNN-feature/spec.md` |
| `/speckit.clarify` | Resolve ambiguities (max 5 questions) | Updates `spec.md` |
| `/speckit.plan` | Technical design & research | `plan.md`, `research.md`, `data-model.md` |
| `/speckit.tasks` | Generate implementation tasks | `tasks.md` with checkboxes |
| `/speckit.analyze` | Validate cross-artifact consistency | Analysis report |
| `/speckit.checklist` | Generate verification checklist | `checklists/requirements.md` |

### Spec Folder Structure

```
specs/NNN-feature-name/
├── spec.md           # WHAT: Requirements, user stories, acceptance criteria
├── plan.md           # HOW: Architecture, tech stack, integration points
├── tasks.md          # TASKS: Ordered implementation checklist
├── research.md       # DECISIONS: Research findings, alternatives rejected
├── data-model.md     # DATA: Entities, relationships, schemas
├── quickstart.md     # USAGE: CLI examples, API usage
└── checklists/
    └── requirements.md  # VERIFY: Quality gates
```

## SpecKit Cross-Spec Synchronization

**IMPORTANT**: When modifying a spec that introduces cross-cutting changes (new systems, shared infrastructure, or features that affect later specs), you MUST review and update all dependent specs.

### Dependency Chain (Current)

```
═══════════════════════════════════════════════════════════════════════════════
                              IMPLEMENTED (v2.6.1)
═══════════════════════════════════════════════════════════════════════════════
v2.5   001-github-issues-cli ✅
v2.6.1 001-cython-binary-dist ✅ ─────┐ PyPI wheel builds
v2.6.1 002-flexible-timeout ✅ ───────┤ Timeout management + heartbeat
v2.6.1 014-reanalyze-flag ✅ ─────────┤ Incremental analysis (--reanalyze)
v2.6.1 013-readme-restructure ✅ ─────┘ Public docs + GitHub Pages

═══════════════════════════════════════════════════════════════════════════════
                              PLANNED (Next)
═══════════════════════════════════════════════════════════════════════════════
v2.6.2 012-artifact-cleanup           Nettoyage des Artefacts & Sécurisation des Paquets
v2.6.5 003-advanced-stats             Statistics command (aetheris stats)
v2.7   004-i18n-multilingual          Internationalization support
v2.8   015-gemini-cli-skills          CLI Wrapper + Skills + MCP Integration
v2.9   005-cicd-template              GitHub Actions templates

═══════════════════════════════════════════════════════════════════════════════
                              v3.0 CONFIG SYSTEM
═══════════════════════════════════════════════════════════════════════════════
v3.0   006-persistent-config ─────────┐ Core: config.json system
                                      │
v3.0.1 007-docs-update ◄──────────────┤ Uses config.json
v3.0.1 008-extended-agents ◄──────────┤ Uses config.json (4 new agents)
v3.0.2 009-agent-selection ◄──────────┤ Uses config.json (--agents flag)
v3.0.3 010-safety-profiles ◄──────────┤ Uses config.json (safety settings)
v3.0.4 011-readme-safety-docs ◄───────┘ References config.json
```

### When to Sync Specs

Review downstream specs when:
1. **Adding a new system** (e.g., config.json) - Update all specs that should use it
2. **Modifying data models** - Ensure schema changes propagate
3. **Adding CLI flags** - Check if other specs should reference them
4. **Changing architecture** - Verify dependent specs align

### How to Sync

1. Identify the spec introducing the change (e.g., 006-persistent-config)
2. List all specs with higher version numbers
3. For each downstream spec:
   - Update `plan.md`: Add "Depends On" and integration section
   - Update `tasks.md`: Add tasks for integration (ConfigSchema, Settings UI, etc.)
   - Update task counts in Summary section
4. Commit all updates together with descriptive message

### Example: Config.json Integration

When 006-persistent-config introduced `config.json`, all post-v3.0 specs needed:
- `Depends On: v3.0 (Persistent Config)` in plan.md
- Configuration Integration section showing JSON schema
- Tasks for adding to ConfigSchema
- Tasks for Settings UI tab (if applicable)

## Configuration Hierarchy (v3.0+)

**Priority Order** (highest to lowest):

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLI FLAGS            --timeout 300, --profile safe       │
│    ↓ overrides                                              │
│ 2. LOCAL config.json    ./config.json (project-specific)    │
│    ↓ overrides                                              │
│ 3. GLOBAL config.json   ~/.aetheris/config.json (user-wide) │
│    ↓ overrides                                              │
│ 4. ENVIRONMENT          .env file (secrets only)            │
│    ↓ overrides                                              │
│ 5. DEFAULTS             Built-in defaults                   │
└─────────────────────────────────────────────────────────────┘
```

### Config.json Structure

> **Note**: Model names (e.g., `gemini-1.5-pro`) are examples and may change. Always consult the provider's documentation for current model identifiers. Use `"model": "default"` to let Aetheris select the recommended model for each provider.

```json
{
  "ai": {
    "provider": "gemini",
    "model": "default",
    "timeout": 120,
    "max_retries": 3
  },
  "analysis": {
    "default_preset": "quick-scan",
    "enabled_agents": ["all"],
    "skip_agents": [],
    "exclude_patterns": ["**/node_modules/**", "**/.git/**"]
  },
  "safety": {
    "default_profile": "safe",
    "custom_allowlist": [],
    "audit_log_path": "aetheris-audit.jsonl"
  },
  "presets": {
    "custom-preset": {
      "description": "My custom preset",
      "agents": ["security", "performance"]
    }
  },
  "output": {
    "format": "markdown",
    "directory": "docs/analyses"
  }
}
```

### Key Files

| File | Purpose | Secrets? |
|------|---------|----------|
| `config.json` | Preferences, presets, settings | ❌ Never |
| `.env` | API keys, tokens | ✅ Always |
| `~/.aetheris/config.json` | Global user preferences | ❌ Never |
| `config/presets.json` | Built-in presets | ❌ Never |
| `config/default_allowlist.json` | Safe mode command allowlist | ❌ Never |

### Settings UI Tabs (v3.0+)

| Tab | Config Section | Features |
|-----|----------------|----------|
| AI Provider | `ai.*` | Provider, model, timeout, retries |
| Analysis | `analysis.*` | Default preset, agents, exclusions |
| Presets | `presets.*` | Custom preset creation |
| Safety | `safety.*` | Default profile, allowlist, audit path |
| Output | `output.*` | Format, directory |

## Commands

### Running the CLI
```bash
# Main command (after pip install)
aetheris analysis

# Development mode (from source)
python main.py
python -m src.cli analysis

# Analyze specific files
aetheris analysis --changed-files-only --files src/file1.py,src/file2.py

# With JSON file list (from CI)
aetheris analysis --changed-files-only --files '["src/file1.py", "src/file2.py"]'

# v2.6.1: Timeout management
aetheris analysis --timeout 30m           # 30 minute timeout
aetheris analysis --timeout 2h            # 2 hour timeout
aetheris analysis --timeout 0             # Unlimited (no timeout)

# v2.6.1: Incremental reanalysis
aetheris analysis --reanalyze             # Only changed files since last analysis
aetheris analysis -r                      # Short form
aetheris analysis -r --timeout 30m        # Combined with timeout
```

### v2.6.1 Feature Reference

| Feature | Flag | Description |
|---------|------|-------------|
| **Timeout** | `--timeout <duration>` | Set max analysis time (e.g., `30m`, `2h`, `0` for unlimited) |
| **Heartbeat** | (automatic) | Progress indicator every 10 min for long analyses |
| **Reanalyze** | `--reanalyze` / `-r` | Detect and analyze only changed files |

**Change Detection Methods:**
- **Git-based**: Uses `git diff` when commit SHA from last analysis is available
- **Timestamp-based**: Falls back to file modification times when git unavailable

**Last Analysis Info**: Read from `docs/metrics/metrics_*.json` (most recent file)

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Format code
black src/ main.py --line-length 100
```

### Environment Configuration
Create `.env` file:
```env
AI_PROVIDER=gemini  # or openai, claude
GEMINI_API_KEY=...  # or OPENAI_API_KEY, ANTHROPIC_API_KEY
AI_MODEL=default    # optional, uses provider's recommended model (or specify exact model ID)
```

> **Note**: Model identifiers change over time. Use `default` to automatically use each provider's recommended model, or check the provider's API documentation for current model names.

## Architecture

> **Maintenance Note**: File paths in this section are subject to change during refactoring. Always use search tools (`Glob`, `Grep`) to locate actual files by class/function name rather than relying on hardcoded paths.

### Core Flow
```
CLI → CodeAnalyzer → AnalysisOrchestrator → WorkflowStages → Specialized Agents
```

**To locate key entry points:**
```bash
# Find CLI entry point
grep -r "def analysis\|Typer\|app = " src/*.py

# Find main analyzer class
grep -r "class CodeAnalyzer" src/

# Find orchestrator
grep -r "class AnalysisOrchestrator" src/
```

### Key Components by Role

**Core Module (`src/core/`)** - Orchestration and infrastructure

| Role | Class/Pattern to Search |
|------|-------------------------|
| Analysis coordination | `class CodeAnalyzer` |
| Workflow management | `class AnalysisOrchestrator`, `WorkflowStage` |
| AI provider abstraction | `class AIProvider` (base), provider implementations |
| Configuration | `class AnalysisConfig`, `@dataclass` in config |
| Caching | `class.*Cache`, `def get_cache` |
| Parallel analysis | `parallel`, `concurrent`, `asyncio.gather` |
| Priority management | `class.*Priority`, `PriorityLevel` |
| Error handling | `class CircuitBreaker`, `exponential_backoff` |

**Agents Module (`src/agents/`)** - All inherit from `BaseAgent`

| Role | Class Pattern to Search |
|------|-------------------------|
| Base agent | `class BaseAgent` |
| File analysis | `class.*Expert`, `CodeAnalysis` |
| Architecture analysis | `class.*Architect` |
| Security analysis | `class.*Security` |
| Metrics collection | `class.*Metrics` |
| Dependency vulnerabilities | `class.*Vulnerability`, `OSV` |
| Quality assurance | `class.*Quality` |

**Services Module (`src/services/`)** - Business logic

| Role | Class Pattern to Search |
|------|-------------------------|
| Dependency analysis | `class.*Dependency` |
| Documentation search | `class.*Documentation`, `class.*Searcher` |
| Code generation | `class.*Generator` |

**Models Module (`src/models/`)** - Data structures

| Role | Pattern to Search |
|------|-------------------|
| Core dataclasses | `class FileAnalysis`, `class SecurityIssue`, `class DependencyInfo` |
| Analysis schemas | `@dataclass`, `BaseModel` |

### Adding a New Agent

1. Create a new agent file in the agents module, inheriting from `BaseAgent`
2. Implement analysis logic using `await self._call_ai_with_retry(prompt)` or `await self._call_ai_with_reasoning(prompt)`
3. Register the agent in `CodeAnalyzer` and add a workflow step in `AnalysisOrchestrator`

> **Tip**: Use `grep -r "class BaseAgent" src/` to find the base class location for reference.

### Agent Development Guidelines

#### Agent Structure Template

> **Note**: Import paths below are illustrative. Verify actual module paths with `grep -r "class BaseAgent" src/`.

```python
from src.agents.base_agent import BaseAgent  # Verify actual path
from src.models.data_models import AnalysisResult  # Verify actual path

class MyAnalysisAgent(BaseAgent):
    """Brief description of what this agent analyzes."""

    def __init__(self, ai_provider, config):
        super().__init__(ai_provider, config)
        self.agent_name = "my_analysis"  # Used for caching, logging

    async def analyze(self, context: dict) -> AnalysisResult:
        """Main entry point for analysis."""
        prompt = self._build_prompt(context)

        # Use retry wrapper for resilience
        response = await self._call_ai_with_retry(prompt)

        # Parse and validate response
        return self._parse_response(response)

    def _build_prompt(self, context: dict) -> str:
        """Construct the AI prompt with context."""
        return f"""
        Analyze the following code for [specific concern]:

        {context['code']}

        Respond in JSON format:
        {{
            "issues": [...],
            "recommendations": [...]
        }}
        """

    def _parse_response(self, response: str) -> AnalysisResult:
        """Parse AI response into structured data."""
        # Always validate and handle malformed responses
        try:
            data = json.loads(response)
            return AnalysisResult(**data)
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Failed to parse response: {e}")
            return AnalysisResult(issues=[], recommendations=[])
```

#### Prompt Engineering Best Practices

| Practice | Example |
|----------|---------|
| **Be specific** | "Identify SQL injection vulnerabilities" not "find security issues" |
| **Request structured output** | Always ask for JSON with defined schema |
| **Provide context** | Include file path, language, project type |
| **Set constraints** | "List maximum 10 issues, prioritized by severity" |
| **Include examples** | Show expected output format in prompt |

#### Agent Registration Checklist

- [ ] Add agent class to agents module `__init__.py` (find with `grep -l "__all__" src/agents/`)
- [ ] Register in `CodeAnalyzer.__init__()` (find with `grep -r "class CodeAnalyzer" src/`)
- [ ] Add `WorkflowStage` enum value (find with `grep -r "class WorkflowStage" src/`)
- [ ] Add workflow step in `AnalysisOrchestrator`
- [ ] Add agent to presets configuration (find with `find . -name "presets.json"`)
- [ ] Add to `--agents` CLI help text
- [ ] Add to Settings UI agent list
- [ ] Create unit tests in tests directory
- [ ] Update docs with agent description

#### Response Handling

```python
# Always handle AI response failures gracefully
async def analyze(self, context):
    try:
        response = await self._call_ai_with_retry(prompt)
        return self._parse_response(response)
    except AIProviderError as e:
        self.logger.error(f"AI call failed: {e}")
        return self._empty_result()  # Never crash, return empty
    except Exception as e:
        self.logger.exception(f"Unexpected error: {e}")
        raise  # Re-raise unexpected errors for debugging
```

### Extending via Hooks

Register hooks on `WorkflowStage` enum values:
```python
orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, my_hook_function)
```
See `docs/PLUGINS.md` for full hook documentation.

## Code Patterns

- **Async throughout**: All agent calls and AI interactions are async
- **Progress reporting**: Use `ProgressManager` for terminal progress bars (Rich library)
- **Error resilience**: `exponential_backoff()` and `CircuitBreaker` for API calls (find with `grep -r "CircuitBreaker\|exponential_backoff" src/`)
- **Markdown sanitization**: `sanitize_markdown()` function for XSS prevention in reports (find with `grep -r "def sanitize_markdown" src/`)

## Zero Issues Left Behind Policy

**CRITICAL**: Never leave issues unresolved. Every identified problem must be addressed before moving on.

### Enforcement Rules

| Rule | Action |
|------|--------|
| **Spec Analysis Issues** | Run `/speckit.analyze` → Fix ALL findings before implementation |
| **Edge Cases** | Every edge case in `spec.md` MUST have a corresponding task in `tasks.md` |
| **Task Coverage** | Every requirement MUST map to at least one task |
| **Cross-Spec Sync** | When adding systems, update ALL dependent specs immediately |
| **Validation Errors** | Fix lint/typecheck errors before committing |

### During Spec Creation

```
After /speckit.tasks, ALWAYS:
1. Compare spec.md Edge Cases section with tasks.md
2. For each edge case without a task → Add task to tasks.md
3. Update Summary table with new task count
4. Run /speckit.analyze to verify coverage
```

### During Implementation

```
After completing a task, ALWAYS:
1. Mark task as completed in tasks.md (if tracking)
2. Check for related edge cases that need handling
3. Run tests to verify no regressions
4. If new issues found → Add new tasks, don't ignore
```

### Issue Categories

| Category | Detection | Resolution |
|----------|-----------|------------|
| **Missing Edge Case Tasks** | Compare spec.md with tasks.md | Add tasks to Polish phase |
| **Coverage Gaps** | `/speckit.analyze` report | Add tasks for uncovered requirements |
| **Cross-Spec Inconsistency** | Manual review or analyze | Update dependent specs |
| **Ambiguity** | `/speckit.clarify` | Resolve with user, update spec |
| **Duplicate Requirements** | `/speckit.analyze` | Consolidate, remove redundancy |

### Examples of Issues NOT to Leave Behind

```markdown
❌ BAD: "Edge case: Handle timeout → No task created"
✅ GOOD: "Edge case: Handle timeout → T023 in tasks.md"

❌ BAD: "New config.json system → Only update current spec"
✅ GOOD: "New config.json system → Update ALL post-v3.0 specs"

❌ BAD: "Lint warning → Commit anyway"
✅ GOOD: "Lint warning → Fix before commit"

❌ BAD: "Test failure → Will fix later"
✅ GOOD: "Test failure → Fix now or add task"
```

## Common Pitfalls

### SpecKit Workflow Pitfalls

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Skipping `/speckit.clarify` | Ambiguous requirements | Always run, even if "obvious" |
| Not running `/speckit.analyze` | Coverage gaps missed | Run before implementation |
| Ignoring edge cases | Bugs in production | Map every edge case to a task |
| Hardcoding in tasks.md | Stale file paths | Use relative paths, verify existence |

### Cross-Spec Pitfalls

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Adding system without sync | Inconsistent specs | Check dependency chain |
| Missing "Depends On" | Build order issues | Always add to plan.md |
| Not updating task counts | Misleading metrics | Update Summary after adding tasks |
| Forgetting Settings UI | Incomplete config integration | Add tab task for each config section |

### Code Implementation Pitfalls

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Sync AI calls | UI freezes | Always use `async/await` |
| Catching all exceptions silently | Hidden failures | Log errors, re-raise unexpected |
| Hardcoding API keys | Security breach | Use `.env` only |
| Ignoring rate limits | Service bans | Use `CircuitBreaker` class |
| Not caching | Excessive API costs | Use cache module with Git SHA |

### Config Pitfalls (v3.0+)

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Secrets in config.json | Exposed credentials | Secrets in `.env` ONLY |
| Missing ConfigSchema field | Config ignored | Add to config schema (find with `grep -r "ConfigSchema\|config.*schema" src/`) |
| Wrong hierarchy lookup | Wrong values used | Test CLI > local > global > default |
| Not handling missing config | Crashes | Use defaults, warn on missing |

### Testing Pitfalls

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Not mocking AI calls | Slow, flaky tests | Use `pytest-mock` for AI responses |
| Testing implementation | Brittle tests | Test behavior, not internals |
| Ignoring async | Incomplete coverage | Use `pytest-asyncio` |

## Output

Reports are generated in `docs/analyses/`:
- Individual file reports: `docs/analyses/<filename>.md`
- Architecture overview: `docs/architecture_overview.md`
- Quality assurance report: `docs/analyses/quality_assurance_report.md`
- Vulnerability report: `docs/analyses/vulnerabilities_report.md`
- Performance metrics: `docs/metrics/metrics_<timestamp>.json`

## Tech Stack

| Category | Technologies |
|----------|--------------|
| **Language** | Python 3.9+ |
| **CLI Framework** | Typer |
| **Terminal UI** | Rich (progress bars, tables, panels) |
| **Data Validation** | Pydantic, dataclasses |
| **AI Providers** | Gemini, OpenAI, Claude (Anthropic) |
| **File Parsing** | pathlib, re |
| **External APIs** | GitHub CLI (gh), OSV (vulnerabilities) |
| **Storage** | Local filesystem (JSON, Markdown) |
