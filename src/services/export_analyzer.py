"""
Analyseur d'exports pour extraire les exports de fichiers
Supporte TypeScript/JavaScript, Python, Dart
"""

import re
from typing import List

from src.models.data_models import FileExport


class ExportAnalyzer:
    """Analyseur d'exports multi-langage"""

    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def extract_exports(self, file_path: str, content: str, language: str) -> List[FileExport]:
        """
        Extrait tous les exports d'un fichier selon son langage.

        Args:
            file_path: Chemin du fichier
            content: Contenu du fichier
            language: Langage détecté

        Returns:
            Liste des exports trouvés
        """
        if language in ["TypeScript", "TypeScript (React)", "JavaScript", "JavaScript (React)"]:
            return self._extract_ts_exports(content)
        elif language == "Python":
            return self._extract_python_exports(content)
        elif language == "Dart":
            return self._extract_dart_exports(content)
        return []

    def _extract_ts_exports(self, content: str) -> List[FileExport]:
        """
        Extrait les exports TypeScript/JavaScript.

        Patterns supportés:
        - export default X
        - export const/let/var X
        - export function X
        - export class X
        - export interface X
        - export type X
        - export enum X
        - export { X, Y as Z }
        - export * from '...'
        - export { X } from '...'
        """
        exports = []

        # Pattern pour les différents types d'exports
        patterns = [
            # export default function/class/const name
            (r"^export\s+default\s+(?:function|class)\s+(\w+)", "default", True),
            # export default anonymous
            (r"^export\s+default\s+(?:function|class)\s*[\(\{]", "default", True),
            # export default expression (sans nom)
            (r"^export\s+default\s+(?!function|class|interface|type|enum)", "default", True),
            # export const/let/var name
            (r"^export\s+(?:const|let|var)\s+(\w+)", "variable", False),
            # export function name
            (r"^export\s+function\s+(\w+)", "function", False),
            # export async function name
            (r"^export\s+async\s+function\s+(\w+)", "function", False),
            # export class name
            (r"^export\s+class\s+(\w+)", "class", False),
            # export abstract class name
            (r"^export\s+abstract\s+class\s+(\w+)", "class", False),
            # export interface name (TypeScript)
            (r"^export\s+interface\s+(\w+)", "type", False),
            # export type name (TypeScript)
            (r"^export\s+type\s+(\w+)", "type", False),
            # export enum name
            (r"^export\s+enum\s+(\w+)", "named", False),
        ]

        for i, line in enumerate(content.split("\n"), 1):
            line_stripped = line.strip()

            # Ignorer les commentaires
            if line_stripped.startswith("//") or line_stripped.startswith("/*"):
                continue

            # Vérifier les patterns simples
            for pattern, export_type, is_default in patterns:
                match = re.match(pattern, line_stripped)
                if match:
                    name = match.group(1) if match.groups() and match.group(1) else "default"
                    exports.append(
                        FileExport(
                            name=name,
                            export_type=export_type,
                            line_number=i,
                            is_default=is_default,
                        )
                    )
                    break

            # export { name, name2 as alias } (exports nommés)
            named_export_match = re.match(r"^export\s*\{([^}]+)\}(?!\s*from)", line_stripped)
            if named_export_match:
                names_str = named_export_match.group(1)
                exports.extend(self._parse_named_exports(names_str, i))
                continue

            # export { ... } from '...' (re-exports nommés)
            reexport_named_match = re.match(
                r"^export\s*\{([^}]+)\}\s*from\s*['\"]([^'\"]+)['\"]", line_stripped
            )
            if reexport_named_match:
                names_str = reexport_named_match.group(1)
                source = reexport_named_match.group(2)
                for exp in self._parse_named_exports(names_str, i):
                    exp.export_type = "reexport"
                    exports.append(exp)
                continue

            # export * from '...' (re-export tout)
            reexport_all_match = re.match(r"^export\s*\*\s*from\s*['\"]([^'\"]+)['\"]", line_stripped)
            if reexport_all_match:
                source = reexport_all_match.group(1)
                exports.append(
                    FileExport(
                        name=f"* from {source}",
                        export_type="reexport",
                        line_number=i,
                        is_default=False,
                    )
                )
                continue

            # export * as name from '...' (namespace re-export)
            reexport_ns_match = re.match(
                r"^export\s*\*\s*as\s+(\w+)\s*from\s*['\"]([^'\"]+)['\"]", line_stripped
            )
            if reexport_ns_match:
                name = reexport_ns_match.group(1)
                exports.append(
                    FileExport(
                        name=name,
                        export_type="reexport",
                        line_number=i,
                        is_default=False,
                    )
                )

        return exports

    def _parse_named_exports(self, names_str: str, line_number: int) -> List[FileExport]:
        """Parse une liste d'exports nommés: { A, B as C, D }"""
        exports = []
        for name_part in names_str.split(","):
            name_part = name_part.strip()
            if not name_part:
                continue

            if " as " in name_part:
                original, alias = name_part.split(" as ", 1)
                exports.append(
                    FileExport(
                        name=original.strip(),
                        export_type="named",
                        line_number=line_number,
                        is_default=False,
                        alias=alias.strip(),
                    )
                )
            else:
                exports.append(
                    FileExport(
                        name=name_part,
                        export_type="named",
                        line_number=line_number,
                        is_default=False,
                    )
                )
        return exports

    def _extract_python_exports(self, content: str) -> List[FileExport]:
        """
        Extrait les exports Python.

        En Python, les "exports" sont:
        - Les éléments listés dans __all__
        - Ou toutes les définitions publiques (sans underscore)
        """
        exports = []

        # Chercher __all__ en premier
        all_match = re.search(r"__all__\s*=\s*\[([^\]]+)\]", content, re.DOTALL)
        if all_match:
            names_str = all_match.group(1)
            for name in re.findall(r"['\"](\w+)['\"]", names_str):
                # Trouver la ligne de __all__
                line_num = content[: all_match.start()].count("\n") + 1
                exports.append(
                    FileExport(
                        name=name,
                        export_type="named",
                        line_number=line_num,
                        is_default=False,
                    )
                )
            return exports

        # Si pas de __all__, extraire les définitions publiques au niveau module
        patterns = [
            (r"^def\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\(", "function"),
            (r"^async\s+def\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\(", "function"),
            (r"^class\s+([a-zA-Z][a-zA-Z0-9_]*)", "class"),
            (r"^([A-Z][A-Z0-9_]*)\s*=", "variable"),  # Constantes UPPER_CASE
        ]

        for i, line in enumerate(content.split("\n"), 1):
            # Ignorer les lignes indentées (pas au niveau module)
            if line.startswith(" ") or line.startswith("\t"):
                continue

            # Ignorer les commentaires
            if line.strip().startswith("#"):
                continue

            for pattern, export_type in patterns:
                match = re.match(pattern, line)
                if match:
                    name = match.group(1)
                    # Ignorer les noms privés (commençant par _)
                    if not name.startswith("_"):
                        exports.append(
                            FileExport(
                                name=name,
                                export_type=export_type,
                                line_number=i,
                                is_default=False,
                            )
                        )
                    break

        return exports

    def _extract_dart_exports(self, content: str) -> List[FileExport]:
        """
        Extrait les exports Dart.

        En Dart, les exports sont:
        - export '...' (re-exports)
        - Classes, fonctions, variables publiques (sans underscore)
        """
        exports = []

        patterns = [
            # export '...' - re-export d'un fichier
            (r"^export\s+['\"]([^'\"]+)['\"]", "reexport"),
            # part of '...' - partie d'une library
            (r"^part\s+of\s+['\"]([^'\"]+)['\"]", "part"),
            # class Name
            (r"^class\s+([A-Z][a-zA-Z0-9_]*)", "class"),
            # abstract class Name
            (r"^abstract\s+class\s+([A-Z][a-zA-Z0-9_]*)", "class"),
            # mixin Name
            (r"^mixin\s+([A-Z][a-zA-Z0-9_]*)", "class"),
            # extension Name
            (r"^extension\s+([A-Z][a-zA-Z0-9_]*)", "class"),
            # enum Name
            (r"^enum\s+([A-Z][a-zA-Z0-9_]*)", "named"),
            # typedef Name
            (r"^typedef\s+([A-Z][a-zA-Z0-9_]*)", "type"),
        ]

        for i, line in enumerate(content.split("\n"), 1):
            line_stripped = line.strip()

            # Ignorer les lignes indentées et commentaires
            if line.startswith(" ") or line.startswith("\t"):
                continue
            if line_stripped.startswith("//") or line_stripped.startswith("/*"):
                continue

            for pattern, export_type in patterns:
                match = re.match(pattern, line_stripped)
                if match:
                    name = match.group(1)
                    # En Dart, _ = privé
                    if not name.startswith("_"):
                        exports.append(
                            FileExport(
                                name=name,
                                export_type=export_type,
                                line_number=i,
                                is_default=False,
                            )
                        )
                    break

            # Fonction top-level: returnType functionName(...) { ou =>
            func_match = re.match(
                r"^(?:Future<[^>]+>|Stream<[^>]+>|void|int|double|String|bool|dynamic|[A-Z][a-zA-Z0-9_<>?]*)\s+"
                r"([a-z][a-zA-Z0-9_]*)\s*(?:<[^>]+>)?\s*\([^)]*\)",
                line_stripped,
            )
            if func_match:
                name = func_match.group(1)
                if not name.startswith("_"):
                    exports.append(
                        FileExport(
                            name=name,
                            export_type="function",
                            line_number=i,
                            is_default=False,
                        )
                    )

            # Variable/constante top-level: final/const type name = ...
            var_match = re.match(
                r"^(?:final|const)\s+(?:[A-Z][a-zA-Z0-9_<>?]*\s+)?([a-zA-Z][a-zA-Z0-9_]*)\s*=",
                line_stripped,
            )
            if var_match:
                name = var_match.group(1)
                if not name.startswith("_"):
                    exports.append(
                        FileExport(
                            name=name,
                            export_type="variable",
                            line_number=i,
                            is_default=False,
                        )
                    )

        return exports
