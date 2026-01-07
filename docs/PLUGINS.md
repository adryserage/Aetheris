# Système de Plugins et Hooks

Le système d'analyse Aetheris inclut un système de hooks/plugins qui permet d'étendre et de personnaliser le comportement du workflow d'analyse.

## Vue d'ensemble

Le système de hooks permet d'exécuter du code personnalisé à différentes étapes du workflow d'analyse. Les hooks sont enregistrés sur des étapes spécifiques et sont exécutés avant et après l'exécution de chaque étape.

## Architecture

Le système de hooks est intégré dans l'`AnalysisOrchestrator` qui gère l'exécution du workflow. Chaque étape du workflow peut avoir plusieurs hooks associés.

### Étapes du Workflow

Les hooks peuvent être enregistrés sur les étapes suivantes :

- `WorkflowStage.SCAN` : Scan des fichiers
- `WorkflowStage.DEPENDENCY_INIT` : Initialisation de l'analyseur de dépendances
- `WorkflowStage.FILE_ANALYSIS` : Analyse des fichiers
- `WorkflowStage.EXPORT_ANALYSIS` : Extraction des exports de chaque fichier (v2.1.0+)
- `WorkflowStage.REVERSE_DEPENDENCY` : Construction du graphe de dépendances inverse (v2.1.0+)
- `WorkflowStage.IMPACT_ANALYSIS` : Analyse d'impact des bugs (v2.1.0+)
- `WorkflowStage.DEPENDENCY_ANALYSIS` : Analyse des dépendances et détection des cycles
- `WorkflowStage.ARCHITECTURE_REPORT` : Génération du rapport d'architecture
- `WorkflowStage.VULNERABILITY_ANALYSIS` : Analyse des vulnérabilités
- `WorkflowStage.QUALITY_REPORT` : Génération du rapport d'assurance qualité

## Utilisation

### Enregistrer un Hook

Pour enregistrer un hook, utilisez la méthode `register_hook()` de l'orchestrateur :

```python
from src.core.orchestrator import AnalysisOrchestrator, WorkflowStage
from src.core.config import AnalysisConfig

# Créer l'orchestrateur
orchestrator = AnalysisOrchestrator(config, progress_manager)

# Définir un hook
async def my_hook(context):
    print(f"Étape {context.current_stage} exécutée")
    # Accéder aux données du contexte
    print(f"Fichiers: {len(context.files)}")
    print(f"Analyses: {len(context.analyses)}")

# Enregistrer le hook sur une étape
orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, my_hook)
```

### Hooks Synchrones et Asynchrones

Les hooks peuvent être synchrones ou asynchrones :

```python
# Hook synchrone
def sync_hook(context):
    print("Hook synchrone")

# Hook asynchrone
async def async_hook(context):
    await some_async_operation()
    print("Hook asynchrone")

orchestrator.register_hook(WorkflowStage.SCAN, sync_hook)
orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, async_hook)
```

### Accéder au Contexte

Le hook reçoit un objet `WorkflowContext` qui contient toutes les données du workflow :

```python
async def my_hook(context: WorkflowContext):
    # Fichiers à analyser
    files = context.files

    # Analyses complétées
    analyses = context.analyses

    # Cycles de dépendances détectés
    cycles = context.cycles

    # Vulnérabilités détectées
    vulnerabilities = context.vulnerabilities

    # Rapports générés
    architecture_report = context.architecture_report
    quality_report = context.quality_report

    # Erreurs rencontrées
    errors = context.errors

    # Métadonnées personnalisées
    metadata = context.metadata

    # Temps d'exécution
    start_time = context.start_time
    end_time = context.end_time
```

## Exemples d'Utilisation

### Exemple 1 : Logging Personnalisé

```python
async def log_step_progress(context):
    """Log les progrès de chaque étape"""
    import logging
    logger = logging.getLogger("aetheris")

    logger.info(f"Étape exécutée: {len(context.files)} fichiers")
    if context.analyses:
        success_count = sum(1 for a in context.analyses if a.success)
        logger.info(f"Analyses réussies: {success_count}/{len(context.analyses)}")

orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, log_step_progress)
```

