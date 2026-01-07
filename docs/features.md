# Features

## Performance & Optimization

### Intelligent Cache
- Git SHA-based cache invalidation
- Persistent storage in `.cache/aetheris/`
- Configurable TTL (default: 7 days)
- 60-80% API cost reduction

```bash
# Disable cache if needed
ENABLE_CACHE=false aetheris analysis
```

### Smart Parallelization
- Dependency graph-based analysis
- Independent files analyzed simultaneously
- Respects dependency order
- Significant time reduction

### Priority System (PR Reviews)
| Priority | Files |
|----------|-------|
| HIGH | Modified in PR |
| MEDIUM | Direct dependencies |
| LOW | Other files |

### Context Caching (Gemini)
```env
ENABLE_CONTEXT_CACHING=true
CONTEXT_CACHE_TTL_SECONDS=3600
```
- 50% API cost reduction
- Reuses context between requests

### Batch API (Gemini)
```env
ENABLE_BATCH_MODE=true
```
- 50% price reduction
- Best for large projects

## Analysis Capabilities

### Security Analysis
- SQL/XSS/Command injection
- Hardcoded secrets detection
- Weak cryptography
- Authentication issues
- CWE identifiers
- OWASP categories

### Code Metrics
- Cyclomatic complexity
- Code duplication detection
- Nesting depth
- Maintainability index

### Dependency Vulnerabilities
- OSV API integration
- npm, PyPI, Pub support
- CVE identification
- Fixed version recommendations

### Incremental Analysis
- Transitive dependencies analysis
- Configurable depth (default: 2)
- PR-optimized (only impacted files)

## AI Features

### Multi-Provider Support
```env
AI_PROVIDER=gemini  # or openai, claude
```

### Consensus Mode (PR Review)
```bash
aetheris pr --providers gemini,claude --consensus
```
Only reports issues found by ALL providers.

### Structured Outputs (Gemini)
```env
ENABLE_STRUCTURED_OUTPUTS=true
```
JSON responses validated via Pydantic.

### Thinking Mode (Gemini 2.5+)
```env
ENABLE_THINKING=true
THINKING_BUDGET=2048
```
See the model's reasoning process.

### Code Execution (Gemini)
```env
ENABLE_CODE_EXECUTION=true
```
Python sandbox for dynamic analysis.

## Error Handling

### Circuit Breaker
Prevents repeated API calls on errors.

### Exponential Backoff
Intelligent retry with increasing delays.

### Error Classification
- Temporary: Retry with backoff
- Permanent: Skip with logging
- Critical: Halt and report

## Extensibility

### Hook System
Register custom hooks on workflow stages:

```python
orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, my_hook)
```

See [PLUGINS.md](./PLUGINS.md) for details.

### Metrics Export
Performance metrics saved to:
```
docs/metrics/metrics_YYYYMMDD_HHMMSS.json
```

Contains:
- Execution duration
- Per-stage metrics
- Agent statistics
- Cache hit rate
- Token estimates

## Supported Languages

| Language | Extensions |
|----------|------------|
| Python | `.py` |
| TypeScript | `.ts`, `.tsx` |
| JavaScript | `.js`, `.jsx` |
| Dart/Flutter | `.dart` |
| Java | `.java` |
| Kotlin | `.kt` |
| Swift | `.swift` |
| Go | `.go` |
| Rust | `.rs` |
| C/C++ | `.c`, `.cpp`, `.h` |
| C# | `.cs` |
| PHP | `.php` |
| Ruby | `.rb` |

## Excluded Files

Automatically excluded:
- Build directories (`build/`, `dist/`, `node_modules/`)
- Generated files (`.g.dart`, `.d.ts`, `.pyc`)
- Lock files (`package-lock.json`, `yarn.lock`)
- Binary files (> 1MB)
- Hidden directories (`.git/`, `.venv/`)
- `.gitignore` patterns respected
