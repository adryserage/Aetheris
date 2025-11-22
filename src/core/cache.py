"""
Système de cache pour les analyses de code
Réduit les coûts API en évitant les ré-analyses inutiles
"""

import os
import json
import hashlib
import subprocess
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from src.models.data_models import FileAnalysis


class AnalysisCache:
    """Cache pour les résultats d'analyse de fichiers"""

    def __init__(self, root_dir: str, cache_dir: str = ".cache/aetheris", ttl_days: int = 7):
        """
        Initialise le cache

        Args:
            root_dir: Répertoire racine du projet
            cache_dir: Répertoire de cache (relatif à root_dir)
            ttl_days: Durée de vie du cache en jours
        """
        self.root_dir = root_dir
        self.cache_dir = os.path.join(root_dir, cache_dir)
        self.ttl_days = ttl_days
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_file_hash(self, file_path: str) -> str:
        """Calcule le hash SHA256 du contenu d'un fichier"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            return ""

    def _get_git_sha(self, file_path: str) -> Optional[str]:
        """
        Récupère le SHA git du dernier commit qui a modifié le fichier
        Retourne None si git n'est pas disponible ou si le fichier n'est pas dans git
        """
        try:
            rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H", "--", rel_path],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()[:16]  # Utiliser les 16 premiers caractères
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def _get_file_timestamp(self, file_path: str) -> float:
        """Récupère le timestamp de modification du fichier"""
        try:
            return os.path.getmtime(file_path)
        except Exception:
            return 0.0

    def _get_cache_key(self, file_path: str) -> str:
        """
        Génère une clé de cache unique pour un fichier
        Format: {git_sha}_{file_path_hash}_{timestamp}
        """
        git_sha = self._get_git_sha(file_path)
        file_hash = self._get_file_hash(file_path)
        timestamp = int(self._get_file_timestamp(file_path))

        # Normaliser le chemin pour la clé
        rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
        path_hash = hashlib.md5(rel_path.encode()).hexdigest()[:8]

        if git_sha:
            return f"{git_sha}_{path_hash}_{timestamp}"
        else:
            # Fallback si git n'est pas disponible
            return f"{file_hash}_{path_hash}_{timestamp}"

    def _get_cache_path(self, cache_key: str) -> str:
        """Retourne le chemin du fichier de cache"""
        # Utiliser les premiers caractères pour créer une structure de dossiers
        dir_name = cache_key[:2]
        cache_subdir = os.path.join(self.cache_dir, dir_name)
        os.makedirs(cache_subdir, exist_ok=True)
        return os.path.join(cache_subdir, f"{cache_key}.json")

    def get(self, file_path: str) -> Optional[FileAnalysis]:
        """
        Récupère une analyse depuis le cache si elle existe et est valide

        Args:
            file_path: Chemin du fichier à analyser

        Returns:
            FileAnalysis si trouvé et valide, None sinon
        """
        try:
            cache_key = self._get_cache_key(file_path)
            cache_path = self._get_cache_path(cache_key)

            if not os.path.exists(cache_path):
                return None

            # Vérifier l'âge du cache
            cache_mtime = os.path.getmtime(cache_path)
            cache_age = datetime.now() - datetime.fromtimestamp(cache_mtime)
            if cache_age > timedelta(days=self.ttl_days):
                # Cache expiré
                os.remove(cache_path)
                return None

            # Vérifier que le fichier n'a pas été modifié depuis la mise en cache
            file_timestamp = self._get_file_timestamp(file_path)
            cached_data = json.load(open(cache_path, "r", encoding="utf-8"))
            cached_timestamp = cached_data.get("file_timestamp", 0)

            if file_timestamp != cached_timestamp:
                # Fichier modifié, cache invalide
                os.remove(cache_path)
                return None

            # Charger l'analyse depuis le cache
            analysis_data = cached_data.get("analysis")
            if not analysis_data:
                return None

            # Reconstruire l'objet FileAnalysis
            return FileAnalysis(
                file_path=analysis_data.get("file_path", file_path),
                language=analysis_data.get("language", ""),
                objective=analysis_data.get("objective", ""),
                strengths=analysis_data.get("strengths", []),
                risks=analysis_data.get("risks", []),
                suggestions=analysis_data.get("suggestions", []),
                analysis_markdown=analysis_data.get("analysis_markdown", ""),
                success=analysis_data.get("success", False),
                dependencies=[
                    # Reconstruire FileDependency si nécessaire
                    # Pour simplifier, on stocke juste les données de base
                ],
                inconsistencies=analysis_data.get("inconsistencies", []),
                security_issues=analysis_data.get("security_issues", []),
                code_metrics=analysis_data.get("code_metrics"),
                error=analysis_data.get("error"),
            )

        except Exception as e:
            # En cas d'erreur, ignorer le cache
            return None

    def set(self, file_path: str, analysis: FileAnalysis):
        """
        Sauvegarde une analyse dans le cache

        Args:
            file_path: Chemin du fichier analysé
            analysis: Résultat de l'analyse
        """
        try:
            cache_key = self._get_cache_key(file_path)
            cache_path = self._get_cache_path(cache_key)

            # Préparer les données à sauvegarder
            analysis_data = {
                "file_path": analysis.file_path,
                "language": analysis.language,
                "objective": analysis.objective,
                "strengths": analysis.strengths,
                "risks": analysis.risks,
                "suggestions": analysis.suggestions,
                "analysis_markdown": analysis.analysis_markdown,
                "success": analysis.success,
                "inconsistencies": analysis.inconsistencies,
                "security_issues": [
                    {
                        "severity": issue.severity,
                        "issue_type": issue.issue_type,
                        "description": issue.description,
                        "line_number": issue.line_number,
                        "code_snippet": issue.code_snippet,
                        "recommendation": issue.recommendation,
                    }
                    for issue in analysis.security_issues
                ],
                "code_metrics": (
                    {
                        "file_path": analysis.code_metrics.file_path,
                        "language": analysis.code_metrics.language,
                        "lines_of_code": analysis.code_metrics.lines_of_code,
                        "cyclomatic_complexity": analysis.code_metrics.cyclomatic_complexity,
                        "max_nesting_depth": analysis.code_metrics.max_nesting_depth,
                        "function_count": analysis.code_metrics.function_count,
                        "average_function_length": analysis.code_metrics.average_function_length,
                        "duplicate_code_blocks": analysis.code_metrics.duplicate_code_blocks,
                        "maintainability_index": analysis.code_metrics.maintainability_index,
                    }
                    if analysis.code_metrics
                    else None
                ),
                "error": analysis.error,
            }

            cache_data = {
                "cache_key": cache_key,
                "file_path": file_path,
                "file_timestamp": self._get_file_timestamp(file_path),
                "cached_at": datetime.now().isoformat(),
                "analysis": analysis_data,
            }

            # Sauvegarder dans le cache
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

        except Exception:
            # En cas d'erreur, ignorer (ne pas bloquer l'analyse)
            pass

    def clear(self, older_than_days: Optional[int] = None):
        """
        Nettoie le cache

        Args:
            older_than_days: Supprimer les entrées plus anciennes que X jours (None = tout supprimer)
        """
        try:
            if older_than_days is None:
                # Supprimer tout le cache
                import shutil

                if os.path.exists(self.cache_dir):
                    shutil.rmtree(self.cache_dir)
                    os.makedirs(self.cache_dir, exist_ok=True)
            else:
                # Supprimer uniquement les entrées expirées
                cutoff_time = datetime.now() - timedelta(days=older_than_days)
                for root, dirs, files in os.walk(self.cache_dir):
                    for file in files:
                        if file.endswith(".json"):
                            file_path = os.path.join(root, file)
                            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                            if file_mtime < cutoff_time:
                                os.remove(file_path)

        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le cache"""
        try:
            total_files = 0
            total_size = 0
            for root, dirs, files in os.walk(self.cache_dir):
                for file in files:
                    if file.endswith(".json"):
                        total_files += 1
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)

            return {
                "cache_dir": self.cache_dir,
                "total_entries": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
            }
        except Exception:
            return {
                "cache_dir": self.cache_dir,
                "total_entries": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0,
            }