### Exemple 2 : Notification

```python
async def send_notification(context):
    """Envoie une notification à la fin de l'analyse"""
    if context.end_time:
        # Envoyer une notification (email, Slack, etc.)
        send_slack_message(f"Analyse terminée: {len(context.analyses)} fichiers")

orchestrator.register_hook(WorkflowStage.QUALITY_REPORT, send_notification)
```

### Exemple 3 : Validation Personnalisée

```python
import re

def sanitize_log_input(value: str) -> str:
    """Assainit les entrées pour éviter le Log Forging.

    Supprime les caractères de contrôle qui pourraient falsifier les logs.
    """
    # Supprime les caractères de contrôle (retours à la ligne, tabs, etc.)
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(value))

async def validate_analysis(context):
    """Valide les résultats de l'analyse"""
    for analysis in context.analyses:
        # Assainir le chemin avant de le logger (prévention Log Forging)
        safe_path = sanitize_log_input(analysis.file_path)

        if not analysis.success:
            # Faire quelque chose avec les erreurs
            log_error(f"Échec: {safe_path}")

        # Vérifier des critères personnalisés
        if analysis.code_metrics:
            if analysis.code_metrics.cyclomatic_complexity > 30:
                log_warning(f"Complexité élevée: {safe_path}")

orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, validate_analysis)
```

### Exemple 4 : Export Personnalisé

```python
async def export_to_custom_format(context):
    """Exporte les résultats dans un format personnalisé"""
    import json

    # Créer un format personnalisé
    custom_data = {
        "files": len(context.files),
        "analyses": [
            {
                "file": a.file_path,
                "language": a.language,
                "success": a.success,
            }
            for a in context.analyses
        ],
    }

    # Sauvegarder
    with open("custom_export.json", "w") as f:
        json.dump(custom_data, f, indent=2)

orchestrator.register_hook(WorkflowStage.QUALITY_REPORT, export_to_custom_format)
```

### Exemple 5 : Hook sur l'analyse d'impact (v2.1.0+)

```python
async def on_impact_analysis(context):
    """Traite les résultats de l'analyse d'impact des bugs"""
    # Accéder aux bugs via les analyses
    total_bugs = 0
    high_impact_files = set()

    # Validation défensive du contexte
    analyses = getattr(context, 'analyses', None)
    if not analyses or not isinstance(analyses, (list, tuple)):
        return

    for analysis in analyses:
        # Vérifier que l'analyse a un attribut bugs valide
        bugs = getattr(analysis, 'bugs', None)
        if not bugs or not isinstance(bugs, (list, tuple)):
            continue

        for bug in bugs:
            # Valider que bug est un objet valide avec impacted_files
            if bug is None:
                continue

            total_bugs += 1

            # Validation robuste de impacted_files
            impacted_files = getattr(bug, 'impacted_files', None)
            if impacted_files and isinstance(impacted_files, (list, tuple, set)):
                # Collecter les fichiers avec fort impact
                if len(impacted_files) > 5:
                    high_impact_files.update(impacted_files)

    print(f"Total bugs détectés: {total_bugs}")
    print(f"Fichiers à fort impact: {len(high_impact_files)}")

    # Stocker dans les métadonnées pour utilisation ultérieure
    if hasattr(context, 'metadata') and isinstance(context.metadata, dict):
        context.metadata["total_bugs"] = total_bugs
        context.metadata["high_impact_files"] = list(high_impact_files)

orchestrator.register_hook(WorkflowStage.IMPACT_ANALYSIS, on_impact_analysis)
```

### Exemple 6 : Hook sur le graphe de dépendances inverse (v2.1.0+)

