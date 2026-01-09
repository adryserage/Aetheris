# Agent Development Guide

> **Internal documentation for creating custom Aetheris agents.**

## Agent Architecture

All agents inherit from `BaseAgent` class located in `src/agents/base_agent.py`:

```python
class BaseAgent:
    def __init__(self, ai_provider: AIProvider, config: AnalysisConfig):
        self.ai_provider = ai_provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    async def _call_ai_with_retry(self, prompt: str) -> str:
        """Standard AI call with exponential backoff retry"""
        pass

    async def _call_ai_with_reasoning(self, prompt: str) -> str:
        """AI call with reasoning display (Gemini Thinking, OpenAI o1)"""
        pass

    async def _call_ai_structured(self, prompt: str, schema: Type[BaseModel]) -> BaseModel:
        """AI call with Pydantic schema validation"""
        pass
```

## Structured Output with Pydantic

The `_call_ai_structured` method validates AI responses against Pydantic schemas:

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class SecurityIssue(BaseModel):
    severity: str = Field(description="Issue severity: critical, high, medium, low")
    description: str = Field(description="Detailed description of the issue")
    file_path: str = Field(description="Path to affected file")
    line_number: Optional[int] = Field(default=None, description="Line number if applicable")
    cwe_id: Optional[str] = Field(default=None, description="CWE identifier")
    recommendation: str = Field(description="How to fix the issue")

class SecurityAnalysisResult(BaseModel):
    issues: List[SecurityIssue] = Field(default_factory=list)
    risk_score: int = Field(ge=0, le=100, description="Overall risk score 0-100")
    summary: str = Field(description="Executive summary of findings")

# Usage in agent
result = await self._call_ai_structured(prompt, SecurityAnalysisResult)
```

## Workflow Integration

Agents are registered in the `AnalysisOrchestrator` via `WorkflowStage` enum:

```python
from src.core.orchestrator import WorkflowStage

# Available stages
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
```

## Creating a Custom Agent

### Step 1: Create Agent File

```python
# src/agents/performance_agent.py
from src.agents.base_agent import BaseAgent
from src.models.data_models import PerformanceAnalysisResult
from typing import List

class PerformanceAnalysisAgent(BaseAgent):
    """Analyzes code for performance issues and optimization opportunities."""

    async def analyze(self, files: List[str], context: dict) -> PerformanceAnalysisResult:
        prompt = self._build_prompt(files, context)
        return await self._call_ai_structured(prompt, PerformanceAnalysisResult)

    def _build_prompt(self, files: List[str], context: dict) -> str:
        return f"""
        Analyze the following code for performance issues:

        Files: {files}
        Context: {context}

        Identify:
        - N+1 query patterns
        - Inefficient algorithms (O(n²) or worse)
        - Memory leaks
        - Blocking operations in async code
        - Missing caching opportunities
        - Excessive database queries
        - Large object allocations in loops

        For each issue, provide:
        - Severity (critical, high, medium, low)
        - File path and line number
        - Description of the problem
        - Recommended fix with code example
        """
```

### Step 2: Define Response Schema

```python
# src/models/performance_models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class PerformanceIssue(BaseModel):
    severity: str = Field(description="Issue severity")
    category: str = Field(description="Category: algorithm, database, memory, async, caching")
    file_path: str
    line_number: Optional[int] = None
    description: str
    recommendation: str
    estimated_impact: str = Field(description="Performance improvement estimate")

class PerformanceAnalysisResult(BaseModel):
    issues: List[PerformanceIssue] = Field(default_factory=list)
    performance_score: int = Field(ge=0, le=100)
    summary: str
    optimization_priority: List[str] = Field(description="Ordered list of optimization targets")
```

### Step 3: Register in CodeAnalyzer

```python
# src/core/analyzer.py
from src.agents.performance_agent import PerformanceAnalysisAgent

class CodeAnalyzer:
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.ai_provider = self._create_provider()

        # Existing agents
        self.code_expert = CodeExpertAgent(self.ai_provider, config)
        self.security_agent = SecurityAnalysisAgent(self.ai_provider, config)
        self.architect_agent = ArchitectAnalysisAgent(self.ai_provider, config)
        self.metrics_agent = MetricsAgent(self.ai_provider, config)
        self.vulnerability_agent = VulnerabilityAgent(self.ai_provider, config)
        self.qa_agent = QAAgent(self.ai_provider, config)

        # New agent
        self.performance_agent = PerformanceAnalysisAgent(self.ai_provider, config)
```

### Step 4: Add Workflow Stage

```python
# src/core/orchestrator.py
class WorkflowStage(Enum):
    # ... existing stages ...
    PERFORMANCE_ANALYSIS = "performance_analysis"

