"""Python code minifier for reducing package size."""

import ast
import io
import logging
import tokenize
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Minifier:
    """Minifier for Python source code."""

    def __init__(self, strip_docstrings: bool = False, keep_public_docs: bool = True):
        """Initialize the minifier.

        Args:
            strip_docstrings: Whether to remove docstrings
            keep_public_docs: Keep module and public class/function docstrings
        """
        self.strip_docstrings = strip_docstrings
        self.keep_public_docs = keep_public_docs

    def remove_comments(self, source: str) -> str:
        """Remove comments from Python source code.

        Preserves:
        - Strings (even if they look like comments)
        - Shebang lines (#!)
        - Type comments (# type:)

        Args:
            source: Python source code

        Returns:
            Source with comments removed
        """
        result = []
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0

        try:
            tokens = tokenize.generate_tokens(io.StringIO(source).readline)

            for tok in tokens:
                token_type = tok.type
                token_string = tok.string
                start_line, start_col = tok.start
                end_line, end_col = tok.end

                # Handle newlines between tokens
                if start_line > last_lineno:
                    last_col = 0

                # Add whitespace if needed
                if start_col > last_col:
                    result.append(" " * (start_col - last_col))

                # Skip comments (but preserve type comments and shebangs)
                if token_type == tokenize.COMMENT:
                    if token_string.startswith("#!") or "type:" in token_string:
                        result.append(token_string)
                    # Otherwise skip the comment
                elif token_type == tokenize.NL:
                    # Preserve newlines
                    result.append(token_string)
                elif token_type == tokenize.NEWLINE:
                    result.append(token_string)
                else:
                    result.append(token_string)

                prev_toktype = token_type
                last_lineno = end_line
                last_col = end_col

        except tokenize.TokenizeError as e:
            logger.warning(f"Tokenize error: {e}, returning original source")
            return source

        return "".join(result)

    def remove_docstrings(self, source: str, keep_public: bool = True) -> str:
        """Remove docstrings from Python source code.

        Args:
            source: Python source code
            keep_public: Keep module-level and public class/function docstrings

        Returns:
            Source with docstrings removed
        """
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            logger.warning(f"Parse error: {e}, returning original source")
            return source

        # Collect positions of docstrings to remove
        docstring_positions = []

        for node in ast.walk(tree):
            # Check for docstring nodes
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if not hasattr(node, "body") or not node.body:
                    continue

                first_stmt = node.body[0]
                if not isinstance(first_stmt, ast.Expr):
                    continue
                if not isinstance(first_stmt.value, ast.Constant):
                    continue
                if not isinstance(first_stmt.value.value, str):
                    continue

                # This is a docstring
                is_public = True
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    is_public = not node.name.startswith("_")
                elif isinstance(node, ast.ClassDef):
                    is_public = not node.name.startswith("_")

                # Skip if we should keep public docstrings
                if keep_public and (isinstance(node, ast.Module) or is_public):
                    continue

                # Mark for removal
                docstring_positions.append(
                    (first_stmt.lineno, first_stmt.end_lineno or first_stmt.lineno)
                )

        if not docstring_positions:
            return source

        # Remove docstrings from source
        lines = source.splitlines(keepends=True)
        lines_to_remove = set()

        for start_line, end_line in docstring_positions:
            for line_num in range(start_line, end_line + 1):
                lines_to_remove.add(line_num - 1)  # Convert to 0-indexed

        result = []
        for i, line in enumerate(lines):
            if i not in lines_to_remove:
                result.append(line)

        return "".join(result)

    def minify(self, source: str) -> str:
        """Apply all configured minification steps.

        Args:
            source: Python source code

        Returns:
            Minified source code
        """
        result = self.remove_comments(source)

        if self.strip_docstrings:
            result = self.remove_docstrings(result, keep_public=self.keep_public_docs)

        return result

    def minify_file(self, filepath: str | Path, output: str | Path | None = None) -> str:
        """Minify a Python file.

        Args:
            filepath: Path to the source file
            output: Optional output path (overwrites source if None)

        Returns:
            Minified source code
        """
        filepath = Path(filepath)

        if filepath.suffix != ".py":
            logger.warning(f"Skipping non-Python file: {filepath}")
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        minified = self.minify(source)

        if output:
            output_path = Path(output)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(minified)

        return minified

    def preview_minification(self, filepath: str | Path) -> dict:
        """Preview minification without applying changes.

        Args:
            filepath: Path to the source file

        Returns:
            Dict with original_size, minified_size, savings_percent
        """
        filepath = Path(filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        minified = self.minify(source)

        original_size = len(source.encode("utf-8"))
        minified_size = len(minified.encode("utf-8"))
        savings = original_size - minified_size
        savings_percent = (savings / original_size * 100) if original_size > 0 else 0

        return {
            "filepath": str(filepath),
            "original_size": original_size,
            "minified_size": minified_size,
            "savings_bytes": savings,
            "savings_percent": round(savings_percent, 2),
        }
