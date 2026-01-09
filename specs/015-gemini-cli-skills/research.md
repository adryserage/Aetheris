# Research: Migration Gemini CLI & Intégration Skills

**Date**: 2026-01-09 | **Branch**: `015-gemini-cli-skills`

## 1. Gemini Function Calling vs Claude Tool Use

### Decision: Adapter Pattern

**Rationale**: Les deux APIs ont des formats différents mais des capacités similaires. Un adapter abstrait les différences.

| Aspect | Gemini Function Calling | Claude Tool Use |
|--------|------------------------|-----------------|
| Declaration | `tools=[{"function_declarations": [...]}]` | `tools=[{"name": ..., "input_schema": ...}]` |
| Invocation | `function_call` in response | `tool_use` content block |
| Result | `function_response` | `tool_result` content block |
| Multi-call | Native support | Native support |

**Alternatives Considered**:
- Direct implementation per provider → Rejected: Code duplication
- Single format with conversion → Rejected: Loses provider-specific features

### Implementation Notes

```python
# Abstract Skill Interface
class Skill(ABC):
    name: str
    description: str
    parameters: dict  # JSON Schema

    @abstractmethod
    async def execute(self, **params) -> SkillResult: ...

# Provider Adapters convert to native format
class ClaudeAdapter:
    def to_tool_definition(self, skill: Skill) -> dict: ...
    def parse_tool_use(self, response) -> SkillCall: ...

class GeminiAdapter:
    def to_function_declaration(self, skill: Skill) -> dict: ...
    def parse_function_call(self, response) -> SkillCall: ...
```

## 2. Interactive CLI with Autocomplete

### Decision: prompt_toolkit

**Rationale**: Bibliothèque mature, support natif autocomplete, compatible Windows/Linux/macOS.

| Library | Pros | Cons |
|---------|------|------|
| prompt_toolkit | Full-featured, async, cross-platform | Larger dependency |
| readline | Built-in | Limited on Windows |
| click.prompt | Simple | No real-time autocomplete |

**Alternatives Considered**:
- readline → Rejected: Poor Windows support
- Custom implementation → Rejected: Reinventing the wheel

### Implementation Pattern

```python
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

class CommandCompleter(Completer):
    def __init__(self, registry: CommandRegistry):
        self.registry = registry

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith('/'):
            prefix = text[1:]
            for cmd in self.registry.get_commands():
                if cmd.startswith(prefix):
                    yield Completion(cmd, start_position=-len(prefix))
```

## 3. MCP Protocol Integration

### Decision: Official MCP SDK (when stable)

**Rationale**: Anthropic's MCP is becoming standard. Use official SDK for compatibility.

| Approach | Pros | Cons |
|----------|------|------|
| Official SDK | Standard-compliant, maintained | May have breaking changes |
| Custom implementation | Full control | Maintenance burden |
| HTTP-only | Simple | Misses stdio transport |

**Alternatives Considered**:
- Custom JSON-RPC implementation → Rejected: MCP spec is complex
- HTTP-only transport → Rejected: Most servers use stdio

### MCP Server Discovery Pattern

```python
# config.json
{
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
      }
    ]
  }
}

# Discovery flow
1. Read config.json mcp.servers
2. Spawn each server process
3. Send initialize request
4. Receive capabilities (tools, resources)
5. Register MCP tools as Skills
```

## 4. Security Sandboxing

### Decision: Path-based sandboxing + safe mode

**Rationale**: Simple, effective, configurable.

| Approach | Pros | Cons |
|----------|------|------|
| Path restriction | Simple, works | Can be bypassed with symlinks |
| chroot/container | Strong isolation | Complex, platform-specific |
| Capability-based | Fine-grained | Requires kernel support |

**Implementation**:

```python
class SandboxedFileSkill(Skill):
    def __init__(self, project_root: Path, safe_mode: bool = True):
        self.project_root = project_root.resolve()
        self.safe_mode = safe_mode

    def _validate_path(self, path: Path) -> Path:
        resolved = (self.project_root / path).resolve()
        if not resolved.is_relative_to(self.project_root):
            raise SecurityError(f"Access denied: {path} is outside project")
        return resolved

    async def execute(self, path: str, **kwargs) -> SkillResult:
        safe_path = self._validate_path(Path(path))
        # ... proceed with operation
```

## 5. Conductor Task Decomposition

### Decision: LLM-driven planning with structured output

**Rationale**: Leverages Gemini's reasoning for complex tasks.

| Approach | Pros | Cons |
|----------|------|------|
| LLM planning | Flexible, handles edge cases | May hallucinate |
| Rule-based | Predictable | Limited to known patterns |
| Hybrid | Best of both | Complex to implement |

**Planning Prompt Pattern**:

```python
PLANNER_PROMPT = """
Decompose this task into a sequence of skill calls:

Task: {user_request}

Available skills:
{skill_descriptions}

Output a JSON plan:
{
  "steps": [
    {"skill": "skill_name", "params": {...}, "depends_on": [step_indices]},
    ...
  ],
  "max_steps": 20
}

Rules:
- Maximum 20 steps
- Each step must use an available skill
- Dependencies must reference previous steps only
"""
```

## 6. Cycle Detection Algorithm

### Decision: State hashing with visited set

**Rationale**: Simple O(n) detection, catches most infinite loops.

```python
class CycleDetector:
    def __init__(self, max_visits: int = 2):
        self.state_visits: dict[str, int] = {}
        self.max_visits = max_visits

    def check_and_record(self, state: ExecutionState) -> bool:
        """Returns True if cycle detected."""
        state_hash = self._hash_state(state)
        self.state_visits[state_hash] = self.state_visits.get(state_hash, 0) + 1
        return self.state_visits[state_hash] > self.max_visits

    def _hash_state(self, state: ExecutionState) -> str:
        # Hash relevant state: current step, pending skills, key variables
        return hashlib.md5(json.dumps(state.to_dict(), sort_keys=True)).hexdigest()
```

## 7. Command Registry Design

### Decision: Provider-specific registries with common interface

**Rationale**: Different CLIs have different commands, but unified access pattern.

```python
@dataclass
class Command:
    name: str
    description: str
    arguments: list[Argument]
    provider: str  # "claude", "gemini", "aetheris"

class CommandRegistry:
    def __init__(self):
        self._commands: dict[str, list[Command]] = {
            "claude": [],
            "gemini": [],
            "aetheris": [],  # Built-in commands
        }

    def register(self, provider: str, command: Command):
        self._commands[provider].append(command)

    def get_commands(self, provider: str) -> list[Command]:
        # Return provider-specific + aetheris built-in
        return self._commands[provider] + self._commands["aetheris"]

    def find_similar(self, name: str, provider: str) -> list[Command]:
        # Levenshtein distance ≤2
        return [c for c in self.get_commands(provider)
                if levenshtein(c.name, name) <= 2]
```

## Summary of Decisions

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| Skill abstraction | Adapter pattern | Format differences, code reuse |
| Interactive CLI | prompt_toolkit | Cross-platform autocomplete |
| MCP integration | Official SDK | Standard compliance |
| Sandboxing | Path-based + safe mode | Simple, effective |
| Conductor planning | LLM-driven | Flexibility for complex tasks |
| Cycle detection | State hashing | O(n) efficiency |
| Command registry | Provider-specific | Different CLI capabilities |
