# Implementation Plan: Flexible Timeout Management

**Branch**: `002-flexible-timeout` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Target Version**: v2.6.1

## Summary

Implement flexible timeout management for Aetheris analysis commands. Extends default timeout to 60 minutes, adds CLI parameter for custom timeouts, and provides heartbeat feedback during long-running operations.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: asyncio (timeout handling), Rich (progress display)
**Testing**: Unit tests for timeout parsing, integration tests for CLI
**Target Platform**: Cross-platform (Linux, macOS, Windows)
**Constraints**: Must be backward compatible with existing CLI usage

## Project Structure

### Files to Modify

```text
src/cli.py                    # ADD: --timeout/-t parameter
src/core/config.py            # ADD: TimeoutConfig dataclass, default timeout
src/core/orchestrator.py      # MODIFY: Apply timeout to analysis workflow
src/core/heartbeat.py         # NEW: HeartbeatMonitor class
```

## Content Structure

### TimeoutConfig

```python
@dataclass
class TimeoutConfig:
    value: int           # Timeout in seconds
    enabled: bool        # Whether timeout is active

    @classmethod
    def parse(cls, value: str) -> "TimeoutConfig":
        """Parse timeout from CLI string (e.g., '30m', '2h', '3600', '0')"""
```

### HeartbeatMonitor

```python
class HeartbeatMonitor:
    def __init__(self, interval_minutes: int = 10):
        """Initialize heartbeat with configurable interval"""

    async def start(self) -> None:
        """Start heartbeat in background"""

    async def stop(self) -> None:
        """Stop heartbeat"""
```

## Research Summary

No external research needed - uses standard Python async patterns.

Key implementation notes:
- Use `asyncio.wait_for()` for timeout enforcement
- Use `asyncio.create_task()` for background heartbeat
- Parse timeout with regex: `^(\d+)(s|m|h)?$`
- Special values: `0` or `no-limit` disables timeout

## Next Steps

1. Generate tasks.md with implementation tasks
2. Implement TimeoutConfig in config.py
3. Implement HeartbeatMonitor
4. Add CLI parameter
5. Integrate with orchestrator
