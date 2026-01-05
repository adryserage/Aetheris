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
async def validate_analysis(context):
    """Valide les résultats de l'analyse"""
    for analysis in context.analyses:
        if not analysis.success:
            # Faire quelque chose avec les erreurs
            log_error(f"Échec: {analysis.file_path}")

        # Vérifier des critères personnalisés
        if analysis.code_metrics:
            if analysis.code_metrics.cyclomatic_complexity > 30:
                log_warning(f"Complexité élevée: {analysis.file_path}")

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

    for analysis in context.analyses:
        if hasattr(analysis, 'bugs') and analysis.bugs:
            for bug in analysis.bugs:
                total_bugs += 1
                # Collecter les fichiers avec fort impact
                if len(bug.impacted_files) > 5:
                    high_impact_files.update(bug.impacted_files)

    print(f"Total bugs détectés: {total_bugs}")
    print(f"Fichiers à fort impact: {len(high_impact_files)}")

    # Stocker dans les métadonnées pour utilisation ultérieure
    context.metadata["total_bugs"] = total_bugs
    context.metadata["high_impact_files"] = list(high_impact_files)

orchestrator.register_hook(WorkflowStage.IMPACT_ANALYSIS, on_impact_analysis)
```

### Exemple 6 : Hook sur le graphe de dépendances inverse (v2.1.0+)

```python
async def on_reverse_dependencies(context):
    """Analyse le graphe de dépendances inverse"""
    # Les dépendances inverses sont accessibles via l'analyseur de dépendances
    for analysis in context.analyses:
        if hasattr(analysis, 'reverse_dependencies') and analysis.reverse_dependencies:
            file_path = analysis.file_path
            dependents = analysis.reverse_dependencies
            print(f"{file_path} est importé par {len(dependents)} fichier(s)")

orchestrator.register_hook(WorkflowStage.REVERSE_DEPENDENCY, on_reverse_dependencies)
```

### Exemple 7 : Hook sur l'extraction des exports (v2.1.0+)

```python
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
        print(f"  - {export_type}: {count}")

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

## Limitations

- Les hooks ne peuvent pas modifier le comportement de l'étape elle-même
- Les erreurs dans les hooks sont capturées et loggées, mais n'interrompent pas le workflow
- Les hooks sont exécutés séquentiellement (pas en parallèle)

## Extensions Futures

Le système de hooks peut être étendu pour :

- Support des hooks conditionnels
- Système de plugins avec chargement dynamique
- Hooks avec priorité
- Hooks qui peuvent modifier le contexte

## Références

- `src/core/orchestrator.py` : Implémentation de l'orchestrateur et des hooks
- `src/core/analyzer.py` : Utilisation de l'orchestrateur dans CodeAnalyzer
- `src/models/data_models.py` : Modèles de données pour le contexte
