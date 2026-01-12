"""
API Contract Analysis Agent (v2.10)

Detects REST violations, breaking changes, undocumented endpoints,
and API design anti-patterns.
"""

import re
from typing import List, Optional

from src.agents.base_agent import BaseAgent
from src.core.config import AnalysisConfig
from src.core.progress import ProgressManager
from src.models.data_models import APIContractViolation


class APIContractAgent(BaseAgent):
    """Agent for detecting API contract violations"""

    def __init__(self, config: AnalysisConfig, progress_manager: Optional[ProgressManager] = None):
        super().__init__(config, progress_manager)

        # REST principles and violations
        self.http_method_patterns = {
            "get_with_body": [
                r"@Get\s*\([^)]*\)[^{]*\{[^}]*@Body\b",
                r"\.get\s*\([^)]*,\s*\{[^}]*body\s*:",
                r"app\.get\s*\([^)]+,.*body\s*:",
                r"@api\.route\s*\([^)]*,\s*methods\s*=.*GET.*\)[^:]*:[^}]*request\.(?:json|data)",
            ],
            "delete_with_body": [
                r"@Delete\s*\([^)]*\)[^{]*\{[^}]*@Body\b",
                r"\.delete\s*\([^)]*,\s*\{[^}]*body\s*:",
            ],
            "post_for_retrieval": [
                r"@Post\s*\([^)]*get|list|fetch|search[^)]*\)",
                r"\.post\s*\([^)]*get|list|fetch|search",
            ],
        }

        self.naming_patterns = {
            "verb_in_url": [
                r"['\"]\/\w*(?:get|create|update|delete|fetch|add|remove)\w*['\"]",
                r"@\w+Mapping\s*\([^)]*['\"].*(?:get|create|update|delete).*['\"]",
            ],
            "inconsistent_pluralization": [
                r"['\"]\/users?\/[^/]+\/user['\"]",  # /users/:id/user
                r"['\"]\/items?\/[^/]+\/item['\"]",  # /items/:id/item
            ],
            "non_restful_endpoint": [
                r"['\"]\/\w+Actions['\"]",
                r"['\"]\/doSomething['\"]",
                r"['\"]\/process\w+['\"]",
            ],
        }

        self.breaking_change_patterns = {
            "removed_field": [
                r"\/\/\s*(?:REMOVED|DEPRECATED):\s*\w+",
                r"#\s*(?:REMOVED|DEPRECATED):\s*\w+",
            ],
            "type_change": [
                r":\s*string\s*\/\/\s*was:\s*number",
                r":\s*number\s*\/\/\s*was:\s*string",
            ],
            "required_field_added": [
                r"@Required\s*\(\s*\)\s*\/\/\s*NEW",
                r"required\s*=\s*True\s*#\s*NEW",
            ],
        }

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language/framework from file path"""
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
        return "unknown"

    def _is_api_file(self, file_path: str, content: str) -> bool:
        """Check if file likely contains API definitions"""
        api_indicators = [
            r"@Controller|@RestController|@RequestMapping",
            r"app\.(get|post|put|delete|patch)\s*\(",
            r"@app\.route|@api\.route|@router\.",
            r"@Get|@Post|@Put|@Delete|@Patch",
            r"express\(\)|fastify\(\)|Hono\(\)",
            r"class.*APIView|class.*ViewSet",
            r"func.*http\.(Request|ResponseWriter)",
        ]

        for indicator in api_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                return True

        # Check file path
        api_paths = ["controller", "route", "endpoint", "api", "handler"]
        return any(path in file_path.lower() for path in api_paths)

    def _detect_pattern_issues(
        self, content: str, file_path: str, language: str
    ) -> List[APIContractViolation]:
        """Detect API contract violations via patterns"""
        issues = []

        # HTTP method violations
        for violation_type, patterns in self.http_method_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    line_number = content[: match.start()].count("\n") + 1
                    issues.append(
                        APIContractViolation(
                            severity="high" if "get" in violation_type else "medium",
                            violation_type="http_method",
                            description=self._get_http_method_description(violation_type),
                            endpoint=self._extract_endpoint(match.group(0)),
                            line_number=line_number,
                            code_snippet=match.group(0)[:100],
                            recommendation=self._get_http_method_recommendation(violation_type),
                            rest_principle=self._get_rest_principle(violation_type),
                        )
                    )

        # Naming violations
        for violation_type, patterns in self.naming_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_number = content[: match.start()].count("\n") + 1
                    issues.append(
                        APIContractViolation(
                            severity="low",
                            violation_type="rest_naming",
                            description=self._get_naming_description(violation_type),
                            endpoint=self._extract_endpoint(match.group(0)),
                            line_number=line_number,
                            code_snippet=match.group(0)[:100],
                            recommendation=self._get_naming_recommendation(violation_type),
                            rest_principle="REST naming conventions",
                        )
                    )

        # Breaking change indicators
        for violation_type, patterns in self.breaking_change_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    line_number = content[: match.start()].count("\n") + 1
                    issues.append(
                        APIContractViolation(
                            severity="critical",
                            violation_type="breaking_change",
                            description=f"Potential breaking change: {violation_type.replace('_', ' ')}",
                            line_number=line_number,
                            code_snippet=match.group(0)[:100],
                            recommendation=(
                                "Document breaking changes. Consider versioning the API or "
                                "deprecation period before removal."
                            ),
                            rest_principle="API versioning and backwards compatibility",
                        )
                    )

        return issues

    def _extract_endpoint(self, text: str) -> Optional[str]:
        """Extract endpoint path from code snippet"""
        match = re.search(r"['\"](/[a-zA-Z0-9/:_-]+)['\"]", text)
        return match.group(1) if match else None

    def _get_http_method_description(self, violation_type: str) -> str:
        """Get description for HTTP method violation"""
        descriptions = {
            "get_with_body": "GET request with body. GET requests should not have a request body.",
            "delete_with_body": "DELETE request with body. Consider using POST if body is required.",
            "post_for_retrieval": "POST used for data retrieval. Use GET for idempotent queries.",
        }
        return descriptions.get(violation_type, f"HTTP method violation: {violation_type}")

    def _get_http_method_recommendation(self, violation_type: str) -> str:
        """Get recommendation for HTTP method violation"""
        recommendations = {
            "get_with_body": "Move filter parameters to query string. Use POST if complex filtering needed.",
            "delete_with_body": "Use request parameters or path variables. Consider POST with action if complex.",
            "post_for_retrieval": "Use GET with query parameters for retrieval operations.",
        }
        return recommendations.get(violation_type, "Review HTTP method usage")

    def _get_rest_principle(self, violation_type: str) -> str:
        """Get REST principle for violation"""
        principles = {
            "get_with_body": "GET requests must be safe and idempotent (RFC 7231)",
            "delete_with_body": "DELETE requests should identify resource via URI (RFC 7231)",
            "post_for_retrieval": "GET is the standard method for resource retrieval",
        }
        return principles.get(violation_type, "REST API design principles")

    def _get_naming_description(self, violation_type: str) -> str:
        """Get description for naming violation"""
        descriptions = {
            "verb_in_url": "Verb in URL path. RESTful URLs should be noun-based.",
            "inconsistent_pluralization": "Inconsistent pluralization in URL hierarchy.",
            "non_restful_endpoint": "Non-RESTful endpoint name detected.",
        }
        return descriptions.get(violation_type, f"Naming violation: {violation_type}")

    def _get_naming_recommendation(self, violation_type: str) -> str:
        """Get recommendation for naming violation"""
        recommendations = {
            "verb_in_url": "Use HTTP methods (GET, POST, PUT, DELETE) to indicate action.",
            "inconsistent_pluralization": "Use consistent pluralization (prefer plural for collections).",
            "non_restful_endpoint": "Restructure as resource-based endpoint.",
        }
        return recommendations.get(violation_type, "Follow REST naming conventions")

    async def analyze_api_contract(
        self, file_path: str, content: str, language: Optional[str] = None
    ) -> List[APIContractViolation]:
        """Analyze a file for API contract violations"""
        issues: List[APIContractViolation] = []

        # Detect language if not provided
        if not language:
            language = self._detect_language(file_path)

        # Check if file contains API definitions
        if not self._is_api_file(file_path, content):
            return issues

        # Pattern-based detection
        pattern_issues = self._detect_pattern_issues(content, file_path, language)
        issues.extend(pattern_issues)

        # AI-based detection for more complex issues
        if self.config.enable_api_contract_analysis and content.strip():
            try:
                prompt = f"""You are a REST API design expert. Analyze this code for API contract violations.

