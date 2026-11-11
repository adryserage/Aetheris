# Data Model: Migration Gemini CLI & Intégration Skills

**Date**: 2026-01-09 | **Branch**: `015-gemini-cli-skills`

## Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  CommandRegistry │────▶│     Command      │────▶│    Argument     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │
        │                        ▼
        │               ┌─────────────────┐
        └──────────────▶│ CommandCompleter│
                        └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  SkillRegistry   │────▶│      Skill       │◀────│  SkillAdapter   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                       │
        │                        ▼                       │
        │               ┌─────────────────┐              │
        │               │   SkillResult    │              │
        │               └─────────────────┘              │
        │                                                │
        ▼                                                ▼
┌─────────────────┐                             ┌─────────────────┐
│   MCPToolBridge  │                             │  ClaudeAdapter  │
└─────────────────┘                             │  GeminiAdapter  │
                                                └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Conductor     │────▶│  ExecutionPlan   │────▶│  PlanStep       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │
        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐
│  CycleDetector   │     │  ExecutionState  │
└─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    MCPClient     │────▶│   MCPServer      │────▶│   MCPTool       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │   MCPResource    │
                        └─────────────────┘
```

## Core Entities

### Command (CLI)

```python
@dataclass
class Argument:
    name: str
    description: str
    type: str  # "string", "int", "bool", "file"
    required: bool = False
    default: Any = None

@dataclass
class Command:
    name: str                    # e.g., "analysis", "commit"
    description: str             # Help text
    arguments: list[Argument]    # Command arguments
    provider: str                # "claude", "gemini", "aetheris"
    aliases: list[str] = field(default_factory=list)  # e.g., ["a"] for "analysis"

    def matches(self, prefix: str) -> bool:
        """Check if command matches prefix for autocomplete."""
        return self.name.startswith(prefix) or any(a.startswith(prefix) for a in self.aliases)
```

### CommandRegistry

```python
@dataclass
class CommandRegistry:
    commands: dict[str, list[Command]]  # provider -> commands
    active_provider: str = "gemini"

    def register(self, provider: str, command: Command) -> None: ...
    def get_commands(self, provider: str | None = None) -> list[Command]: ...
    def find_by_name(self, name: str) -> Command | None: ...
    def find_similar(self, name: str, threshold: int = 2) -> list[Command]: ...
```

### Skill

```python
@dataclass
class SkillParameter:
    name: str
    description: str
    type: str  # JSON Schema type
    required: bool = True
    enum: list[str] | None = None

@dataclass
class Skill:
    name: str                         # e.g., "read_file"
    description: str                  # For AI context
    parameters: list[SkillParameter]  # Input parameters
    returns: str                      # Return type description
    safe: bool = True                 # Requires confirmation if False

    def to_json_schema(self) -> dict:
        """Convert to JSON Schema for API calls."""
        ...

@dataclass
class SkillResult:
    success: bool
    data: Any                # Result data
    error: str | None = None # Error message if failed
    metadata: dict = field(default_factory=dict)  # Timing, etc.
```

### SkillRegistry

```python
@dataclass
class SkillRegistry:
    skills: dict[str, Skill]           # name -> Skill
    custom_skills_path: Path | None    # Path to custom skill definitions
    enabled_skills: set[str]           # Currently enabled skill names

    def register(self, skill: Skill) -> None: ...
    def get(self, name: str) -> Skill | None: ...
    def list_enabled(self) -> list[Skill]: ...
    def load_custom_skills(self) -> None: ...
    def validate_skill_definition(self, path: Path) -> list[str]: ...  # Returns errors
```

### ExecutionPlan (Conductor)

```python
@dataclass
class PlanStep:
    id: int
    skill: str                    # Skill name to execute
    params: dict[str, Any]        # Parameters for skill
    depends_on: list[int]         # Step IDs this depends on
    status: str = "pending"       # "pending", "running", "completed", "failed"
    result: SkillResult | None = None

@dataclass
class ExecutionPlan:
    task: str                     # Original user request
    steps: list[PlanStep]         # Ordered steps
    created_at: datetime
    max_steps: int = 20           # NFR-003 limit

    def is_valid(self) -> tuple[bool, str]: ...  # Validates DAG, step limit
    def get_ready_steps(self) -> list[PlanStep]: ...  # Steps with deps satisfied

