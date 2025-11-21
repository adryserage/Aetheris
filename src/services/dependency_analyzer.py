"""
Analyseur de dépendances entre fichiers
"""

import os
import re
from typing import List, Dict, Optional

from src.models.data_models import FileDependency


class DependencyAnalyzer:
    """Analyseur de dépendances entre fichiers"""

    def __init__(self, root_dir: str, all_files: List[str]):
        self.root_dir = root_dir
        self.all_files = all_files
        self.file_map = self._build_file_map()

    def _build_file_map(self) -> Dict[str, str]:
        """Construit une map des chemins relatifs vers les chemins absolus"""
        file_map = {}
        for file_path in self.all_files:
            rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
            # Ajouter différentes variantes du chemin
            file_map[rel_path] = file_path
            # Sans extension
            base_path = os.path.splitext(rel_path)[0]
            file_map[base_path] = file_path
            # Avec index (pour Dart/TypeScript)
            if rel_path.endswith("/index"):
                file_map[rel_path.replace("/index", "")] = file_path
        return file_map

    def _resolve_import_path(
        self, file_path: str, import_path: str, language: str
    ) -> Optional[str]:
        """Résout un chemin d'import relatif vers un chemin de fichier absolu"""
        file_dir = os.path.dirname(file_path)
        rel_file_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
        rel_file_dir = os.path.dirname(rel_file_path) if os.path.dirname(rel_file_path) else "."

        # Nettoyer le chemin d'import
        clean_import = import_path.strip().strip('"').strip("'")

        # Résoudre selon le langage
        if language in ["TypeScript", "TypeScript (React)", "JavaScript", "JavaScript (React)"]:
            return self._resolve_ts_import(rel_file_dir, clean_import)
        elif language == "Dart":
            return self._resolve_dart_import(rel_file_dir, clean_import)
        elif language == "Python":
            return self._resolve_python_import(rel_file_dir, clean_import)

        return None

    def _resolve_ts_import(self, from_dir: str, import_path: str) -> Optional[str]:
        """Résout un import TypeScript/JavaScript"""
        # Imports relatifs
        if import_path.startswith("./") or import_path.startswith("../"):
            target_path = os.path.normpath(os.path.join(from_dir, import_path)).replace("\\", "/")
        # Imports absolus avec alias (ex: @/components)
        elif import_path.startswith("@/"):
            # Chercher dans tous les dossiers src du projet (détection automatique)
            alias_path = import_path.replace("@/", "")
            # Chercher dans tous les fichiers pour trouver les dossiers src
            for mapped_path in self.file_map.keys():
                if "/src/" in mapped_path or mapped_path.startswith("src/"):
                    # Extraire le préfixe du dossier src
                    if "/src/" in mapped_path:
                        src_prefix = mapped_path.split("/src/")[0] + "/src/"
                    else:
                        src_prefix = "src/"
                    test_path = src_prefix + alias_path
                    # Essayer différentes extensions
                    for ext in [".ts", ".tsx", ".js", ".jsx", ""]:
                        full_path = test_path + ext
                        if full_path in self.file_map:
                            return self.file_map[full_path]
                        # Essayer avec /index
                        index_path = os.path.join(test_path, "index" + ext).replace("\\", "/")
                        if index_path in self.file_map:
                            return self.file_map[index_path]
            return None
        else:
            # Package npm ou alias non reconnu
            return None  # On ignore les packages externes

        # Essayer différentes extensions
        extensions = [".ts", ".tsx", ".js", ".jsx", ""]
        for ext in extensions:
            test_path = target_path + ext
            if test_path in self.file_map:
                return self.file_map[test_path]
            # Essayer avec /index
            test_path_index = os.path.join(target_path, "index" + ext).replace("\\", "/")
            if test_path_index in self.file_map:
                return self.file_map[test_path_index]

        return None

    def _resolve_dart_import(self, from_dir: str, import_path: str) -> Optional[str]:
        """Résout un import Dart"""
        # Imports package: (packages externes)
        if import_path.startswith("package:"):
            return None  # Packages externes

        # Imports relatifs
        if import_path.startswith("./") or import_path.startswith("../"):
            target_path = os.path.normpath(os.path.join(from_dir, import_path)).replace("\\", "/")
        else:
            # Import absolu depuis lib/ - chercher dans tous les packages (détection automatique)
            target_path = None
            # Détecter automatiquement les packages avec lib/
            if "/lib/" in from_dir:
                # Extraire le préfixe du package
                package_prefix = from_dir.split("/lib/")[0] + "/lib/"
                target_path = package_prefix + import_path
            else:
                # Chercher dans tous les fichiers pour trouver les packages
                for mapped_path in self.file_map.keys():
                    if "/lib/" in mapped_path:
                        package_prefix = mapped_path.split("/lib/")[0] + "/lib/"
                        if from_dir.startswith(package_prefix.replace("/lib/", "/")):  # type: ignore
                            target_path = package_prefix + import_path
                            break

            if not target_path:
                return None

        # Essayer avec .dart
        test_path = target_path + ".dart"
        if test_path in self.file_map:
            return self.file_map[test_path]

        # Essayer sans extension (pour les dossiers avec fichier barrel)
        if target_path in self.file_map:
            return self.file_map[target_path]

        return None

    def _resolve_python_import(self, from_dir: str, import_path: str) -> Optional[str]:
        """Résout un import Python"""
        # Imports relatifs
        if import_path.startswith("."):
            parts = import_path.split(".")
            target_path = from_dir
            for part in parts:
                if part == "":
                    continue
                elif part == "..":
                    target_path = os.path.dirname(target_path)
                else:
                    target_path = os.path.join(target_path, part)
            target_path = target_path.replace("\\", "/")
        else:
            # Import absolu
            target_path = import_path.replace(".", "/")

        # Essayer avec .py
        test_path = target_path + ".py"
        if test_path in self.file_map:
            return self.file_map[test_path]
        # Essayer avec __init__.py
        test_path_init = os.path.join(target_path, "__init__.py").replace("\\", "/")
        if test_path_init in self.file_map:
            return self.file_map[test_path_init]

        return None

    def extract_dependencies(
        self, file_path: str, content: str, language: str
    ) -> List[FileDependency]:
        """Extrait les dépendances d'un fichier"""
        dependencies = []

        if language in ["TypeScript", "TypeScript (React)", "JavaScript", "JavaScript (React)"]:
            dependencies = self._extract_ts_imports(file_path, content, language)
        elif language == "Dart":
            dependencies = self._extract_dart_imports(file_path, content, language)
        elif language == "Python":
            dependencies = self._extract_python_imports(file_path, content, language)

        # Résoudre les chemins et vérifier l'existence
        for dep in dependencies:
            resolved = self._resolve_import_path(file_path, dep.import_path, language)
            if resolved:
                dep.resolved_path = resolved
                dep.exists = True
            else:
                # Vérifier si c'est un package externe (à ignorer)
                if not (
                    dep.import_path.startswith("@/")
                    or dep.import_path.startswith("package:")
                    or not (dep.import_path.startswith("./") or dep.import_path.startswith("../"))
                ):
                    # Probablement un package externe, on ignore
                    dep.exists = True  # On considère comme valide

        return dependencies

    def _extract_ts_imports(
        self, file_path: str, content: str, language: str
    ) -> List[FileDependency]:
        """Extrait les imports TypeScript/JavaScript"""
        dependencies = []

        # Patterns pour différents types d'imports
        patterns = [
            # import ... from '...'
            (
                r"import\s+(?:(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)(?:\s*,\s*(?:\{[^}]*\}|\*\s+as\s+\w+|\w+))*\s+from\s+)?['\"]([^'\"]+)['\"]",
                "import",
            ),
            # require('...')
            (r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", "require"),
            # import('...')
            (r"import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", "dynamic_import"),
        ]

        for i, line in enumerate(content.split("\n"), 1):
            for pattern, import_type in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    import_path = match.group(1) if match.groups() else match.group(0)
                    # Ignorer les packages npm
                    if not import_path.startswith(".") and not import_path.startswith("@/"):
                        continue
                    dependencies.append(
                        FileDependency(
                            import_path=import_path, line_number=i, import_type=import_type
                        )
                    )

        return dependencies

    def _extract_dart_imports(
        self, file_path: str, content: str, language: str
    ) -> List[FileDependency]:
        """Extrait les imports Dart"""
        dependencies = []

        # Pattern: import '...' ou import '...' as ... ou import '...' show/hide ...
        pattern = r"import\s+['\"]([^'\"]+)['\"]"

        for i, line in enumerate(content.split("\n"), 1):
            matches = re.finditer(pattern, line)
            for match in matches:
                import_path = match.group(1)
                dependencies.append(
                    FileDependency(import_path=import_path, line_number=i, import_type="import")
                )

        return dependencies

    def _extract_python_imports(
        self, file_path: str, content: str, language: str
    ) -> List[FileDependency]:
        """Extrait les imports Python"""
        dependencies = []

        # Patterns pour imports Python
        patterns = [
            # import ...
            (r"^import\s+([a-zA-Z_][a-zA-Z0-9_.]*)", "import"),
            # from ... import ...
            (r"^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import", "from_import"),
        ]

        for i, line in enumerate(content.split("\n"), 1):
            # Ignorer les commentaires
            if line.strip().startswith("#"):
                continue
            for pattern, import_type in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    import_path = match.group(1)
                    # Ignorer les imports de la bibliothèque standard
                    if not import_path.startswith(".") and import_path.split(".")[0] in [
                        "os",
                        "sys",
                        "json",
                        "re",
                        "asyncio",
                        "pathlib",
                        "datetime",
                        "typing",
                        "dataclasses",
                        "collections",
                    ]:
                        continue
                    dependencies.append(
                        FileDependency(
                            import_path=import_path, line_number=i, import_type=import_type
                        )
                    )

        return dependencies

    def detect_circular_dependencies(
        self, dependencies_map: Dict[str, List[FileDependency]]
    ) -> List[List[str]]:
        """Détecte les dépendances circulaires"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(file_path: str, path: List[str]):
            if file_path in rec_stack:
                # Cycle détecté
                cycle_start = path.index(file_path)
                cycle = path[cycle_start:] + [file_path]
                cycles.append(cycle)
                return
            if file_path in visited:
                return

            visited.add(file_path)
            rec_stack.add(file_path)

            if file_path in dependencies_map:
                for dep in dependencies_map[file_path]:
                    if dep.resolved_path and dep.exists:
                        dfs(dep.resolved_path, path + [file_path])

            rec_stack.remove(file_path)

        for file_path in dependencies_map:
            if file_path not in visited:
                dfs(file_path, [])

        return cycles