```python
import re

def sanitize_log_input(value: str) -> str:
    """Assainit les entrées pour éviter le Log Forging."""
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(value))

async def on_reverse_dependencies(context):
    """Analyse le graphe de dépendances inverse"""
    # Les dépendances inverses sont accessibles via l'analyseur de dépendances
    for analysis in context.analyses:
        if hasattr(analysis, 'reverse_dependencies') and analysis.reverse_dependencies:
            # Assainir le chemin avant affichage (prévention Log Forging)
            safe_path = sanitize_log_input(analysis.file_path)
            dependents = analysis.reverse_dependencies
            print(f"{safe_path} est importé par {len(dependents)} fichier(s)")

orchestrator.register_hook(WorkflowStage.REVERSE_DEPENDENCY, on_reverse_dependencies)
```

### Exemple 7 : Hook sur l'extraction des exports (v2.1.0+)

```python
import re

def sanitize_log_input(value: str) -> str:
    """Assainit les entrées pour éviter le Log Forging."""
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(value))

async def on_export_analysis(context):
    """Analyse les exports de chaque fichier"""
    total_exports = 0
    export_types = {}

    for analysis in context.analyses:
        if hasattr(analysis, 'exports') and analysis.exports:
            for export in analysis.exports:
                total_exports += 1
                export_type = export.export_type
                export_types[export_type] = export_types.get(export_type, 0) + 1

    print(f"Total exports: {total_exports}")
    for export_type, count in export_types.items():
        # Assainir le type d'export avant affichage (prévention Log Forging)
        safe_type = sanitize_log_input(export_type)
        print(f"  - {safe_type}: {count}")

orchestrator.register_hook(WorkflowStage.EXPORT_ANALYSIS, on_export_analysis)
```

## Intégration dans CodeAnalyzer

Pour utiliser les hooks avec `CodeAnalyzer`, accédez à l'orchestrateur interne :

```python
from src.core.analyzer import CodeAnalyzer
from src.core.config import AnalysisConfig
from src.core.orchestrator import WorkflowStage

config = AnalysisConfig(...)
analyzer = CodeAnalyzer(config, progress_manager=progress_manager)

# Accéder à l'orchestrateur
orchestrator = analyzer.orchestrator

# Enregistrer un hook
async def my_hook(context):
    print("Hook exécuté")

orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, my_hook)

# Exécuter l'analyse
await analyzer.run()
```

## Bonnes Pratiques

1. **Gestion d'erreurs** : Toujours gérer les erreurs dans vos hooks pour ne pas interrompre le workflow

   ```python
   async def safe_hook(context):
       try:
           # Votre code
           pass
       except Exception as e:
           print(f"Erreur dans le hook: {e}")
   ```

2. **Performance** : Les hooks sont exécutés à chaque étape, gardez-les légers

   ```python
   # Éviter les opérations lourdes dans les hooks
   # Utiliser des opérations asynchrones si nécessaire
   ```

3. **Ordre d'exécution** : Les hooks sont exécutés dans l'ordre d'enregistrement

   ```python
   # Hook 1 exécuté en premier
   orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, hook1)
   # Hook 2 exécuté après hook1
   orchestrator.register_hook(WorkflowStage.FILE_ANALYSIS, hook2)
   ```

4. **Contexte partagé** : Utilisez `context.metadata` pour partager des données entre hooks

   ```python
   async def hook1(context):
       context.metadata["custom_data"] = "value"

   async def hook2(context):
       data = context.metadata.get("custom_data")
   ```

## Hooks Critiques (Bloquants)

Par défaut, les erreurs dans les hooks sont capturées et loggées sans interrompre le workflow. Cependant, pour les cas d'usage critiques (validation de sécurité, conformité, etc.), vous pouvez enregistrer des **hooks critiques** qui interrompent le workflow en cas d'échec.

### Enregistrer un Hook Critique