@dataclass
class ExecutionState:
    plan: ExecutionPlan
    current_step: int
    completed_steps: set[int]
    variables: dict[str, Any]     # Step outputs for reference

    def to_dict(self) -> dict: ...  # For hashing in cycle detection
```

### MCPClient

```python
@dataclass
class MCPServerConfig:
    name: str
    command: str              # e.g., "npx"
    args: list[str]           # e.g., ["-y", "@mcp/server"]
    env: dict[str, str] = field(default_factory=dict)

@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: dict        # JSON Schema
    server: str               # Server name that provides this tool

@dataclass
class MCPResource:
    uri: str
    name: str
    description: str
    mime_type: str
    server: str

@dataclass
class MCPClient:
    servers: dict[str, MCPServerConfig]
    connected: dict[str, bool]
    tools: list[MCPTool]
    resources: list[MCPResource]

    async def connect(self, server_name: str) -> bool: ...
    async def disconnect(self, server_name: str) -> None: ...
    async def call_tool(self, tool_name: str, params: dict) -> Any: ...
    async def read_resource(self, uri: str) -> str: ...
```

## Adapter Interfaces

### SkillAdapter (Abstract)

```python
class SkillAdapter(ABC):
    @abstractmethod
    def to_api_format(self, skill: Skill) -> dict:
        """Convert Skill to provider-specific API format."""
        ...

    @abstractmethod
    def parse_response(self, response: Any) -> list[SkillCall]:
        """Parse provider response to extract skill calls."""
        ...

    @abstractmethod
    def format_result(self, result: SkillResult) -> dict:
        """Format result for provider API."""
        ...

@dataclass
class SkillCall:
    skill_name: str
    arguments: dict[str, Any]
    call_id: str  # For matching results
```

### ClaudeAdapter

```python
class ClaudeAdapter(SkillAdapter):
    def to_api_format(self, skill: Skill) -> dict:
        return {
            "name": skill.name,
            "description": skill.description,
            "input_schema": skill.to_json_schema()
        }

    def parse_response(self, response) -> list[SkillCall]:
        # Extract tool_use blocks from response.content
        ...

    def format_result(self, result: SkillResult) -> dict:
        return {
            "type": "tool_result",
            "tool_use_id": result.metadata.get("call_id"),
            "content": str(result.data) if result.success else result.error
        }
```

### GeminiAdapter

```python
class GeminiAdapter(SkillAdapter):
    def to_api_format(self, skill: Skill) -> dict:
        return {
            "name": skill.name,
            "description": skill.description,
            "parameters": skill.to_json_schema()
        }

    def parse_response(self, response) -> list[SkillCall]:
        # Extract function_call from response.candidates
        ...

    def format_result(self, result: SkillResult) -> dict:
        return {
            "name": result.metadata.get("skill_name"),
            "response": {"result": result.data if result.success else {"error": result.error}}
        }
```

## State Transitions

### Skill Execution Flow

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│ Pending │───▶│ Validating│───▶│ Executing │───▶│ Completed │
└─────────┘    └──────────┘    └───────────┘    └──────────┘
                    │                │
                    ▼                ▼
              ┌──────────┐    ┌──────────┐
              │ Rejected │    │  Failed  │
              └──────────┘    └──────────┘
```

### Conductor Plan Execution

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│ Planning│───▶│ Executing │───▶│ Completed │    │ Aborted  │
└─────────┘    └──────────┘    └───────────┘    └──────────┘
     │              │                               ▲
     │              │         ┌───────────┐         │
     │              └────────▶│ Replanning│─────────┤
     │                        └───────────┘         │
     │                             │                │
     └─────────────────────────────┴── (on error) ──┘
```

## Validation Rules

| Entity | Rule | Error |
|--------|------|-------|
| Command | name must be unique per provider | `DuplicateCommandError` |
| Skill | name must be unique globally | `DuplicateSkillError` |
| SkillParameter | type must be valid JSON Schema type | `InvalidParameterTypeError` |
| ExecutionPlan | steps ≤ max_steps (20) | `PlanTooLongError` |
| ExecutionPlan | depends_on must reference earlier steps | `InvalidDependencyError` |
| MCPServerConfig | command must exist in PATH | `MCPServerNotFoundError` |
