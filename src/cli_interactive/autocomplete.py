"""
Autocomplete Engine for CLI Interactive Mode (v3.0)

Provides command and argument autocomplete with:
- Command name completion
- Argument completion with choices
- Similar command suggestions
- Provider-aware filtering
"""

from typing import Iterable, List, Optional

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

from src.cli_interactive.command_registry import CommandRegistry, Provider


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row: list[int] = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class CommandCompleter(Completer):
    """Autocomplete engine for CLI commands"""

    def __init__(
        self,
        registry: CommandRegistry,
        current_provider: Optional[Provider] = None,
    ) -> None:
        self.registry = registry
        self.current_provider = current_provider

    def set_provider(self, provider: Optional[Provider]) -> None:
        """Update the current provider for filtering"""
        self.current_provider = provider

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent,
    ) -> Iterable[Completion]:
        """Generate completions for the current input"""
        text = document.text_before_cursor.lstrip()

        # Empty or just starting with /
        if not text or text == "/":
            yield from self._complete_command("")
            return

        # Command completion (starts with /)
        if text.startswith("/"):
            parts = text[1:].split(maxsplit=1)
            command_text = parts[0]

            if len(parts) == 1 and not text.endswith(" "):
                # Still typing command name
                yield from self._complete_command(command_text)
            else:
                # After command, complete arguments
                arg_text = parts[1] if len(parts) > 1 else ""
                yield from self._complete_arguments(command_text, arg_text)
        else:
            # Not a command, could be natural language query
            pass

    def _complete_command(self, prefix: str) -> Iterable[Completion]:
        """Complete command names"""
        commands = self.registry.get_command_names(self.current_provider)
        prefix_lower = prefix.lower()

        for name in commands:
            if name.lower().startswith(prefix_lower):
                cmd = self.registry.get(name)
                meta = cmd.description if cmd else ""
                yield Completion(
                    name,
                    start_position=-len(prefix),
                    display=f"/{name}",
                    display_meta=meta,
                )

    def _complete_arguments(
        self,
        command_name: str,
        arg_text: str,
    ) -> Iterable[Completion]:
        """Complete command arguments"""
        cmd = self.registry.get(command_name)
        if not cmd:
            return

        # Find what we're completing
        last_word = arg_text.split()[-1] if arg_text.split() else ""

        # Check if we're completing an argument name
        if last_word.startswith("-"):
            for arg in cmd.arguments:
                if arg.name.lower().startswith(last_word.lower()):
                    yield Completion(
                        arg.name,
                        start_position=-len(last_word),
                        display=arg.name,
                        display_meta=arg.description,
                    )
        # Check if previous word was an argument with choices
        else:
            parts = arg_text.split()
            if len(parts) >= 1:
                prev_arg = parts[-2] if len(parts) >= 2 else parts[-1]
                for arg in cmd.arguments:
                    if arg.name == prev_arg and arg.choices:
                        for choice in arg.choices:
                            if choice.lower().startswith(last_word.lower()):
                                yield Completion(
                                    choice,
                                    start_position=-len(last_word),
                                    display=choice,
                                )

    def suggest_similar(self, command: str, max_distance: int = 2) -> List[str]:
        """Find commands similar to the given one (for typo suggestions)"""
        commands = self.registry.get_command_names(self.current_provider)
        suggestions = []

        for name in commands:
            distance = levenshtein_distance(command.lower(), name.lower())
            if distance <= max_distance and command.lower() != name.lower():
                suggestions.append((name, distance))

        # Sort by distance, then alphabetically
        suggestions.sort(key=lambda x: (x[1], x[0]))
        return [name for name, _ in suggestions[:3]]