```python
from src.core.orchestrator import AnalysisOrchestrator, WorkflowStage

# Hook critique - une erreur interrompt le workflow
async def security_validation_hook(context):
    """Valide les critères de sécurité - BLOQUANT en cas d'échec"""
    critical_vulnerabilities = [
        v for v in context.vulnerabilities
        if v.severity == "critical"
    ]

    if critical_vulnerabilities:
        # Lever une exception interrompt le workflow
        raise SecurityValidationError(
            f"Échec de validation: {len(critical_vulnerabilities)} vulnérabilités critiques détectées"
        )

# Enregistrer comme hook critique (critical=True)
orchestrator.register_hook(
    WorkflowStage.VULNERABILITY_ANALYSIS,
    security_validation_hook,
    critical=True  # Ce hook peut interrompre le workflow
)
```

### Comportement des Hooks Critiques vs Non-Critiques

| Type | Paramètre | Comportement en cas d'erreur |
|------|-----------|------------------------------|
| **Non-critique** (défaut) | `critical=False` | Erreur loggée, workflow continue |
| **Critique** | `critical=True` | Erreur loggée, workflow **interrompu** |

### Exemple : Gate de Sécurité

```python
class SecurityGateError(Exception):
    """Erreur de validation de sécurité"""
    pass

async def security_gate(context):
    """
    Gate de sécurité obligatoire avant déploiement.

    Ce hook DOIT bloquer le workflow si les critères ne sont pas remplis.
    """
    # Vérifier les vulnérabilités critiques
    if any(v.severity == "critical" for v in context.vulnerabilities):
        raise SecurityGateError("Vulnérabilités critiques non résolues")

    # Vérifier la couverture de sécurité
    security_score = context.metadata.get("security_score", 0)
    if security_score < 70:
        raise SecurityGateError(f"Score de sécurité insuffisant: {security_score}/100")

    # Vérifier les secrets exposés
    if context.metadata.get("exposed_secrets"):
        raise SecurityGateError("Secrets exposés détectés dans le code")

# IMPORTANT: critical=True pour bloquer le workflow
orchestrator.register_hook(
    WorkflowStage.QUALITY_REPORT,
    security_gate,
    critical=True
)
```

### Exemple : Validation de Conformité

```python
async def compliance_check(context):
    """Vérifie la conformité aux standards (OWASP, SOC2, etc.)"""
    violations = []

    for analysis in context.analyses:
        # Vérifier les patterns interdits
        if analysis.has_sql_injection_risk:
            violations.append(f"SQL Injection: {analysis.file_path}")
        if analysis.has_hardcoded_secrets:
            violations.append(f"Secrets hardcodés: {analysis.file_path}")

    if violations:
        raise ComplianceError(
            f"Violations de conformité détectées:\n" +
            "\n".join(f"  - {v}" for v in violations)
        )

orchestrator.register_hook(
    WorkflowStage.FILE_ANALYSIS,
    compliance_check,
    critical=True  # Bloque le déploiement si non-conforme
)
```

### Gestion des Erreurs de Hooks Critiques

Quand un hook critique échoue, l'orchestrateur :

1. **Log l'erreur** avec le niveau `ERROR`
2. **Stocke l'erreur** dans `context.errors`
3. **Interrompt le workflow** immédiatement
4. **Retourne un statut d'échec** avec les détails

```python
try:
    result = await analyzer.run()
except CriticalHookError as e:
    print(f"Workflow interrompu par hook critique: {e}")
    print(f"Étape: {e.stage}")
    print(f"Hook: {e.hook_name}")
    sys.exit(1)
```

## Limitations

- Les hooks ne peuvent pas modifier le comportement de l'étape elle-même
- Les hooks non-critiques (`critical=False`, défaut) capturent les erreurs sans interrompre le workflow
- Les hooks critiques (`critical=True`) interrompent le workflow en cas d'erreur — **à utiliser pour les validations de sécurité**
- Les hooks sont exécutés séquentiellement (pas en parallèle)

## Chargement Dynamique de Plugins

Aetheris supporte le chargement dynamique de plugins "drop-in" via un répertoire de plugins. Cette approche permet de créer des extensions tierces sans modifier le code source.

### Structure du Répertoire de Plugins

