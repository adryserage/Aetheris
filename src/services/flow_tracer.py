"""
FlowTracer Service

Détecte les appels API et endpoints dans le code source de manière agnostique.
Supporte JavaScript/TypeScript, Dart/Flutter, Python et plusieurs frameworks.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from ..models.user_story_models import APICall, APIEndpoint

# === Patterns de détection par langage ===

# JavaScript/TypeScript - Appels API
JS_API_CALL_PATTERNS = {
    # Fetch API
    "fetch": r"fetch\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
    "fetch_template": r"fetch\s*\(\s*`([^`]+)`",
    # Axios
    "axios_get": r"axios\.get\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
    "axios_post": r"axios\.post\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
    "axios_put": r"axios\.put\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
    "axios_patch": r"axios\.patch\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
    "axios_delete": r"axios\.delete\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
    "axios_request": r"axios\s*\(\s*\{[^}]*url:\s*[`'\"]([^`'\"]+)[`'\"]",
    # jQuery
    "jquery_ajax": r"\$\.ajax\s*\(\s*\{[^}]*url:\s*['\"]([^'\"]+)['\"]",
    "jquery_get": r"\$\.get\s*\(\s*['\"]([^'\"]+)['\"]",
    "jquery_post": r"\$\.post\s*\(\s*['\"]([^'\"]+)['\"]",
    # SWR / React Query
    "use_swr": r"useSWR\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
    "use_query": r"useQuery\s*\([^)]*[`'\"]([^`'\"]+)[`'\"]",
    # tRPC (pattern différent)
    "trpc": r"trpc\.(\w+)\.(\w+)\.(query|mutate|mutation)",
    # Ky
    "ky_get": r"ky\.get\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
    "ky_post": r"ky\.post\s*\(\s*[`'\"]([^`'\"]+)[`'\"]",
}

# Dart/Flutter - Appels API
DART_API_CALL_PATTERNS = {
    # http package
    "http_get": r"http\.get\s*\(\s*Uri\.parse\s*\(\s*['\"]([^'\"]+)['\"]",
    "http_post": r"http\.post\s*\(\s*Uri\.parse\s*\(\s*['\"]([^'\"]+)['\"]",
    "http_put": r"http\.put\s*\(\s*Uri\.parse\s*\(\s*['\"]([^'\"]+)['\"]",
    "http_delete": r"http\.delete\s*\(\s*Uri\.parse\s*\(\s*['\"]([^'\"]+)['\"]",
    # Dio
    "dio_get": r"dio\.get\s*\(\s*['\"]([^'\"]+)['\"]",
    "dio_post": r"dio\.post\s*\(\s*['\"]([^'\"]+)['\"]",
    "dio_put": r"dio\.put\s*\(\s*['\"]([^'\"]+)['\"]",
    "dio_delete": r"dio\.delete\s*\(\s*['\"]([^'\"]+)['\"]",
    "dio_request": r"dio\.request\s*\(\s*['\"]([^'\"]+)['\"]",
    # Retrofit annotations
    "retrofit_get": r"@GET\s*\(\s*['\"]([^'\"]+)['\"]",
    "retrofit_post": r"@POST\s*\(\s*['\"]([^'\"]+)['\"]",
    "retrofit_put": r"@PUT\s*\(\s*['\"]([^'\"]+)['\"]",
    "retrofit_delete": r"@DELETE\s*\(\s*['\"]([^'\"]+)['\"]",
    # Chopper
    "chopper_get": r"@Get\s*\(\s*path:\s*['\"]([^'\"]+)['\"]",
    "chopper_post": r"@Post\s*\(\s*path:\s*['\"]([^'\"]+)['\"]",
}

# Python - Appels API
PYTHON_API_CALL_PATTERNS = {
    # requests
    "requests_get": r"requests\.get\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    "requests_post": r"requests\.post\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    "requests_put": r"requests\.put\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    "requests_patch": r"requests\.patch\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    "requests_delete": r"requests\.delete\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    # httpx
    "httpx_get": r"(?:httpx|client)\.get\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    "httpx_post": r"(?:httpx|client)\.post\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    # aiohttp
    "aiohttp_get": r"session\.get\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    "aiohttp_post": r"session\.post\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
    # urllib
    "urllib_request": r"urllib\.request\.urlopen\s*\(\s*[f]?['\"]([^'\"]+)['\"]",
}

# === Patterns de détection des endpoints ===

# Express.js
EXPRESS_ENDPOINT_PATTERNS = {
    "app_method": r"app\.(get|post|put|patch|delete|all)\s*\(\s*['\"]([^'\"]+)['\"]",
    "router_method": r"router\.(get|post|put|patch|delete|all)\s*\(\s*['\"]([^'\"]+)['\"]",
    "use_route": r"app\.use\s*\(\s*['\"]([^'\"]+)['\"]",
}

# Next.js API Routes
NEXTJS_ENDPOINT_PATTERNS = {
    # Route handlers (app/api/**/route.ts)
    "route_handler": r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\(",
    # Server Actions
    "server_action": r"['\"]use server['\"]",
}

# FastAPI
FASTAPI_ENDPOINT_PATTERNS = {
    "app_decorator": r"@app\.(get|post|put|patch|delete|head|options)\s*\(\s*['\"]([^'\"]+)['\"]",
    "router_decorator": r"@router\.(get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)['\"]",
    "api_route": r"@[\w_]+\.api_route\s*\(\s*['\"]([^'\"]+)['\"]",
}

# Flask
FLASK_ENDPOINT_PATTERNS = {
    "route_decorator": r"@app\.route\s*\(\s*['\"]([^'\"]+)['\"]",
    "blueprint_route": r"@\w+\.route\s*\(\s*['\"]([^'\"]+)['\"]",
    "methods": r"methods\s*=\s*\[([^\]]+)\]",
}

# Django
DJANGO_ENDPOINT_PATTERNS = {
    "path": r"path\s*\(\s*['\"]([^'\"]+)['\"]",
    "re_path": r"re_path\s*\(\s*[r]?['\"]([^'\"]+)['\"]",
    "url": r"url\s*\(\s*[r]?['\"]([^'\"]+)['\"]",
}

# NestJS
NESTJS_ENDPOINT_PATTERNS = {
    "get_decorator": r"@Get\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
    "post_decorator": r"@Post\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
    "put_decorator": r"@Put\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
    "patch_decorator": r"@Patch\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
    "delete_decorator": r"@Delete\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
    "controller": r"@Controller\s*\(\s*['\"]([^'\"]+)['\"]",
}


@dataclass
class FlowTracerResult:
    """Résultat du traçage de flux"""

    api_calls: List[APICall] = field(default_factory=list)
    api_endpoints: List[APIEndpoint] = field(default_factory=list)
    call_to_endpoint_map: Dict[str, str] = field(default_factory=dict)
    orphan_endpoints: List[APIEndpoint] = field(default_factory=list)
    unmatched_calls: List[APICall] = field(default_factory=list)


class FlowTracer:
    """
    Service de traçage des flux API

    Détecte les appels API dans le frontend et les endpoints dans le backend,
    puis établit les correspondances entre eux.
    """

    def __init__(self, root_dir: str, all_files: Optional[List[str]] = None):
        self.root_dir = root_dir
        self.all_files = all_files or []
        self.api_calls: List[APICall] = []
        self.api_endpoints: List[APIEndpoint] = []
        self._file_cache: Dict[str, str] = {}

    def _read_file(self, file_path: str) -> Optional[str]:
        """Lit un fichier et le met en cache"""
        if file_path in self._file_cache:
            return self._file_cache[file_path]

        try:
            full_path = os.path.join(self.root_dir, file_path)
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                self._file_cache[file_path] = content
                return content
        except Exception:
            return None

    def _detect_language(self, file_path: str) -> str:
        """Détecte le langage d'un fichier basé sur son extension"""
        ext = os.path.splitext(file_path)[1].lower()

        language_map = {
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".mjs": "javascript",
            ".cjs": "javascript",
            ".dart": "dart",
            ".py": "python",
            ".vue": "javascript",
            ".svelte": "javascript",
        }

        return language_map.get(ext, "unknown")

    def _detect_framework(self, file_path: str, content: str) -> str:
        """Détecte le framework utilisé dans un fichier"""
        # Next.js API routes
        if "/app/api/" in file_path and file_path.endswith("route.ts"):
            return "nextjs"
        if "/pages/api/" in file_path:
            return "nextjs"

        # Express
        if "express" in content.lower() and ("app." in content or "router." in content):
            return "express"

        # NestJS
        if "@Controller" in content or "@Injectable" in content:
            return "nestjs"

        # FastAPI
        if "@app." in content and "FastAPI" in content:
            return "fastapi"
        if "@router." in content and "APIRouter" in content:
            return "fastapi"

        # Flask
        if "@app.route" in content or "Flask(" in content:
            return "flask"

        # Django
        if "urlpatterns" in content or "django" in content.lower():
            return "django"

        return "unknown"

    def _extract_method_from_pattern_name(self, pattern_name: str) -> str:
        """Extrait la méthode HTTP du nom du pattern"""
        method_keywords = ["get", "post", "put", "patch", "delete", "head", "options"]
        pattern_lower = pattern_name.lower()

        for method in method_keywords:
            if method in pattern_lower:
                return method.upper()

        return "GET"  # Défaut

    def _has_error_handling(self, content: str, line_number: int) -> bool:
        """Vérifie si l'appel API a une gestion d'erreur"""
        lines = content.split("\n")
        start = max(0, line_number - 5)
        end = min(len(lines), line_number + 10)
        context = "\n".join(lines[start:end])

        # Patterns de gestion d'erreur
        error_patterns = [
            r"\.catch\s*\(",
            r"try\s*\{",
            r"\.then\s*\([^)]*\)\s*\.catch",
            r"catch\s*\(",
            r"except\s*:",
            r"except\s+\w+",
            r"onError\s*:",
            r"\.catchError\s*\(",
        ]

        for pattern in error_patterns:
            if re.search(pattern, context):
                return True

        return False

    def _has_loading_state(self, content: str, line_number: int) -> bool:
        """Vérifie si l'appel API a un état de chargement"""
        lines = content.split("\n")
        start = max(0, line_number - 15)
        end = min(len(lines), line_number + 5)
        context = "\n".join(lines[start:end])

        # Patterns d'état de chargement
        loading_patterns = [
            r"isLoading",
            r"loading",
            r"setLoading",
            r"useState.*loading",
            r"pending",
            r"isFetching",
            r"isValidating",
        ]

        for pattern in loading_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True

        return False

    def detect_api_calls_in_file(
        self, file_path: str, content: Optional[str] = None
    ) -> List[APICall]:
        """Détecte tous les appels API dans un fichier"""
        if content is None:
            content = self._read_file(file_path)
            if content is None:
                return []

        language = self._detect_language(file_path)
        calls: List[APICall] = []

        # Sélectionner les patterns selon le langage
        if language in ["javascript", "typescript"]:
            patterns = JS_API_CALL_PATTERNS
        elif language == "dart":
            patterns = DART_API_CALL_PATTERNS
        elif language == "python":
            patterns = PYTHON_API_CALL_PATTERNS
        else:
            return []

        for pattern_name, pattern in patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE):
                # Trouver le numéro de ligne
                line_number = content[: match.start()].count("\n") + 1

                # Extraire l'URL
                url = match.group(1) if match.lastindex is not None and match.lastindex >= 1 else ""

                # Déterminer la méthode HTTP
                method = self._extract_method_from_pattern_name(pattern_name)

                # Déterminer la librairie
                library = pattern_name.split("_")[0]

                call = APICall(
                    file_path=file_path,
                    line_number=line_number,
                    method=method,
                    url_pattern=url,
                    library=library,
                    has_error_handling=self._has_error_handling(content, line_number),
                    has_loading_state=self._has_loading_state(content, line_number),
                )
                calls.append(call)

        return calls

    def detect_endpoints_in_file(
        self, file_path: str, content: Optional[str] = None
    ) -> List[APIEndpoint]:
        """Détecte tous les endpoints API dans un fichier"""
        if content is None:
            content = self._read_file(file_path)
            if content is None:
                return []

        framework = self._detect_framework(file_path, content)
        endpoints: List[APIEndpoint] = []

        # Sélectionner les patterns selon le framework
        if framework == "express":
            patterns = EXPRESS_ENDPOINT_PATTERNS
        elif framework == "nextjs":
            endpoints.extend(self._detect_nextjs_endpoints(file_path, content))
            return endpoints
        elif framework == "fastapi":
            patterns = FASTAPI_ENDPOINT_PATTERNS
        elif framework == "flask":
            patterns = FLASK_ENDPOINT_PATTERNS
        elif framework == "django":
            patterns = DJANGO_ENDPOINT_PATTERNS
        elif framework == "nestjs":
            endpoints.extend(self._detect_nestjs_endpoints(file_path, content))
            return endpoints
        else:
            # Essayer tous les patterns de backend
            for fw_patterns in [
                EXPRESS_ENDPOINT_PATTERNS,
                FASTAPI_ENDPOINT_PATTERNS,
                FLASK_ENDPOINT_PATTERNS,
            ]:
                for pattern_name, pattern in fw_patterns.items():
                    for match in re.finditer(pattern, content, re.MULTILINE):
                        line_number = content[: match.start()].count("\n") + 1

                        if match.lastindex and match.lastindex >= 2:
                            method = match.group(1).upper()
                            path = match.group(2)
                        elif match.lastindex and match.lastindex >= 1:
                            path = match.group(1)
                            method = self._extract_method_from_pattern_name(pattern_name)
                        else:
                            continue

                        endpoint = APIEndpoint(
                            file_path=file_path,
                            line_number=line_number,
                            method=method,
                            path=path,
                            framework="unknown",
                        )
                        endpoints.append(endpoint)
            return endpoints

        for pattern_name, pattern in patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE):
                line_number = content[: match.start()].count("\n") + 1

                # Extraire la méthode et le chemin
                if match.lastindex and match.lastindex >= 2:
                    method = match.group(1).upper()
                    path = match.group(2)
                elif match.lastindex and match.lastindex >= 1:
                    path = match.group(1)
                    method = self._extract_method_from_pattern_name(pattern_name)
                else:
                    continue

                # Détecter si l'endpoint est protégé
                is_protected = self._is_endpoint_protected(content, line_number)

                endpoint = APIEndpoint(
                    file_path=file_path,
                    line_number=line_number,
                    method=method,
                    path=path,
                    framework=framework,
                    is_protected=is_protected,
                )
                endpoints.append(endpoint)

        return endpoints

    def _detect_nextjs_endpoints(self, file_path: str, content: str) -> List[APIEndpoint]:
        """Détecte les endpoints Next.js (route handlers)"""
        endpoints: List[APIEndpoint] = []

        # Extraire le chemin de l'API depuis le chemin du fichier
        # Ex: app/api/users/route.ts -> /api/users
        api_path = ""
        if "/app/api/" in file_path:
            parts = file_path.split("/app/api/")
            if len(parts) > 1:
                path_part = parts[1].replace("/route.ts", "").replace("/route.js", "")
                api_path = "/api/" + path_part
        elif "/pages/api/" in file_path:
            parts = file_path.split("/pages/api/")
            if len(parts) > 1:
                path_part = parts[1].replace(".ts", "").replace(".js", "")
                api_path = "/api/" + path_part

        # Détecter les handlers exportés (GET, POST, etc.)
        handler_pattern = (
            r"export\s+(?:async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*\("
        )
        for match in re.finditer(handler_pattern, content):
            line_number = content[: match.start()].count("\n") + 1
            method = match.group(1)

            endpoint = APIEndpoint(
                file_path=file_path,
                line_number=line_number,
                method=method,
                path=api_path or "/api/unknown",
                handler_name=method,
                framework="nextjs",
            )
            endpoints.append(endpoint)

        return endpoints

    def _detect_nestjs_endpoints(self, file_path: str, content: str) -> List[APIEndpoint]:
        """Détecte les endpoints NestJS"""
        endpoints: List[APIEndpoint] = []

        # Trouver le préfixe du controller
        controller_prefix = ""
        controller_match = re.search(r"@Controller\s*\(\s*['\"]([^'\"]+)['\"]", content)
        if controller_match:
            controller_prefix = "/" + controller_match.group(1).strip("/")

        # Patterns pour les décorateurs de méthodes
        method_patterns = {
            "GET": r"@Get\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
            "POST": r"@Post\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
            "PUT": r"@Put\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
            "PATCH": r"@Patch\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
            "DELETE": r"@Delete\s*\(\s*['\"]?([^'\"]*)['\"]?\s*\)",
        }

        for method, pattern in method_patterns.items():
            for match in re.finditer(pattern, content):
                line_number = content[: match.start()].count("\n") + 1
                route_path = match.group(1) if match.group(1) else ""

                full_path = controller_prefix
                if route_path:
                    full_path = controller_prefix + "/" + route_path.strip("/")

                endpoint = APIEndpoint(
                    file_path=file_path,
                    line_number=line_number,
                    method=method,
                    path=full_path or "/",
                    framework="nestjs",
                )
                endpoints.append(endpoint)

        return endpoints

    def _is_endpoint_protected(self, content: str, line_number: int) -> bool:
        """Vérifie si un endpoint est protégé par authentification"""
        lines = content.split("\n")
        start = max(0, line_number - 10)
        end = min(len(lines), line_number + 2)
        context = "\n".join(lines[start:end])

        # Patterns d'authentification
        auth_patterns = [
            r"@UseGuards",
            r"@Auth",
            r"@Authenticated",
            r"authenticate",
            r"requireAuth",
            r"isAuthenticated",
            r"passport\.",
            r"jwt\.",
            r"auth\(",
            r"protect",
            r"@login_required",
            r"@jwt_required",
            r"Depends\(.*auth",
        ]

        for pattern in auth_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True

        return False

    def trace_all_files(self) -> FlowTracerResult:
        """Trace tous les fichiers du projet"""
        result = FlowTracerResult()

        for file_path in self.all_files:
            # Détecter les appels API
            calls = self.detect_api_calls_in_file(file_path)
            result.api_calls.extend(calls)

            # Détecter les endpoints
            endpoints = self.detect_endpoints_in_file(file_path)
            result.api_endpoints.extend(endpoints)

        # Stocker les résultats
        self.api_calls = result.api_calls
        self.api_endpoints = result.api_endpoints

        # Faire les correspondances
        result = self.match_calls_to_endpoints(result)

        return result

    def match_calls_to_endpoints(self, result: FlowTracerResult) -> FlowTracerResult:
        """Fait correspondre les appels API aux endpoints"""
        matched_endpoints: Set[str] = set()

        for call in result.api_calls:
            matched = False
            url = call.url_pattern

            # Normaliser l'URL
            url_normalized = self._normalize_url(url)

            for endpoint in result.api_endpoints:
                endpoint_normalized = self._normalize_url(endpoint.path)

                # Vérifier la correspondance
                if self._urls_match(url_normalized, endpoint_normalized):
                    if call.method == endpoint.method or call.method == "GET":
                        call.matched_endpoint = endpoint.path
                        result.call_to_endpoint_map[f"{call.file_path}:{call.line_number}"] = (
                            endpoint.path
                        )
                        matched_endpoints.add(f"{endpoint.file_path}:{endpoint.line_number}")
                        matched = True
                        break

            if not matched:
                result.unmatched_calls.append(call)

        # Trouver les endpoints orphelins
        for endpoint in result.api_endpoints:
            key = f"{endpoint.file_path}:{endpoint.line_number}"
            if key not in matched_endpoints:
                result.orphan_endpoints.append(endpoint)

        return result

    def _normalize_url(self, url: str) -> str:
        """Normalise une URL pour la comparaison"""
        # Supprimer le protocole et le domaine si présent
        url = re.sub(r"^https?://[^/]+", "", url)

        # Supprimer les paramètres de query
        url = url.split("?")[0]

        # Normaliser les slashes
        url = "/" + url.strip("/")

        # Remplacer les variables par des placeholders
        # ${var}, :var, {var}
        url = re.sub(r"\$\{[^}]+\}", ":param", url)
        url = re.sub(r"\{[^}]+\}", ":param", url)
        url = re.sub(r":[^/]+", ":param", url)

        return url.lower()

    def _urls_match(self, call_url: str, endpoint_url: str) -> bool:
        """Vérifie si deux URLs correspondent"""
        # Correspondance exacte
        if call_url == endpoint_url:
            return True

        # Correspondance avec paramètres
        call_parts = call_url.split("/")
        endpoint_parts = endpoint_url.split("/")

        if len(call_parts) != len(endpoint_parts):
            return False

        for cp, ep in zip(call_parts, endpoint_parts):
            if cp == ep:
                continue
            if cp == ":param" or ep == ":param":
                continue
            return False

        return True

    def find_orphan_endpoints(self) -> List[APIEndpoint]:
        """Trouve les endpoints qui ne sont jamais appelés"""
        result = self.trace_all_files()
        return result.orphan_endpoints

    def find_unmatched_calls(self) -> List[APICall]:
        """Trouve les appels API sans endpoint correspondant"""
        result = self.trace_all_files()
        return result.unmatched_calls
