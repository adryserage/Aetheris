"""
Orchestrateur principal du système d'analyse de code.
"""

import os
import asyncio
import pathlib
import re
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

from pathspec import PathSpec

from src.core.config import AnalysisConfig
from src.core.logger import log_print
from src.models.data_models import FileAnalysis
from src.services.code_generator import CodeGenerator
from src.services.documentation_searcher import DocumentationSearcher
from src.services.dependency_analyzer import DependencyAnalyzer
from src.agents.code_analysis_expert import CodeAnalysisExpert
from src.agents.architect_analysis_agent import ArchitectAnalysisAgent
from src.agents.security_analysis_agent import SecurityAnalysisAgent
from src.agents.code_metrics_agent import CodeMetricsAgent
from src.agents.dependency_vulnerability_agent import DependencyVulnerabilityAgent
from src.agents.quality_assurance_agent import QualityAssuranceAgent


def sanitize_markdown(text: str) -> str:
    """
    Sanitise le texte Markdown pour prévenir les injections XSS.
    Échappe les caractères spéciaux dans les blocs de code et les liens.
    """
    if not text:
        return ""

    # Échapper les caractères HTML dangereux dans les blocs de code inline
    # On préserve les blocs de code (```) mais on échappe le contenu entre backticks simples
    import html

    # Séparer le texte en parties (code blocks, inline code, texte normal)
    parts = []
    i = 0
    in_code_block = False
    in_inline_code = False
    current_part = ""

    while i < len(text):
        # Détecter les blocs de code (```)
        if i + 2 < len(text) and text[i : i + 3] == "```":
            if current_part:
                if in_inline_code:
                    # Échapper le contenu du code inline
                    parts.append(html.escape(current_part))
                else:
                    parts.append(current_part)
                current_part = ""
            in_code_block = not in_code_block
            parts.append("```")
            i += 3
            continue

        # Détecter le code inline (`)
        if not in_code_block and text[i] == "`" and (i == 0 or text[i - 1] != "`"):
            if current_part:
                if in_inline_code:
                    # Échapper le contenu du code inline
                    parts.append(html.escape(current_part))
                else:
                    parts.append(current_part)
                current_part = ""
            in_inline_code = not in_inline_code
            parts.append("`")
            i += 1
            continue

        # Détecter les liens markdown [text](url) - échapper l'URL
        if (
            not in_code_block
            and not in_inline_code
            and text[i] == "]"
            and i + 1 < len(text)
            and text[i + 1] == "("
        ):
            # Trouver le début du lien
            link_start = text.rfind("[", 0, i)
            if link_start != -1:
                # Trouver la fin de l'URL
                url_end = text.find(")", i + 2)
                if url_end != -1:
                    url = text[i + 2 : url_end]
                    # Échapper l'URL si elle contient des caractères dangereux
                    if any(char in url for char in ["<", ">", '"', "'", "javascript:", "data:"]):
                        url = html.escape(url)
                        text = text[: i + 2] + url + text[url_end:]
                        i = url_end + 1
                        continue

        current_part += text[i]
        i += 1

    # Ajouter la dernière partie
    if current_part:
        if in_inline_code:
            parts.append(html.escape(current_part))
        else:
            parts.append(current_part)

    result = "".join(parts)

    # Échapper les balises HTML dangereuses en dehors des blocs de code
    # (mais préserver les balises Markdown valides)
    dangerous_tags = ["<script", "<iframe", "<object", "<embed", "<link", "<meta"]
    for tag in dangerous_tags:
        if tag in result.lower():
            # Remplacer par la version échappée
            result = result.replace(tag, html.escape(tag))

    return result