File: {file_path}
Language: {language}

Code:
```
{content[:25000]}
```

Identify API contract issues including:
- HTTP method violations (GET with body, wrong method for operation)
- RESTful naming violations (verbs in URLs, inconsistent naming)
- Breaking changes (removed fields, type changes, new required fields)
- Undocumented endpoints (missing OpenAPI/Swagger annotations)
- Inconsistent response formats
- Missing error handling
- Security issues (missing auth, exposed sensitive data)

For each issue, provide:
- type: Category (http_method, rest_naming, breaking_change, undocumented, security)
- severity: critical, high, medium, or low
- endpoint: The endpoint path if applicable
- line_number: Line number if applicable
- description: Clear description of the issue
- recommendation: How to fix it

Respond in JSON format:
{{
    "issues": [
        {{
            "type": "...",
            "severity": "...",
            "endpoint": "...",
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
                            line_num = issue_data.get("line_number")
                            if not any(
                                i.line_number == line_num
                                and i.violation_type == issue_data.get("type")
                                for i in issues
                            ):
                                issues.append(
                                    APIContractViolation(
                                        severity=issue_data.get("severity", "medium"),
                                        violation_type=issue_data.get("type", "unknown"),
                                        description=issue_data.get("description", ""),
                                        endpoint=issue_data.get("endpoint"),
                                        line_number=line_num,
                                        code_snippet=None,
                                        recommendation=issue_data.get("recommendation", ""),
                                        rest_principle=None,
                                    )
                                )
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                print(f"⚠️  Error in AI API contract analysis for {file_path}: {e}")

        return issues