class AnalysisOrchestrator:
    async def _run_stage(self, stage: WorkflowStage) -> Any:
        handlers = {
            # ... existing handlers ...
            WorkflowStage.PERFORMANCE_ANALYSIS: self._run_performance_analysis,
        }
        return await handlers[stage]()

    async def _run_performance_analysis(self) -> PerformanceAnalysisResult:
        files = self._get_analysis_files()
        result = await self.analyzer.performance_agent.analyze(files, self.shared_context)
        self.shared_context["performance_findings"] = result.issues
        return result
```

### Step 5: Update Presets

```json
// config/presets.json
{
  "full-analysis": {
    "description": "Complete analysis with all agents",
    "agents": ["code_expert", "security", "architect", "metrics", "vulnerability", "qa", "performance"]
  },
  "performance-focused": {
    "description": "Performance optimization analysis",
    "agents": ["performance", "metrics"]
  }
}
```

## Agent Communication

Agents share context through the orchestrator's shared state:

```python
# In orchestrator
self.shared_context = {
    "file_analyses": {},      # Results from FILE_ANALYSIS stage
    "security_findings": [],   # Results from SECURITY_ANALYSIS
    "architecture_info": {},   # Results from ARCHITECTURE_ANALYSIS
    "metrics": {},            # Results from METRICS_ANALYSIS
    "vulnerabilities": [],    # Results from VULNERABILITY_SCAN
    "performance_findings": [], # Results from PERFORMANCE_ANALYSIS
}

# Agents access shared context
class QAAgent(BaseAgent):
    async def synthesize(self, context: dict) -> QAReport:
        # Access all previous agent results
        security = context.get("security_findings", [])
        metrics = context.get("metrics", {})
        performance = context.get("performance_findings", [])
        # ... synthesize findings ...
```

## Error Handling

Agents use circuit breaker pattern for resilience:

```python
from src.core.circuit_breaker import CircuitBreaker

class BaseAgent:
    def __init__(self, ...):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60
        )

    async def _call_ai_with_retry(self, prompt: str) -> str:
        if self.circuit_breaker.is_open:
            raise CircuitBreakerOpenError("Too many failures, circuit open")

        try:
            result = await self._execute_ai_call(prompt)
            self.circuit_breaker.record_success()
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise
```

## Testing Agents

```python
# tests/agents/test_performance_agent.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.generate.return_value = '''
    {
        "issues": [
            {
                "severity": "high",
                "category": "database",
                "file_path": "src/api/users.py",
                "line_number": 45,
                "description": "N+1 query pattern detected",
                "recommendation": "Use eager loading",
                "estimated_impact": "10x improvement"
            }
        ],
        "performance_score": 65,
        "summary": "Database query optimization needed",
        "optimization_priority": ["database", "caching"]
    }
    '''
    return provider

@pytest.fixture
def config():
    return MagicMock(spec=AnalysisConfig)

@pytest.mark.asyncio
async def test_performance_agent_detects_n_plus_one(mock_provider, config):
    agent = PerformanceAnalysisAgent(mock_provider, config)
    result = await agent.analyze(["src/api/users.py"], {})

    assert len(result.issues) == 1
    assert result.issues[0].severity == "high"
    assert result.issues[0].category == "database"
    assert result.performance_score == 65

@pytest.mark.asyncio
async def test_performance_agent_handles_empty_files(mock_provider, config):
    mock_provider.generate.return_value = '{"issues": [], "performance_score": 100, "summary": "No issues", "optimization_priority": []}'

    agent = PerformanceAnalysisAgent(mock_provider, config)
    result = await agent.analyze([], {})

    assert len(result.issues) == 0
    assert result.performance_score == 100
```

## Prompt Engineering Guidelines

| Practice | Example |
|----------|---------|
| **Be specific** | "Identify SQL injection vulnerabilities" not "find security issues" |
| **Request structured output** | Always ask for JSON with defined schema |
| **Provide context** | Include file path, language, project type |
| **Set constraints** | "List maximum 10 issues, prioritized by severity" |
| **Include examples** | Show expected output format in prompt |

## Agent Registration Checklist

- [ ] Create agent class inheriting from `BaseAgent`
- [ ] Define Pydantic response schema in `src/models/`
- [ ] Add agent to `CodeAnalyzer.__init__()`
- [ ] Add `WorkflowStage` enum value
- [ ] Add workflow handler in `AnalysisOrchestrator`
- [ ] Update `config/presets.json`
- [ ] Add to `--agents` CLI help text
- [ ] Create unit tests in `tests/agents/`
- [ ] Update documentation

## See Also

- [Architecture Guide](./architecture.md)
- [API Reference](./api-reference.md)
- [PLUGINS.md](../docs/PLUGINS.md)
