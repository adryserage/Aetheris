# Implementation Plan: Persistent Configuration & Local Config File

**Branch**: `006-persistent-config` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Target Version**: v2.9

## Summary

Migrate configuration from .env to config.json with cascade hierarchy (CLI > Local > Global > Env > Defaults). Add `aetheris init` and `aetheris settings` commands.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: Rich/Textual (interactive UI), JSON
**Storage**: ~/.aetheris/config.json (global), ./config.json (local)
**Constraints**: Secrets must remain in .env only

## Project Structure

```text
src/core/config_file.py      # NEW: ConfigFile, ConfigHierarchy
src/core/config_schema.py    # NEW: ConfigSchema with all options
src/core/settings_ui.py      # NEW: Interactive settings UI
src/cli.py                   # MODIFY: Add init, settings commands
config/default.json          # NEW: Default configuration
```

## Configuration Hierarchy

```
1. CLI arguments (highest priority)
2. Local config.json (project root)
3. Global config.json (~/.aetheris/)
4. Environment variables (.env)
5. Default values (lowest priority)
```

## Config Schema

```json
{
  "ai": {
    "provider": "gemini",
    "model": "gemini-1.5-pro",
    "temperature": 0.7
  },
  "analysis": {
    "timeout_minutes": 60,
    "parallel_files": 5,
    "exclude_patterns": []
  },
  "output": {
    "format": "markdown",
    "directory": "docs/analyses"
  }
}
```

## Settings UI Categories

1. **General** - Language, verbosity
2. **AI Provider** - Provider, model, temperature
3. **Analysis** - Timeout, parallelism, exclusions
4. **Output** - Format, directory
5. **Advanced** - Cache, debug mode

## Next Steps

1. Generate tasks.md
2. Implement config file loading
3. Implement init command
4. Implement settings UI
5. Migrate existing options