class CodeAnalyzer:
    """Orchestrateur principal du système d'analyse"""

    def __init__(self, config: AnalysisConfig, files_to_analyze: Optional[List[str]] = None):
        self.config = config
        self.files_to_analyze = (
            files_to_analyze  # Liste optionnelle de fichiers spécifiques à analyser
        )
        self.dependency_analyzer = None  # Sera initialisé après le scan des fichiers
        self.doc_searcher = DocumentationSearcher(config) if config.enable_web_search else None
        self.code_generator = CodeGenerator(config) if config.enable_code_generation else None
        self.cae = CodeAnalysisExpert(
            config, self.dependency_analyzer, self.doc_searcher, self.code_generator
        )
        self.aaa = ArchitectAnalysisAgent(config, self.doc_searcher)
        # Nouveaux agents
        self.ssa = (
            SecurityAnalysisAgent(config, self.doc_searcher)
            if config.enable_security_analysis
            else None
        )
        self.cma = CodeMetricsAgent(config) if config.enable_metrics_analysis else None
        self.dva = (
            DependencyVulnerabilityAgent(config, config.root_dir)
            if config.enable_dependency_vulnerability
            else None
        )
        self.qaa = QualityAssuranceAgent(config, self.doc_searcher)  # Agent d'assurance qualité
        self.gitignore_spec = None

    def load_gitignore(self) -> PathSpec:
        """Charge les règles .gitignore"""
        gitignore_path = os.path.join(self.config.root_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                patterns = f.read().splitlines()
            return PathSpec.from_lines("gitwildmatch", patterns)
        return PathSpec.from_lines("gitwildmatch", [])

    def should_analyze(self, file_path: str) -> bool:
        """Vérifie si un fichier doit être analysé - UNIQUEMENT les fichiers source, pas les fichiers générés/compilés"""
        if self.gitignore_spec is None:
            self.gitignore_spec = self.load_gitignore()

        relative_path = os.path.relpath(file_path, self.config.root_dir)
        # Normaliser les séparateurs pour Windows
        relative_path = relative_path.replace("\\", "/")

        # Dossiers à exclure explicitement (même s'ils ne sont pas dans .gitignore)
        # Tous les dossiers de build, compilation, génération, cache, etc.
        excluded_dirs = {
            # Environnements Python
            ".venv",
            "venv",
            "env",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            # Node.js
            "node_modules",
            ".next",
            ".nuxt",
            ".output",
            ".cache",
            ".turbo",
            # Build/Dist
            "build",
            "dist",
            "out",
            "target",
            "bin",
            "obj",
            ".build",
            # Flutter/Dart
            ".dart_tool",
            ".flutter-plugins",
            ".flutter-plugins-dependencies",
            # IDE/Editeurs
            ".git",
            ".vscode",
            ".idea",
            ".cursor",
            ".claude",
            ".windsurf",
            ".vs",
            # Flutter platform-specific builds
            "android/build",
            "android/app/build",
            "android/.gradle",
            "ios/Pods",
            "ios/.symlinks",
            "ios/build",
            "ios/DerivedData",
            "macos/Flutter/ephemeral",
            "windows/flutter/ephemeral",
            "linux/flutter/ephemeral",
            "web",
            # Coverage et tests
            "coverage",
            ".nyc_output",
            ".coverage",
            "htmlcov",
            # Autres
            ".gradle",
            ".mvn",
            ".sass-cache",
            ".parcel-cache",
            # Fichiers générés par les outils
            "generated",
            ".generated",
            "gen",
            ".gen",
        }

        # Vérifier si le chemin contient un dossier exclu
        path_parts = relative_path.split("/")
        for part in path_parts:
            if part in excluded_dirs:
                return False
            # Exclure tous les dossiers cachés sauf .github
            if part.startswith(".") and part != "." and part != ".." and part != ".github":
                return False
            # Exclure les dossiers de build même s'ils ne sont pas dans la liste
            if part in {"build", "dist", "out", "target", "bin", "obj", "generated"}:
                return False

        # Vérifier .gitignore
        if self.gitignore_spec.match_file(relative_path):
            return False

        # Exclure les fichiers générés/compilés par leurs noms/extensions
        filename = os.path.basename(file_path)
        ext = pathlib.Path(file_path).suffix.lower()

        # Fichiers générés TypeScript/JavaScript
        if ext == ".d.ts":  # Fichiers de déclaration TypeScript générés
            return False
        if ext == ".js" and filename.endswith(".min.js"):  # Fichiers minifiés
            return False
        if (
            ext == ".js" and "/node_modules/" in relative_path
        ):  # Déjà exclu mais double vérification
            return False

        # Fichiers générés Dart/Flutter
        generated_dart_patterns = [
            ".g.dart",  # Code généré (freezed, json_serializable, etc.)
            ".freezed.dart",  # Freezed
            ".pb.dart",  # Protobuf
            ".gr.dart",  # gRPC
            ".mocks.dart",  # Mockito
            ".config.dart",  # Build config
        ]
        for pattern in generated_dart_patterns:
            if filename.endswith(pattern):
                return False

        # Fichiers générés Python
        if filename.endswith(".pyc") or filename.endswith(".pyo"):
            return False
        if "__pycache__" in relative_path:
            return False

        # Fichiers de lock (trop volumineux et non pertinents)
        lock_files = {
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "poetry.lock",
            "Pipfile.lock",
            "composer.lock",
            "pubspec.lock",
            "Gemfile.lock",
            "Cargo.lock",
        }
        if filename in lock_files:
            return False

        # Fichiers minifiés/bundlés
        minified_patterns = [
            ".min.js",
            ".min.css",
            ".bundle.js",
            ".chunk.js",
            ".production.js",
            ".production.css",
        ]
        for pattern in minified_patterns:
            if filename.endswith(pattern):
                return False

        # Autoriser tous les fichiers de code source, peu importe leur emplacement
        # On accepte tous les fichiers de code sauf ceux dans les dossiers exclus
        # Autoriser les fichiers de configuration importants
        allowed_config_patterns = [
            "package.json",
            "pubspec.yaml",
            "tsconfig.json",
            "next.config",
            "tailwind.config",
            "vercel.json",
            "README.md",
            ".gitignore",
            "analysis_options.yaml",
            "pyproject.toml",
            "requirements.txt",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
        ]

        filename_lower = filename.lower()
        is_config_file = any(pattern in filename_lower for pattern in allowed_config_patterns)

        # Autoriser les fichiers dans .github (workflows CI/CD)
        if relative_path.startswith(".github/"):
            pass  # Autoriser
        elif is_config_file:
            pass  # Autoriser les fichiers de config
        # Sinon, on continue - on accepte tous les fichiers de code source

        # Exclure les fichiers binaires et trop volumineux
        try:
            size = os.path.getsize(file_path)
            if size > 1_000_000:  # > 1MB
                return False
        except:
            return False

        # Inclure seulement les fichiers de code source pertinents
        code_extensions = {
            ".dart",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".py",
            ".java",
            ".kt",
            ".swift",
            ".go",
            ".rs",
            ".cpp",
            ".c",
            ".h",
            ".cs",
            ".php",
            ".rb",
            ".sh",
            ".yaml",
            ".yml",
            ".json",
            ".xml",
            ".md",
            ".sql",
            ".html",
            ".css",
            ".scss",
            ".sass",
            ".vue",
            ".svelte",
        }

        # Exclure les fichiers .js qui sont probablement générés depuis .ts
        if ext == ".js":
            # Vérifier s'il existe un fichier .ts correspondant
            ts_file = file_path.replace(".js", ".ts").replace(".jsx", ".tsx")
            if os.path.exists(ts_file):
                # Si un .ts existe, le .js est probablement généré
                return False

        return ext in code_extensions or ext == ""

    def scan_files(self) -> List[str]:
        """Scanne tous les fichiers à analyser"""
        # Si on analyse uniquement les fichiers modifiés, utiliser la liste fournie
        if self.config.analyze_changed_files_only and self.config.changed_files:
            files = []
            for file_path in self.config.changed_files:
                # Normaliser le chemin
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.config.root_dir, file_path)
                else:
                    # Si c'est un chemin absolu, le convertir en relatif
                    try:
                        file_path = os.path.relpath(file_path, self.config.root_dir)
                        file_path = os.path.join(self.config.root_dir, file_path)
                    except ValueError:
                        # Si le fichier n'est pas dans root_dir, l'ignorer
                        continue

                # Vérifier que le fichier existe et doit être analysé
                if os.path.exists(file_path) and self.should_analyze(file_path):
                    files.append(file_path)

            return sorted(files)

        # Sinon, scan complet
        files = []

        # Dossiers à exclure complètement du scan
        excluded_dirs = {
            ".git",
            ".venv",
            "venv",
            "env",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".dart_tool",
            "build",
            "dist",
            ".next",
            ".vscode",
            ".idea",
            ".cursor",
            ".claude",
            ".windsurf",
            "android/build",
            "ios/Pods",
            "ios/.symlinks",
            "macos/Flutter/ephemeral",
            "windows/flutter/ephemeral",
            "linux/flutter/ephemeral",
            "coverage",
            ".nyc_output",
            "helpeur_client/build",
            "helpeur_entrepreneur/build",
            "helpeur_client/android/build",
            "helpeur_entrepreneur/android/build",
        }

        for root, dirs, filenames in os.walk(self.config.root_dir):
            # Filtrer les dossiers à exclure
            dirs[:] = [
                d
                for d in dirs
                if d not in excluded_dirs and not d.startswith(".") or d in {".github"}
            ]

            # Vérifier si le dossier racine actuel est exclu
            rel_root = os.path.relpath(root, self.config.root_dir)
            if rel_root != ".":
                rel_parts = rel_root.replace("\\", "/").split("/")
                if any(part in excluded_dirs for part in rel_parts):
                    continue

            for filename in filenames:
                file_path = os.path.join(root, filename)
                if self.should_analyze(file_path):
                    files.append(file_path)

        return sorted(files)

    async def analyze_batch(self, files: List[str]) -> List[FileAnalysis]:
        """Analyse un batch de fichiers en parallèle"""
        tasks = [self._analyze_file_with_all_agents(file_path) for file_path in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        analyses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                analyses.append(
                    FileAnalysis(
                        file_path=files[i],
                        language=self.cae.detect_language(files[i]),
                        objective="Erreur lors de l'analyse",
                        strengths=[],
                        risks=[f"Exception: {str(result)}"],
                        suggestions=[],
                        analysis_markdown="",
                        success=False,
                        error=str(result),
                    )
                )
            else:
                analyses.append(result)

        return analyses

    async def _analyze_file_with_all_agents(self, file_path: str) -> FileAnalysis:
        """Analyse un fichier avec tous les agents"""
        # Analyse de base avec CAE
        analysis = await self.cae.analyze_file(file_path)

        # Lire le contenu pour les autres analyses
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except:
            return analysis

        # Analyse de sécurité
        if self.ssa:
            try:
                security_issues = await self.ssa.analyze_security(
                    file_path, content, analysis.language
                )
                analysis.security_issues = security_issues

                # Ajouter les problèmes de sécurité aux risques
                for issue in security_issues:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(issue.severity, "⚪")
                    analysis.risks.append(
                        f"{severity_emoji} **Sécurité ({issue.severity})**: {issue.description} - {issue.recommendation}"
                    )
            except Exception as e:
                log_print(f"⚠️  Erreur analyse sécurité pour {file_path}: {e}")

        # Analyse de métriques
        if self.cma:
            try:
                metrics = self.cma.calculate_metrics(file_path, content, analysis.language)
                analysis.code_metrics = metrics

                # Ajouter des warnings basés sur les métriques
                if metrics.cyclomatic_complexity > 20:
                    analysis.risks.append(
                        f"⚠️ **Complexité élevée**: Complexité cyclomatique de {metrics.cyclomatic_complexity} (>20 recommandé)"
                    )
                if metrics.max_nesting_depth > 5:
                    analysis.risks.append(
                        f"⚠️ **Imbrication profonde**: Profondeur maximale de {metrics.max_nesting_depth} niveaux (>5 recommandé)"
                    )
                if metrics.duplicate_code_blocks:
                    analysis.risks.append(
                        f"⚠️ **Code dupliqué**: {len(metrics.duplicate_code_blocks)} bloc(s) dupliqué(s) détecté(s)"
                    )
            except Exception as e:
                log_print(f"⚠️  Erreur analyse métriques pour {file_path}: {e}")

        return analysis

    def save_analysis(self, analysis: FileAnalysis):
        """Sauvegarde l'analyse d'un fichier"""
        os.makedirs(self.config.output_dir, exist_ok=True)

        # Nom de fichier basé sur le chemin
        relative_path = os.path.relpath(analysis.file_path, self.config.root_dir)
        safe_name = relative_path.replace("/", "_").replace("\\", "_").replace(":", "_")
        safe_name = re.sub(r'[<>"|?*]', "_", safe_name)

        output_path = os.path.join(self.config.output_dir, f"{safe_name}.md")

        # Sanitiser le contenu Markdown pour prévenir les injections XSS
        sanitized_content = sanitize_markdown(analysis.analysis_markdown)
        sanitized_error = sanitize_markdown(analysis.error) if analysis.error else None

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(sanitized_content)
            if not analysis.success and sanitized_error:
                f.write(f"\n\n## ⚠️ Erreur\n\n{sanitized_error}\n")

    async def run(self):
        """Exécute l'analyse complète"""
        if self.doc_searcher and self.doc_searcher.enabled:
            log_print("🌐 Recherche web activée pour les documentations\n")

        log_print("🔍 Scan des fichiers...")
        # Si une liste de fichiers est fournie, utiliser celle-ci, sinon scanner tout
        if self.files_to_analyze:
            # Filtrer les fichiers pour ne garder que ceux qui doivent être analysés
            files = []
            for file_path in self.files_to_analyze:
                # Normaliser le chemin
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.config.root_dir, file_path)
                file_path = os.path.normpath(file_path)

                # Vérifier que le fichier existe et doit être analysé
                if os.path.exists(file_path) and self.should_analyze(file_path):
                    files.append(file_path)
            log_print(f"✅ {len(files)} fichier(s) à analyser (mode diff)\n")
        else:
            files = self.scan_files()
            log_print(f"✅ {len(files)} fichiers trouvés à analyser (mode full)\n")

        if not files:
            log_print("❌ Aucun fichier à analyser")
            return

        # Initialiser l'analyseur de dépendances
        log_print("🔗 Initialisation de l'analyseur de dépendances...")
        self.dependency_analyzer = DependencyAnalyzer(self.config.root_dir, files)
        self.cae.dependency_analyzer = self.dependency_analyzer
        log_print("✅ Analyseur de dépendances initialisé\n")

        # Créer le dossier de sortie
        os.makedirs(self.config.output_dir, exist_ok=True)

        # Analyser par batch
        all_analyses = []
        total_batches = (len(files) + self.config.batch_size - 1) // self.config.batch_size

        for batch_idx in range(0, len(files), self.config.batch_size):
            batch = files[batch_idx : batch_idx + self.config.batch_size]
            batch_num = (batch_idx // self.config.batch_size) + 1

            log_print(f"📦 Batch {batch_num}/{total_batches} ({len(batch)} fichiers)...")

            analyses = await self.analyze_batch(batch)

            # Sauvegarder chaque analyse
            for analysis in analyses:
                self.save_analysis(analysis)
                status = "✅" if analysis.success else "❌"
                log_print(f"  {status} {os.path.relpath(analysis.file_path, self.config.root_dir)}")

            all_analyses.extend(analyses)

            # Pause entre batches pour éviter les rate limits
            if batch_idx + self.config.batch_size < len(files):
                await asyncio.sleep(2)

        log_print(f"\n✅ Analyse de {len(all_analyses)} fichiers terminée\n")

        # Construire le graphe de dépendances et détecter les cycles
        log_print("🔄 Analyse des dépendances et détection des cycles...")
        dependencies_map = {}
        for analysis in all_analyses:
            if analysis.success and analysis.dependencies:
                dependencies_map[analysis.file_path] = analysis.dependencies

        cycles = self.dependency_analyzer.detect_circular_dependencies(dependencies_map)
        if cycles:
            log_print(f"⚠️  {len(cycles)} cycle(s) de dépendances détecté(s):")
            for i, cycle in enumerate(cycles, 1):
                cycle_paths = [
                    os.path.relpath(f, self.config.root_dir).replace("\\", "/") for f in cycle
                ]
                log_print(f"  Cycle {i}: {' → '.join(cycle_paths)}")
        else:
            log_print("✅ Aucun cycle de dépendances détecté")
        log_print()

        # Générer le rapport d'architecture
        log_print("🏗️  Génération du rapport d'architecture...")
        architecture_report = await self.aaa.generate_architecture_report(all_analyses, cycles)

        # Ajouter des métadonnées
        report_with_metadata = f"""# Vue d'ensemble de l'architecture

*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Nombre de fichiers analysés: {len(all_analyses)}*
*Fichiers réussis: {sum(1 for a in all_analyses if a.success)}*
*Fichiers échoués: {sum(1 for a in all_analyses if not a.success)}*

---

{architecture_report}
"""

        # Sauvegarder le rapport (sanitisé pour prévenir XSS)
        os.makedirs(os.path.dirname(self.config.architecture_report_path), exist_ok=True)
        sanitized_report = sanitize_markdown(report_with_metadata)
        with open(self.config.architecture_report_path, "w", encoding="utf-8") as f:
            f.write(sanitized_report)

        log_print(f"✅ Rapport d'architecture sauvegardé: {self.config.architecture_report_path}\n")

        # Analyser les vulnérabilités des dépendances
        if self.dva:
            log_print("🔒 Analyse des vulnérabilités des dépendances via OSV API...")
            dep_vulnerabilities = await self.dva.analyze_dependencies()

            if dep_vulnerabilities:
                log_print(
                    f"\n⚠️  {len(dep_vulnerabilities)} vulnérabilité(s) détectée(s) dans les dépendances\n"
                )

                # Grouper par sévérité
                by_severity = defaultdict(list)
                for vuln in dep_vulnerabilities:
                    by_severity[vuln.severity].append(vuln)

                log_print("📊 Répartition par sévérité:")
                for severity in ["critical", "high", "medium", "low"]:
                    if severity in by_severity:
                        count = len(by_severity[severity])
                        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(
                            severity, "⚪"
                        )
                        log_print(f"  {emoji} {severity.upper()}: {count}")

                # Sauvegarder un rapport des vulnérabilités (sanitisé pour prévenir XSS)
                vuln_report_path = os.path.join(self.config.output_dir, "vulnerabilities_report.md")
                vuln_report_content = "# Rapport des Vulnérabilités des Dépendances\n\n"
                vuln_report_content += (
                    f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )
                vuln_report_content += f"**Total:** {len(dep_vulnerabilities)} vulnérabilité(s)\n\n"

                for severity in ["critical", "high", "medium", "low"]:
                    if severity in by_severity:
                        vuln_report_content += (
                            f"## {severity.upper()} ({len(by_severity[severity])})\n\n"
                        )
                        for vuln in by_severity[severity]:
                            vuln_report_content += f"### {vuln.package_name}@{vuln.version}\n\n"
                            vuln_report_content += f"- **ID:** {vuln.vulnerability_id}\n"
                            if vuln.cve_id:
                                vuln_report_content += f"- **CVE:** {vuln.cve_id}\n"
                            vuln_report_content += f"- **Description:** {vuln.description}\n"
                            vuln_report_content += (
                                f"- **Versions affectées:** {vuln.affected_versions}\n"
                            )
                            if vuln.fixed_version:
                                vuln_report_content += (
                                    f"- **Version corrigée:** {vuln.fixed_version}\n"
                                )
                            vuln_report_content += "\n"

                sanitized_vuln_report = sanitize_markdown(vuln_report_content)
                with open(vuln_report_path, "w", encoding="utf-8") as f:
                    f.write(sanitized_vuln_report)

                log_print(f"📄 Rapport sauvegardé: {vuln_report_path}\n")
            else:
                log_print("✅ Aucune vulnérabilité détectée dans les dépendances\n")
        else:
            dep_vulnerabilities = []

        # Générer le rapport d'assurance qualité (synthèse de tout)
        log_print("📋 Génération du rapport d'assurance qualité...")
        quality_report = await self.qaa.generate_quality_report(
            all_analyses, architecture_report, dep_vulnerabilities, cycles
        )

        # Ajouter des métadonnées
        quality_report_with_metadata = f"""# Rapport d'Assurance Qualité

*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Synthèse de toutes les analyses effectuées*

---

{quality_report}
"""

        # Sauvegarder le rapport d'assurance qualité (sanitisé pour prévenir XSS)
        quality_report_path = os.path.join(self.config.output_dir, "quality_assurance_report.md")
        os.makedirs(os.path.dirname(quality_report_path), exist_ok=True)
        sanitized_quality_report = sanitize_markdown(quality_report_with_metadata)
        with open(quality_report_path, "w", encoding="utf-8") as f:
            f.write(sanitized_quality_report)

        log_print(f"✅ Rapport d'assurance qualité sauvegardé: {quality_report_path}\n")

        # Statistiques finales
        log_print("📊 Statistiques:")
        log_print(f"  - Fichiers analysés: {len(all_analyses)}")
        log_print(f"  - Succès: {sum(1 for a in all_analyses if a.success)}")
        log_print(f"  - Échecs: {sum(1 for a in all_analyses if not a.success)}")

        languages = {}
        for analysis in all_analyses:
            lang = analysis.language
            languages[lang] = languages.get(lang, 0) + 1

        log_print(f"\n  Répartition par langage:")
        for lang, count in sorted(languages.items(), key=lambda x: -x[1]):
            log_print(f"    - {lang}: {count}")

        # Nettoyer les fichiers temporaires générés
        if self.code_generator:
            self.code_generator.cleanup()
