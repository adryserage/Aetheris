# Aetheris Architecture

> **Internal documentation for understanding system design.**

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLI Layer                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  analysis   │  │    fix      │  │     pr      │  │   issues    │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
└─────────┼────────────────┼────────────────┼────────────────┼───────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Core Layer                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      CodeAnalyzer                                │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │                AnalysisOrchestrator                       │   │   │
│  │  │                                                           │   │   │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │   │
│  │  │  │ Stage 1 │→ │ Stage 2 │→ │ Stage 3 │→ │ Stage N │     │   │   │
│  │  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Config    │  │    Cache    │  │  Progress   │  │   Circuit   │   │
│  │   Manager   │  │    Layer    │  │   Manager   │  │   Breaker   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Agent Layer                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Code    │  │ Security │  │ Architect│  │ Metrics  │  │ Vuln     │ │
│  │  Expert  │  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │             │             │             │        │
│       └─────────────┴─────────────┴─────────────┴─────────────┘        │
│                                   │                                     │
│                          ┌────────┴────────┐                           │
│                          │    QA Agent     │                           │
│                          │  (Synthesis)    │                           │
│                          └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Provider Layer                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     AIProvider (Abstract)                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│       │                    │                    │                       │
│       ▼                    ▼                    ▼                       │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐                 │
│  │  Gemini  │        │  OpenAI  │        │  Claude  │                 │
│  │ Provider │        │ Provider │        │ Provider │                 │
│  └──────────┘        └──────────┘        └──────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### CLI Layer (`src/cli.py`)

Entry point for all commands. Uses Typer for CLI framework.

```python
# Key commands
@app.command()
def analysis(...)  # Main analysis command

@app.command()
def fix(...)       # Auto-fix with Claude Code

@app.command()
def pr(...)        # PR review

@app.command()
def issues(...)    # Create GitHub issues
```

### Core Layer (`src/core/`)

#### CodeAnalyzer (`analyzer.py`)

Main orchestration class. Initializes all agents and coordinates analysis.

```python
class CodeAnalyzer:
    def __init__(self, config: AnalysisConfig):
        self.ai_provider = self._create_provider()
        self.orchestrator = AnalysisOrchestrator(self)
        self._init_agents()

    async def analyze(self, files: List[str]) -> AnalysisResult:
        return await self.orchestrator.run(files)
```

#### AnalysisOrchestrator (`orchestrator.py`)

Manages workflow stages and hooks.

```python
class WorkflowStage(Enum):
    INITIALIZATION = "initialization"
    FILE_DISCOVERY = "file_discovery"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    FILE_ANALYSIS = "file_analysis"
    SECURITY_ANALYSIS = "security_analysis"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"
    METRICS_ANALYSIS = "metrics_analysis"
    VULNERABILITY_SCAN = "vulnerability_scan"
    QA_SYNTHESIS = "qa_synthesis"
    REPORT_GENERATION = "report_generation"

class AnalysisOrchestrator:
    def __init__(self, analyzer: CodeAnalyzer):
        self.analyzer = analyzer
        self.hooks: Dict[WorkflowStage, List[Callable]] = {}
        self.shared_context: Dict[str, Any] = {}

    async def run(self, files: List[str]) -> AnalysisResult:
        for stage in WorkflowStage:
            await self._run_hooks(stage, "before")
            result = await self._run_stage(stage)
            await self._run_hooks(stage, "after")
        return self._build_result()
```

#### Configuration (`config.py`)

```python
@dataclass
class AnalysisConfig:
    ai_provider: str = "gemini"
    ai_model: Optional[str] = None
    root_dir: str = "."
    output_dir: str = "docs/analyses"
    batch_size: int = 10
    timeout_seconds: int = 60
    enable_cache: bool = True
    enable_security: bool = True
    enable_metrics: bool = True
    enable_vulnerability: bool = True
    # ... more options
```

#### Cache Layer (`cache.py`)

Git SHA-based caching for analysis results.

```python
class AnalysisCache:
    def __init__(self, cache_dir: str = ".cache/aetheris"):
        self.cache_dir = cache_dir

    def get_cache_key(self, file_path: str, git_sha: str) -> str:
        return hashlib.sha256(f"{file_path}:{git_sha}".encode()).hexdigest()

    async def get(self, key: str) -> Optional[dict]:
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text())
        return None

    async def set(self, key: str, data: dict, ttl: int = 604800):
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps({
            "data": data,
            "expires": time.time() + ttl
        }))
```

### Agent Layer (`src/agents/`)

All agents inherit from `BaseAgent`:

```python
class BaseAgent:
    def __init__(self, ai_provider: AIProvider, config: AnalysisConfig):
        self.ai_provider = ai_provider
        self.config = config

    async def _call_ai_with_retry(self, prompt: str) -> str:
        """Retry with exponential backoff"""

    async def _call_ai_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        """Parse response into Pydantic model"""
```

### AI Provider Layer (`src/core/ai_providers.py`)

Abstract interface for AI providers:

```python
class AIProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        pass

class GeminiProvider(AIProvider):
    # Gemini-specific implementation

class OpenAIProvider(AIProvider):
    # OpenAI-specific implementation

class ClaudeProvider(AIProvider):
    # Claude-specific implementation
```

## Data Flow

```
1. CLI receives command
   │
   ▼
2. CodeAnalyzer initializes
   │
   ▼
3. File discovery (respects .gitignore)
   │
   ▼
4. Dependency graph built
   │
   ▼
5. Files analyzed in parallel batches
   │  ├─ Check cache first
   │  ├─ If miss: call AI provider
   │  └─ Store in cache
   │
   ▼
6. Security analysis on findings
   │
   ▼
7. Architecture analysis
   │
   ▼
8. Metrics calculation
   │
   ▼
9. Vulnerability scan (OSV API)
   │
   ▼
10. QA synthesis (combines all findings)
    │
    ▼
11. Report generation
    ├─ Individual file reports
    ├─ Quality assurance report
    ├─ Vulnerability report
    └─ Metrics JSON
```

## Error Handling

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "open"

    @property
    def is_open(self) -> bool:
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
                return False
            return True
        return False
```

### Retry with Exponential Backoff

```python
async def exponential_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return await func()
        except RetryableError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
```

## Configuration Priority

```
1. CLI flags (highest priority)
   ↓
2. Environment variables
   ↓
3. .env file
   ↓
4. config.json (local)
   ↓
5. ~/.aetheris/config.json (global)
   ↓
6. Built-in defaults (lowest priority)
```

## Performance Optimizations

1. **Parallel Analysis**: Files analyzed in configurable batches
2. **Smart Caching**: Git SHA-based invalidation
3. **Dependency Ordering**: Analyze dependent files together
4. **Context Caching**: Gemini context caching (50% cost reduction)
5. **Batch API**: Gemini batch mode (50% cost reduction)

## Testing Strategy

```
tests/
├── unit/
│   ├── test_agents/       # Individual agent tests
│   ├── test_core/         # Core component tests
│   └── test_models/       # Model validation tests
├── integration/
│   ├── test_analysis.py   # Full analysis flow
│   └── test_providers.py  # AI provider integration
└── fixtures/
    └── sample_code/       # Test code samples
```

## See Also

- [Agent Development](./agents.md)
- [API Reference](./api-reference.md)
- [Contributing Guide](./contributing.md)