```
~/.aetheris/plugins/           # Répertoire global des plugins
├── my_plugin/
│   ├── __init__.py            # Point d'entrée du plugin
│   └── hooks.py               # Définitions des hooks
└── another_plugin/
    └── __init__.py

./plugins/                     # Répertoire local (projet)
└── project_specific_plugin/
    └── __init__.py
```

### Convention de Plugin

Chaque plugin doit exposer une fonction `register(orchestrator)` dans son `__init__.py` :

```python
# ~/.aetheris/plugins/my_plugin/__init__.py
"""
Mon Plugin Aetheris
Description: Ajoute des notifications Slack après l'analyse
"""

from src.core.orchestrator import WorkflowStage

# Métadonnées du plugin (optionnel mais recommandé)
PLUGIN_NAME = "my_plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Ajoute des notifications Slack après l'analyse"


async def on_analysis_complete(context):
    """Hook exécuté après le rapport de qualité"""
    if context.end_time:
        # Logique de notification
        print(f"Analyse terminée: {len(context.analyses)} fichiers")


def register(orchestrator):
    """Point d'entrée appelé par le chargeur de plugins.

    Args:
        orchestrator: Instance de AnalysisOrchestrator
    """
    orchestrator.register_hook(WorkflowStage.QUALITY_REPORT, on_analysis_complete)
    print(f"✅ Plugin '{PLUGIN_NAME}' v{PLUGIN_VERSION} chargé")
```

### Chargeur de Plugins

Utilisez le module `PluginLoader` pour charger automatiquement les plugins :

```python
import importlib.util
import sys
from pathlib import Path
from typing import List, Optional


class PluginLoader:
    """Chargeur dynamique de plugins Aetheris."""

    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """Initialise le chargeur de plugins.

        Args:
            plugin_dirs: Liste des répertoires de plugins à scanner.
                        Par défaut: ~/.aetheris/plugins/ et ./plugins/
        """
        self.plugin_dirs = plugin_dirs or [
            Path.home() / ".aetheris" / "plugins",
            Path.cwd() / "plugins",
        ]
        self.loaded_plugins: List[str] = []

    def discover_plugins(self) -> List[Path]:
        """Découvre tous les plugins disponibles.

        Returns:
            Liste des chemins vers les répertoires de plugins
        """
        plugins = []
        for plugin_dir in self.plugin_dirs:
            if plugin_dir.exists():
                for item in plugin_dir.iterdir():
                    if item.is_dir() and (item / "__init__.py").exists():
                        plugins.append(item)
        return plugins

    def load_plugin(self, plugin_path: Path) -> bool:
        """Charge un plugin spécifique.

        Args:
            plugin_path: Chemin vers le répertoire du plugin

        Returns:
            True si le chargement a réussi, False sinon
        """
        plugin_name = plugin_path.name
        init_file = plugin_path / "__init__.py"

        try:
            # Charger le module dynamiquement
            spec = importlib.util.spec_from_file_location(
                f"aetheris_plugins.{plugin_name}",
                init_file
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)

                # Vérifier que le plugin expose une fonction register
                if hasattr(module, "register"):
                    self.loaded_plugins.append(plugin_name)
                    return True
                else:
                    print(f"⚠️  Plugin '{plugin_name}': fonction 'register' manquante")
                    return False
        except Exception as e:
            print(f"❌ Erreur lors du chargement de '{plugin_name}': {e}")
            return False

        return False

    def load_all(self, orchestrator) -> int:
        """Charge tous les plugins et les enregistre auprès de l'orchestrateur.

        Args:
            orchestrator: Instance de AnalysisOrchestrator

        Returns:
            Nombre de plugins chargés avec succès
        """
        plugins = self.discover_plugins()
        loaded_count = 0

        for plugin_path in plugins:
            if self.load_plugin(plugin_path):
                plugin_name = plugin_path.name
                module = sys.modules.get(f"aetheris_plugins.{plugin_name}")
                if module and hasattr(module, "register"):
                    try:
                        module.register(orchestrator)
                        loaded_count += 1
                    except Exception as e:
                        print(f"❌ Erreur lors de l'enregistrement de '{plugin_name}': {e}")

        return loaded_count
```

