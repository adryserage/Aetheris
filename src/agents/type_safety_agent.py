"""
Type Safety Analysis Agent (v2.10)

Detects any usage, unsafe casts, null safety violations, and type-related issues.
Supports TypeScript, Python, Java, and other typed languages.
"""

import re
from typing import List, Optional

from src.agents.base_agent import BaseAgent
from src.core.config import AnalysisConfig
from src.core.progress import ProgressManager
from src.models.data_models import TypeSafetyIssue


class TypeSafetyAgent(BaseAgent):
    """Agent for detecting type safety issues in code"""

    def __init__(self, config: AnalysisConfig, progress_manager: Optional[ProgressManager] = None):
        super().__init__(config, progress_manager)

        # Patterns for detecting type safety issues by language
        self.patterns = {
            "typescript": {
                "any_usage": [
                    r"\bany\b(?!\s*\()",  # any type (not function call)
                    r":\s*any\b",
                    r"<any>",
                    r"as\s+any\b",
                ],
                "unsafe_cast": [
                    r"as\s+unknown\s+as",  # Double cast
                    r"<\w+>\s*\(",  # C-style cast
                    r"!\.",  # Non-null assertion
                    r"!\[",  # Non-null assertion on index
                ],
                "type_ignore": [
                    r"@ts-ignore",
                    r"@ts-nocheck",
                    r"@ts-expect-error",
                ],
                "null_safety": [
                    r"\?\.\s*\(",  # Optional chaining before call (might hide errors)
                    r"\?\?\s*(?:null|undefined)",  # Nullish coalescing with null/undefined
                ],
            },
            "python": {
                "any_usage": [
                    r":\s*Any\b",
                    r"->\s*Any\b",
                    r"Union\[.*Any.*\]",
                    r"Optional\[Any\]",
                ],
                "unsafe_cast": [
                    r"\bcast\s*\(",
                    r"# type: ignore\[",  # Specific type ignore
                ],
                "type_ignore": [
                    r"# type: ignore",
                    r"# noqa: ",
                    r"# pyright: ignore",
                    r"# mypy: ignore",
                ],
                "null_safety": [
                    r"if\s+\w+\s+is\s+not\s+None\s*:.*\n.*\w+\.",  # None check followed by access
                ],
            },
            "java": {
                "any_usage": [
                    r"\bObject\b(?!\s*\()",  # Raw Object type
                    r"<\?>",  # Unbounded wildcard
                ],
                "unsafe_cast": [
                    r"\(\s*\w+\s*\)\s*\w+",  # C-style cast
                    r"@SuppressWarnings\s*\(\s*[\"']unchecked[\"']\s*\)",
                ],
                "type_ignore": [
                    r"@SuppressWarnings",
                ],
                "null_safety": [
                    r"\.get\s*\(\s*\w+\s*\)\s*\.",  # Method chaining on get() result
                    r"return\s+null\b",  # Returning null
                ],
            },
        }

    def _detect_language(self, file_path: str, content: str) -> str:
        """Detect programming language from file extension"""
        if file_path.endswith((".ts", ".tsx")):
            return "typescript"
        elif file_path.endswith((".py", ".pyi")):
            return "python"
        elif file_path.endswith(".java"):
            return "java"
        elif file_path.endswith((".js", ".jsx")):
            return "javascript"
        elif file_path.endswith(".go"):
            return "go"
        elif file_path.endswith(".rs"):
            return "rust"
        return "unknown"

    def _detect_pattern_issues(
        self, content: str, file_path: str, language: str
    ) -> List[TypeSafetyIssue]:
        """Detect type safety issues via patterns"""
        issues = []

        if language not in self.patterns:
            return issues

        lang_patterns = self.patterns[language]

        for issue_type, patterns in lang_patterns.items():
            for pattern in patterns:
                for i, line in enumerate(content.split("\n"), 1):
                    # Skip comments
                    stripped = line.strip()
                    if self._is_comment(stripped, language):
                        continue

                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_severity(issue_type)
                        issues.append(
                            TypeSafetyIssue(
                                severity=severity,
                                issue_type=issue_type,
                                description=self._get_description(issue_type, pattern),
                                line_number=i,
                                code_snippet=line.strip()[:100],
                                recommendation=self._get_recommendation(issue_type),
                                language=language,
                            )
                        )

        return issues

    def _is_comment(self, line: str, language: str) -> bool:
        """Check if line is a comment"""
        if language in ["typescript", "javascript", "java", "go", "rust"]:
            return line.startswith("//") or line.startswith("/*") or line.startswith("*")
        elif language == "python":
            return line.startswith("#") or line.startswith('"""') or line.startswith("'''")
        return False

    def _get_severity(self, issue_type: str) -> str:
        """Get severity for issue type"""
        severity_map = {
            "any_usage": "medium",
            "unsafe_cast": "high",
            "type_ignore": "medium",
            "null_safety": "low",
        }
        return severity_map.get(issue_type, "medium")

    def _get_description(self, issue_type: str, pattern: str) -> str:
        """Get description for issue type"""
        descriptions = {
            "any_usage": "Use of 'any' type bypasses type checking",
            "unsafe_cast": "Unsafe type cast may hide type errors",
            "type_ignore": "Type checking is suppressed",
            "null_safety": "Potential null/undefined access",
        }
        return descriptions.get(issue_type, f"Type safety issue: {issue_type}")

    def _get_recommendation(self, issue_type: str) -> str:
        """Get recommendation for issue type"""
        recommendations = {
            "any_usage": "Use a specific type instead of 'any'. Consider generics or union types.",
            "unsafe_cast": "Use type guards or type narrowing instead of unsafe casts.",
            "type_ignore": "Fix the underlying type error instead of suppressing it.",
            "null_safety": "Use optional chaining (?.) or nullish coalescing (??) safely.",
        }
        return recommendations.get(issue_type, "Review and fix type safety issue")

    async def analyze_type_safety(
        self, file_path: str, content: str, language: Optional[str] = None
    ) -> List[TypeSafetyIssue]:
        """Analyze a file for type safety issues"""
        issues = []

        # Detect language if not provided
        if not language:
            language = self._detect_language(file_path, content)

        if language == "unknown":
            return issues

        # Pattern-based detection
        pattern_issues = self._detect_pattern_issues(content, file_path, language)
        issues.extend(pattern_issues)

        # AI-based detection for more complex issues
        if self.config.enable_type_analysis and content.strip():
            try:
                prompt = f"""You are a type safety expert. Analyze this code for type safety issues.

File: {file_path}
Language: {language}

Code:
```
{content[:25000]}
```

Identify type safety issues including:
- Use of 'any' or untyped variables
- Unsafe type casts or assertions
- Missing null/undefined checks
- Type narrowing issues
- Generic type misuse
- Implicit any
- Type widening problems

For each issue, provide:
- type: Category (any_usage, unsafe_cast, type_ignore, null_safety, generic_misuse, implicit_any)
- severity: critical, high, medium, or low
- line_number: Line number if applicable
- description: Clear description of the issue
- recommendation: How to fix it

Respond in JSON format:
{{
    "issues": [
        {{
            "type": "...",
            "severity": "...",
            "line_number": ...,
            "description": "...",
            "recommendation": "..."
        }}
    ]
}}"""

                response = await self._call_ai_with_retry(prompt)

                # Parse JSON response
                import json

                json_match = re.search(r"\{[\s\S]*\}", response)
                if json_match:
                    try:
                        result = json.loads(json_match.group(0))
                        for issue_data in result.get("issues", []):
                            # Avoid duplicates from pattern detection
                            line_num = issue_data.get("line_number")
                            if not any(
                                i.line_number == line_num and i.issue_type == issue_data.get("type")
                                for i in issues
                            ):
                                issues.append(
                                    TypeSafetyIssue(
                                        severity=issue_data.get("severity", "medium"),
                                        issue_type=issue_data.get("type", "unknown"),
                                        description=issue_data.get("description", ""),
                                        line_number=line_num,
                                        code_snippet=None,
                                        recommendation=issue_data.get("recommendation", ""),
                                        language=language,
                                    )
                                )
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                print(f"⚠️  Error in AI type safety analysis for {file_path}: {e}")

        return issues
