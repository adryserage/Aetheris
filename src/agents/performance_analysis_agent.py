"""
Performance Analysis Agent (v2.10)

Detects O(n²) patterns, N+1 queries, memory leaks, blocking async, and other
performance anti-patterns in code.
"""

import re
from typing import List, Optional

from src.agents.base_agent import BaseAgent
from src.core.config import AnalysisConfig
from src.core.progress import ProgressManager
from src.models.data_models import PerformanceIssue


class PerformanceAnalysisAgent(BaseAgent):
    """Agent for detecting performance issues in code"""

    def __init__(self, config: AnalysisConfig, progress_manager: Optional[ProgressManager] = None):
        super().__init__(config, progress_manager)

        # Performance anti-pattern detectors
        self.patterns = {
            "nested_loops": [
                # Python nested for loops
                r"for\s+\w+\s+in\s+.*:\s*\n\s+for\s+\w+\s+in",
                # JavaScript/TypeScript nested loops
                r"for\s*\([^)]+\)\s*\{[^}]*for\s*\([^)]+\)",
                r"\.forEach\([^)]+\)\s*\{[^}]*\.forEach\(",
                r"\.map\([^)]+\)\s*\{[^}]*\.map\(",
            ],
            "n_plus_one": [
                # Database queries in loops
                r"for\s+.*:\s*\n.*(?:query|select|find|get|fetch)\s*\(",
                r"\.forEach\([^)]+\{[^}]*(?:await|\.then)\s*\([^)]*(?:query|find|get|fetch)",
                r"for\s*\([^)]+\)\s*\{[^}]*await\s+.*(?:findOne|findById|query)",
            ],
            "memory_leak": [
                # Event listeners not removed
                r"addEventListener\([^)]+\)",
                r"\.on\s*\([^)]+\)",
                # Unclosed resources
                r"open\s*\([^)]+\)(?!.*close)",
                r"new\s+(?:FileReader|WebSocket|EventSource)\s*\(",
                # Growing arrays in loops
                r"while\s*\([^)]+\)\s*\{[^}]*\.push\(",
            ],
            "blocking_async": [
                # Sync methods in async context
                r"await.*\.readFileSync",
                r"await.*\.writeFileSync",
                r"await.*\.execSync",
                # Sequential awaits that could be parallel
                r"await\s+\w+\s*\(\s*\)\s*\n\s*await\s+\w+\s*\(",
            ],
            "inefficient_string": [
                # String concatenation in loops
                r"for\s+.*:\s*\n.*\+\s*=.*str\(",
                r"for\s*\([^)]+\)\s*\{[^}]*\+=\s*[\"']",
                r"\.join\s*\(\s*[\"'][\"']\s*\)",  # join with empty separator
            ],
            "inefficient_collection": [
                # Repeated list/array operations
                r"if\s+\w+\s+in\s+\w+:",  # O(n) membership test on list
                r"\.indexOf\s*\([^)]+\)\s*!==?\s*-1",
                r"\.includes\s*\([^)]+\)",
                # Sorting in loops
                r"for\s+.*:\s*\n.*\.sort\s*\(",
            ],
        }

    def _detect_language(self, file_path: str) -> str:
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
    ) -> List[PerformanceIssue]:
        """Detect performance issues via patterns"""
        issues = []

        # Check for nested loops (O(n²) complexity)
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip comments
            if (
                stripped.startswith("//")
                or stripped.startswith("#")
                or stripped.startswith("*")
            ):
                continue

            # Check patterns that work on single lines
            for issue_type, patterns in self.patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append(
                            PerformanceIssue(
                                severity=self._get_severity(issue_type),
                                issue_type=issue_type,
                                description=self._get_description(issue_type),
                                line_number=i,
                                code_snippet=line.strip()[:100],
                                recommendation=self._get_recommendation(issue_type),
                                estimated_impact=self._get_impact(issue_type),
                                complexity=self._get_complexity(issue_type),
                            )
                        )

        # Multi-line pattern detection (nested loops, etc.)
        multi_line_issues = self._detect_multiline_patterns(content, lines)
        issues.extend(multi_line_issues)

        return issues

    def _detect_multiline_patterns(
        self, content: str, lines: List[str]
    ) -> List[PerformanceIssue]:
        """Detect patterns that span multiple lines"""
        issues = []

        # Detect nested loops by tracking indentation
        loop_stack = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())

            # Pop loops that we've exited (by indentation)
            while loop_stack and indent <= loop_stack[-1]["indent"]:
                loop_stack.pop()

            # Check for loop start
            if re.match(r"^(for|while)\s+", stripped):
                if loop_stack:
                    # Nested loop detected
                    outer_loop = loop_stack[-1]
                    if not any(
                        issue.issue_type == "nested_loops"
                        and issue.line_number == outer_loop["line"]
                        for issue in issues
                    ):
                        issues.append(
                            PerformanceIssue(
                                severity="high",
                                issue_type="nested_loops",
                                description=(
                                    f"Nested loop detected (lines {outer_loop['line']}-{i}). "
                                    "This may cause O(n²) or worse complexity."
                                ),
                                line_number=outer_loop["line"],
                                code_snippet=lines[outer_loop["line"] - 1].strip()[:100],
                                recommendation=(
                                    "Consider using hash maps, sets, or optimized algorithms "
                                    "to reduce time complexity."
                                ),
                                estimated_impact="Exponential slowdown for large datasets",
                                complexity="O(n²)",
                            )
                        )

                loop_stack.append({"line": i, "indent": indent})

        return issues

    def _get_severity(self, issue_type: str) -> str:
        """Get severity for issue type"""
        severity_map = {
            "nested_loops": "high",
            "n_plus_one": "critical",
            "memory_leak": "high",
            "blocking_async": "medium",
            "inefficient_string": "low",
            "inefficient_collection": "medium",
        }
        return severity_map.get(issue_type, "medium")

    def _get_description(self, issue_type: str) -> str:
        """Get description for issue type"""
        descriptions = {
            "nested_loops": "Nested loop detected - potential O(n²) complexity",
            "n_plus_one": "N+1 query pattern detected - database queries inside loop",
            "memory_leak": "Potential memory leak - unclosed resource or growing collection",
            "blocking_async": "Blocking operation in async context",
            "inefficient_string": "Inefficient string concatenation in loop",
            "inefficient_collection": "Inefficient collection operation",
        }
        return descriptions.get(issue_type, f"Performance issue: {issue_type}")

    def _get_recommendation(self, issue_type: str) -> str:
        """Get recommendation for issue type"""
        recommendations = {
            "nested_loops": (
                "Use hash-based lookups (Set, Map, dict) or optimize algorithm. "
                "Consider batch processing or caching."
            ),
            "n_plus_one": (
                "Use eager loading, batch queries, or DataLoader pattern. "
                "Fetch all related data in one query."
            ),
            "memory_leak": (
                "Ensure resources are properly closed. "
                "Use try-finally, context managers, or cleanup functions."
            ),
            "blocking_async": (
                "Use async versions of I/O operations. "
                "Consider Promise.all() for parallel async operations."
            ),
            "inefficient_string": (
                "Use StringBuilder, join(), or string interpolation instead. "
                "Build list first, then join."
            ),
            "inefficient_collection": (
                "Use Set or dict for O(1) lookups. "
                "Pre-sort data or use binary search if sorted."
            ),
        }
        return recommendations.get(issue_type, "Review and optimize for performance")

    def _get_impact(self, issue_type: str) -> str:
        """Get estimated impact for issue type"""
        impacts = {
            "nested_loops": "10x-100x slower for large datasets",
            "n_plus_one": "N additional database queries",
            "memory_leak": "Memory grows unbounded over time",
            "blocking_async": "Event loop blocked, reduced concurrency",
            "inefficient_string": "O(n²) string operations",
            "inefficient_collection": "O(n) per lookup instead of O(1)",
        }
        return impacts.get(issue_type, "Performance degradation")

    def _get_complexity(self, issue_type: str) -> Optional[str]:
        """Get complexity for issue type"""
        complexities = {
            "nested_loops": "O(n²)",
            "n_plus_one": "O(n) queries",
            "inefficient_string": "O(n²)",
            "inefficient_collection": "O(n)",
        }
        return complexities.get(issue_type)

    async def analyze_performance(
        self, file_path: str, content: str, language: Optional[str] = None
    ) -> List[PerformanceIssue]:
        """Analyze a file for performance issues"""
        issues = []

        # Detect language if not provided
        if not language:
            language = self._detect_language(file_path)

        # Pattern-based detection
        pattern_issues = self._detect_pattern_issues(content, file_path, language)
        issues.extend(pattern_issues)

        # AI-based detection for more complex issues
        if self.config.enable_performance_analysis and content.strip():
            try:
                prompt = f"""You are a performance optimization expert. Analyze this code for performance issues.

File: {file_path}
Language: {language}

Code:
```
{content[:25000]}
```

Identify performance issues including:
- O(n²) or worse algorithmic complexity
- N+1 query patterns (database queries in loops)
- Memory leaks (unclosed resources, growing collections)
- Blocking operations in async contexts
- Inefficient string operations
- Inefficient collection operations
- Missing caching opportunities
- Excessive object creation

For each issue, provide:
- type: Category (nested_loops, n_plus_one, memory_leak, blocking_async, inefficient_algo)
- severity: critical, high, medium, or low
- line_number: Line number if applicable
- description: Clear description of the issue
- recommendation: How to fix it
- complexity: Time complexity (e.g., "O(n²)")

Respond in JSON format:
{{
    "issues": [
        {{
            "type": "...",
            "severity": "...",
            "line_number": ...,
            "description": "...",
            "recommendation": "...",
            "complexity": "..."
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
                                    PerformanceIssue(
                                        severity=issue_data.get("severity", "medium"),
                                        issue_type=issue_data.get("type", "unknown"),
                                        description=issue_data.get("description", ""),
                                        line_number=line_num,
                                        code_snippet=None,
                                        recommendation=issue_data.get("recommendation", ""),
                                        estimated_impact=issue_data.get("impact"),
                                        complexity=issue_data.get("complexity"),
                                    )
                                )
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                print(f"⚠️  Error in AI performance analysis for {file_path}: {e}")

        return issues