### Intégration avec CodeAnalyzer

Pour activer le chargement automatique des plugins dans votre workflow :

```python
from src.core.analyzer import CodeAnalyzer
from src.core.config import AnalysisConfig

# Créer l'analyseur
config = AnalysisConfig(...)
analyzer = CodeAnalyzer(config, progress_manager=progress_manager)

# Charger les plugins dynamiquement
loader = PluginLoader()
plugins_loaded = loader.load_all(analyzer.orchestrator)
print(f"📦 {plugins_loaded} plugin(s) chargé(s)")

# Exécuter l'analyse avec les plugins actifs
await analyzer.run()
```

### Exemple Complet : Plugin de Métriques Custom

```python
# ~/.aetheris/plugins/custom_metrics/__init__.py
"""Plugin de métriques personnalisées pour Aetheris."""

import json
from datetime import datetime
from pathlib import Path
from src.core.orchestrator import WorkflowStage

PLUGIN_NAME = "custom_metrics"
PLUGIN_VERSION = "1.0.0"


async def collect_metrics(context):
    """Collecte des métriques personnalisées après l'analyse."""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(context.files),
        "successful_analyses": sum(1 for a in context.analyses if a.success),
        "failed_analyses": sum(1 for a in context.analyses if not a.success),
        "vulnerabilities_count": len(context.vulnerabilities),
        "errors": context.errors,
    }

    # Calculer des métriques agrégées
    if context.analyses:
        complexities = [
            a.code_metrics.cyclomatic_complexity
            for a in context.analyses
            if a.code_metrics and a.code_metrics.cyclomatic_complexity
        ]
        if complexities:
            metrics["avg_complexity"] = sum(complexities) / len(complexities)
            metrics["max_complexity"] = max(complexities)

    # Sauvegarder les métriques
    output_dir = Path("docs/metrics")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"custom_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"📊 Métriques personnalisées sauvegardées: {output_file}")

    # Stocker dans le contexte pour d'autres plugins
    context.metadata["custom_metrics"] = metrics


def register(orchestrator):
    """Enregistre le plugin auprès de l'orchestrateur."""
    orchestrator.register_hook(WorkflowStage.QUALITY_REPORT, collect_metrics)
    print(f"✅ Plugin '{PLUGIN_NAME}' v{PLUGIN_VERSION} activé")
```

### Bonnes Pratiques pour les Plugins

1. **Toujours exposer `register(orchestrator)`** : C'est le point d'entrée standard
2. **Documenter les métadonnées** : `PLUGIN_NAME`, `PLUGIN_VERSION`, `PLUGIN_DESCRIPTION`
3. **Gérer les erreurs gracieusement** : Ne jamais faire crasher le workflow principal
4. **Utiliser `context.metadata`** : Pour partager des données entre plugins
5. **Logs explicites** : Indiquer clairement quand le plugin est chargé/actif

### Désactivation de Plugins

Pour désactiver temporairement un plugin, renommez son répertoire avec un préfixe `_` :

```bash
# Désactiver
mv ~/.aetheris/plugins/my_plugin ~/.aetheris/plugins/_my_plugin

# Réactiver
mv ~/.aetheris/plugins/_my_plugin ~/.aetheris/plugins/my_plugin
```

## Extensions Futures

Le système de hooks peut être étendu pour :

- Support des hooks conditionnels
- Hooks avec priorité
- Interface CLI pour gérer les plugins (`aetheris plugins list`, `aetheris plugins enable/disable`)

## Références

- `src/core/orchestrator.py` : Implémentation de l'orchestrateur et des hooks
- `src/core/analyzer.py` : Utilisation de l'orchestrateur dans CodeAnalyzer
- `src/models/data_models.py` : Modèles de données pour le contexte
