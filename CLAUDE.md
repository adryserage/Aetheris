# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aetheris is a multi-agent code analysis system that uses AI (Gemini, OpenAI, or Claude) to analyze codebases for quality, security, architecture, and technical debt. It coordinates 6 specialized agents to produce comprehensive analysis reports.

## SpecKit Cross-Spec Synchronization

**IMPORTANT**: When modifying a spec that introduces cross-cutting changes (new systems, shared infrastructure, or features that affect later specs), you MUST review and update all dependent specs.

### Dependency Chain (Current)

```
v2.5   001-github-issues-cli (implemented)
v2.6   002-flexible-timeout
v2.7   003-caching-optimization
v2.8   004-i18n-multilingual
v2.9   005-cicd-template
v3.0   006-persistent-config ──────────────────┐
v3.0.1 007-docs-update                         │
v3.0.1 008-extended-agents ◄───────────────────┤ Uses config.json
v3.0.2 009-agent-selection ◄───────────────────┤ Uses config.json
v3.0.3 010-safety-profiles ◄───────────────────┤ Uses config.json
v3.0.4 011-readme-safety-docs ◄────────────────┘ References config.json
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
```

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
AI_MODEL=gemini-1.5-pro  # optional, defaults per provider
```

## Architecture

### Core Flow
```
CLI (src/cli.py) → CodeAnalyzer (src/core/analyzer.py) → AnalysisOrchestrator (src/core/orchestrator.py)
                                                                      ↓
                                                              WorkflowStages
                                                    (SCAN → FILE_ANALYSIS → ARCHITECTURE_REPORT → ...)
                                                                      ↓
                                                              6 Specialized Agents
```

### Key Components

**`src/core/`**
- `analyzer.py` - Main `CodeAnalyzer` class that coordinates the analysis workflow
- `orchestrator.py` - `AnalysisOrchestrator` with step-based workflow, hooks, and error handling
- `ai_providers.py` - Abstraction layer for AI providers (Gemini, OpenAI, Claude via `AIProvider` base class)
- `config.py` - `AnalysisConfig` dataclass with all configuration options
- `cache.py` - Git SHA-based caching to reduce API costs
- `parallel_analyzer.py` - Dependency graph-based parallel file analysis
- `priority_manager.py` - Priority levels (HIGH/MEDIUM/LOW) for PR file ordering
- `error_handler.py` - Circuit breaker and exponential backoff

**`src/agents/`** - All agents inherit from `BaseAgent` (src/agents/base_agent.py)
- `code_analysis_expert.py` - Individual file analysis
- `architect_analysis_agent.py` - Architecture overview
- `security_analysis_agent.py` - Vulnerability detection
- `code_metrics_agent.py` - Complexity, duplication metrics
- `dependency_vulnerability_agent.py` - OSV API for dependency CVEs
- `quality_assurance_agent.py` - Final synthesis report

**`src/services/`**
- `dependency_analyzer.py` - Import/export analysis and cycle detection
- `documentation_searcher.py` - Web search for library docs
- `code_generator.py` - Code snippet generation for analysis

**`src/models/data_models.py`** - Dataclasses: `FileAnalysis`, `SecurityIssue`, `DependencyInfo`, etc.

### Adding a New Agent

1. Create `src/agents/my_agent.py` inheriting from `BaseAgent`
2. Implement analysis logic using `await self._call_ai_with_retry(prompt)` or `await self._call_ai_with_reasoning(prompt)`
3. Register the agent in `CodeAnalyzer` and add a workflow step in `AnalysisOrchestrator`

### Extending via Hooks

Register hooks on `WorkflowStage` enum values:
```python
orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, my_hook_function)
```
See `docs/PLUGINS.md` for full hook documentation.

## Code Patterns

- **Async throughout**: All agent calls and AI interactions are async
- **Progress reporting**: Use `ProgressManager` for terminal progress bars (Rich library)
- **Error resilience**: `exponential_backoff()` and `CircuitBreaker` for API calls
- **Markdown sanitization**: `sanitize_markdown()` in analyzer.py for XSS prevention in reports

## Output

Reports are generated in `docs/analyses/`:
- Individual file reports: `docs/analyses/<filename>.md`
- Architecture overview: `docs/architecture_overview.md`
- Quality assurance report: `docs/analyses/quality_assurance_report.md`
- Vulnerability report: `docs/analyses/vulnerabilities_report.md`
- Performance metrics: `docs/metrics/metrics_<timestamp>.json`

## Active Technologies
- Python 3.8+ (matches existing project) + Rich (terminal UI), subprocess (gh CLI), re/pathlib (parsing) (001-github-issues-cli)
- N/A (reads existing markdown files, writes to GitHub via gh) (001-github-issues-cli)
- Python 3.9+ (matches existing project) + dataclasses, typer (CLI), rich (progress/output), pydantic (validation) (010-safety-profiles)
- Local filesystem (audit logs, allowlist config) (010-safety-profiles)
- Markdown + None (documentation only) (011-readme-safety-docs)

## Recent Changes
- 001-github-issues-cli: Added Python 3.8+ (matches existing project) + Rich (terminal UI), subprocess (gh CLI), re/pathlib (parsing)
