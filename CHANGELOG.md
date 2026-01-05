# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [2.3.3] - 2025-01-05

### 🐛 Corrections

- **User Story Agent** : Corrige `AttributeError: 'ProgressManager' object has no attribute 'update_current_file'`
  - Remplace l'appel à `update_current_file` par `print` existant

## [2.3.2] - 2025-01-05

### 🐛 Corrections

- **Impact Analyzer** : Les champs `fixed`, `fixed_at`, `fix_summary` sont maintenant inclus dans le cache initial
  - Corrige l'incohérence entre le cache initial et le cache mis à jour après correction

## [2.3.1] - 2025-01-05

### ✨ Améliorations

- **Suivi des bugs corrigés** : Les bugs corrigés sont maintenant marqués dans le cache
  - Nouveau champ `fixed: boolean` dans `BugIdentifier`
  - Champ `fixed_at` avec timestamp de la correction
  - Champ `fix_summary` avec résumé de la correction appliquée
  - Les bugs déjà corrigés sont automatiquement ignorés lors des prochaines sessions
  - Le cache `.bugs_cache.json` est mis à jour après chaque correction réussie
  - Message d'info indiquant le nombre de bugs déjà corrigés

## [2.3.0] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **User Story Analysis** : Nouvelle commande `aetheris user-story` pour analyser les flux utilisateur
  - Trace les appels frontend ↔ backend bidirectionnels
  - Détecte les endpoints orphelins (définis mais jamais appelés)
  - Détecte les appels API sans handler correspondant
  - Analyse les incohérences logiques et les problèmes potentiels
  - Génère des diagrammes Mermaid et PlantUML
  - Supporte plusieurs modes d'entrée :
    - `--text "description"` : Depuis une description textuelle
    - `--file user-stories.md` : Depuis un fichier markdown
    - `--entry LoginButton.tsx` : Depuis un point d'entrée code
    - `--auto` : Auto-détection de tous les flux
  - Sortie en markdown, JSON ou les deux

- **Nouveaux modèles et services** :
  - `FlowTracer` : Détection agnostique des appels API (JS/TS, Dart, Python)
  - `UserStoryParser` : Parsing de user stories depuis texte, markdown, Gherkin
  - `UserStoryAnalysisAgent` : Agent IA pour l'analyse des flux
  - `DiagramGenerator` : Génération de diagrammes de séquence et flowcharts

- **Détection multi-framework** :
  - Frontend : fetch, axios, dio, requests, httpx, aiohttp
  - Backend : Express, Next.js, FastAPI, Flask, Django, NestJS

- **Types de problèmes détectés** :
  - `orphan_endpoint` : Endpoint défini mais jamais appelé
  - `missing_handler` : Appel API sans endpoint correspondant
  - `missing_error_handling` : Appel API sans gestion d'erreur
  - `race_condition` : Appels concurrents sur même state
  - `missing_auth` : Endpoint sensible sans authentification
  - `dead_code` : Code jamais exécuté dans le flux

## [2.2.8] - 2025-01-05

### 🐛 Corrections

- **Correction du mode direct Claude Code** : Ajout des flags manquants pour le mode non-interactif
  - Ajout de `--print` pour le mode non-interactif
  - Ajout de `--output-format text` pour la sortie texte
  - Ajout de `--no-session-persistence` pour éviter les problèmes de session
  - Résout le timeout de 300s qui se produisait en mode arrière-plan

- **Nouvelle méthode `test_claude_code_execution()`** : Test complet de l'exécution
  - Teste que Claude Code peut réellement exécuter des prompts
  - Utilisé par `aetheris fix --test`

## [2.2.7] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Flag `--version`** : Affichage de la version avec `aetheris --version` ou `aetheris -v`

- **Mode direct pour Claude Code** : Exécution en arrière-plan (sans fenêtre terminal)
  - Nouvelle méthode `run_claude_direct()` pour exécution directe
  - Nouvelle méthode `test_claude_code()` pour vérifier la connexion
  - Nouvelle méthode `fix_bug_direct()` pour correction sans fenêtre
  - Mode direct par défaut (plus fiable que le mode terminal)

- **Flag `--test` pour Claude Code** : Test de connexion avant correction
  - `aetheris fix --test` vérifie si Claude Code fonctionne
  - Affiche la version et effectue un test de communication

- **Flag `--terminal` pour Claude Code** : Mode fenêtre terminal optionnel
  - `aetheris fix --terminal` ouvre Claude Code dans une nouvelle fenêtre
  - Utile pour le débogage interactif

### 🐛 Corrections

- **Correction du terminal vide sur Windows** : Le mode direct évite les problèmes d'échappement

## [2.2.6] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Mode direct pour Claude Code (initial)** : Première implémentation du mode arrière-plan
- **Workflow publish avec workflow_dispatch** : Permet le déclenchement manuel de la publication

## [2.2.5] - 2025-01-05

### 🐛 Corrections

- **Correction severity 'info' dans impact analyzer** : Ajout de la clé 'info' manquante
  - Résout l'erreur `KeyError: 'info'` dans l'analyse d'impact
  - Les issues de sécurité de niveau 'info' sont maintenant correctement traitées

## [2.2.4] - 2025-01-05

### 🐛 Corrections

- **Correction du parser .env** : Les commentaires inline sont maintenant ignorés
  - `API_KEY=abc123  # commentaire` fonctionne correctement
  - Résout l'erreur "API key not valid" causée par les commentaires

- **Validation de la clé API au démarrage** : Test automatique de la clé
  - Affichage de la clé masquée pour debug
  - Message d'erreur clair si la clé est invalide
  - Arrêt immédiat au lieu de continuer avec des erreurs

## [2.2.3] - 2025-01-05

### 🐛 Corrections

- **Restauration du modèle gemini-3-pro-preview** : Le modèle existe bien
  - Revert de la v2.2.2 qui avait changé le modèle par erreur
  - Le modèle `gemini-3-pro-preview` est le bon modèle par défaut

## [2.2.1] - 2025-01-05

### 🐛 Corrections

- **Correction du SDK google-genai** : Mise à jour des imports dans CLI et main.py
  - Changement de `import google.generativeai` vers `from google import genai`
  - Alignement avec le nouveau SDK google-genai>=1.0.0

- **Options de configuration v2.2.0** : Les nouvelles options Gemini sont maintenant passées à AnalysisConfig
  - `ENABLE_STRUCTURED_OUTPUTS`, `ENABLE_THINKING`, `ENABLE_CODE_EXECUTION`, etc.
  - Documentation des incompatibilités dans `.env.example`

- **Exclusion des fichiers cachés** : Les fichiers commençant par `.` sont maintenant exclus de l'analyse
  - Respect des règles `.gitignore`
  - Meilleure performance et pertinence des analyses

### 📚 Documentation

- Mise à jour de `.env.example` avec les incompatibilités entre fonctionnalités Gemini
- Ajout de `ENABLE_GOOGLE_SEARCH` comme option de configuration

## [2.2.0] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Migration vers le nouveau SDK google-genai** : Passage de `google-generativeai` à `google-genai>=1.0.0`
  - Nouvelle architecture client-based (`genai.Client`)
  - API plus moderne et performante
  - Support des dernières fonctionnalités Gemini

- **Modèle par défaut Gemini 3 Pro Preview** : `gemini-3-pro-preview`
  - Input: 1,048,576 tokens
  - Output: 65,536 tokens
  - Support de toutes les fonctionnalités avancées

- **Structured Outputs (Sorties structurées)** : Réponses JSON garanties via schémas Pydantic
  - Nouvelle méthode `generate_structured()` dans GeminiProvider
  - Nouvelle méthode `_call_ai_structured()` dans BaseAgent
  - Schémas Pydantic dans `src/models/analysis_schemas.py`
  - Validation automatique des réponses

- **Code Execution (Exécution de code)** : Le modèle peut exécuter du Python en sandbox
  - Nouvelle méthode `generate_with_code_execution()`
  - Nouvelle méthode `_call_ai_with_code_execution()` dans BaseAgent
  - Analyse dynamique avec parsing AST, calcul de métriques, etc.

- **Thinking/Reasoning (Raisonnement)** : Affichage du processus de raisonnement du modèle
  - Nouvelle méthode `generate_with_thinking()`
  - Nouvelle méthode `_call_ai_with_thinking()` dans BaseAgent
  - Budget de tokens configurable (`thinking_budget`)

- **Context Caching (Cache de contexte)** : Réduction des coûts API (~50%)
  - Nouvelle méthode `create_cache()` pour créer des caches
  - Nouvelle méthode `generate_with_cache()` pour utiliser les caches
  - TTL configurable (`cache_ttl_seconds`)

- **Batch API (API Batch)** : Traitement en lot à coût réduit (-50%)
  - Nouvelle méthode `create_batch_job()` pour créer des jobs batch
  - Mode batch activable via configuration

- **Function Calling (Appel de fonction)** : Appel automatique de fonctions Python
  - Nouvelle méthode `generate_with_tools()` avec fonctions Python
  - Support des outils personnalisés

- **Google Search (Recherche web intégrée)** : Grounding avec recherche web
  - Nouvelle méthode `generate_with_search()` pour recherche en temps réel

### 🔧 Modifications

- **Configuration** : Nouvelles options dans `AnalysisConfig`
  - `enable_code_execution` : Activer l'exécution de code
  - `enable_structured_outputs` : Activer les sorties structurées (défaut: true)
  - `enable_function_calling` : Activer l'appel de fonctions
  - `enable_thinking` : Activer le mode thinking
  - `thinking_budget` : Budget de tokens pour le raisonnement
  - `enable_context_caching` : Activer le cache de contexte
  - `cache_ttl_seconds` : Durée de vie du cache API
  - `enable_batch_mode` : Activer le mode batch
  - `enable_google_search` : Activer la recherche Google intégrée

- **BaseAgent** : Nouvelles méthodes pour les fonctionnalités avancées
  - `_call_ai_structured()` pour les sorties structurées
  - `_call_ai_with_thinking()` pour le raisonnement visible
  - `_call_ai_with_code_execution()` pour l'exécution de code

- **SecurityAnalysisAgent** : Utilisation des Structured Outputs
  - Analyse de sécurité avec schémas Pydantic validés
  - Champs CWE et OWASP enrichis

- **CodeAnalysisExpert** : Nouvelles méthodes avancées
  - `analyze_file_structured()` avec Structured Outputs
  - `analyze_with_code_execution()` pour analyses dynamiques

- **SecurityIssue (data_models)** : Nouveaux champs
  - `cwe_id` : Identifiant CWE (ex: CWE-79)
  - `owasp_category` : Catégorie OWASP (ex: A01:2021)

### 📦 Nouveaux modules

- `src/core/gemini_config.py` : Configuration des fonctionnalités avancées Gemini
  - `GeminiFeatureConfig` : Configuration par requête
  - `CodeExecutionResult` : Résultat d'exécution de code
  - `ThinkingResult` : Résultat avec raisonnement
  - `CacheConfig` : Configuration du cache
  - `BatchRequest/BatchJobInfo` : Gestion des jobs batch
  - Helpers : `supports_code_execution()`, `supports_thinking()`, etc.

- `src/models/analysis_schemas.py` : Schémas Pydantic pour Structured Outputs
  - `Severity`, `IssueCategory` : Enums pour les issues
  - `SecurityIssue`, `SecurityAnalysisResult` : Analyse de sécurité
  - `CodeMetrics`, `CodeIssue`, `Dependency` : Métriques et issues
  - `FileAnalysisResult` : Résultat complet d'analyse
  - `ArchitecturePattern`, `LayerAnalysis`, `ArchitectureAnalysisResult` : Architecture
  - `QualityDimension`, `QualityAssuranceResult` : Qualité
  - `VulnerabilityInfo`, `DependencyVulnerabilityResult` : Vulnérabilités

### 📦 Dépendances

- `google-genai>=1.0.0` remplace `google-generativeai>=0.8.5`
- `pydantic>=2.0.0` pour les schémas structurés

### 📝 Documentation

- Mise à jour du README avec les nouvelles fonctionnalités Gemini
- Exemples d'utilisation des Structured Outputs
- Documentation des méthodes avancées

## [2.1.0] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Commande `aetheris fix`** : Nouvelle commande CLI pour corriger les bugs détectés avec Claude Code
  - Lance Claude Code dans une fenêtre séparée pour chaque bug
  - Correction séquentielle avec confirmation utilisateur
  - Filtrage par sévérité (`--severity critical|high|medium|low`)
  - Mode automatique (`--auto`) sans confirmations entre les bugs
  - Détection automatique et support multi-plateforme (Windows, macOS, Linux)

- **Extraction des exports** : Analyse des exports de chaque fichier pour comprendre les relations
  - Support TypeScript/JavaScript (export default, export {}, export function/class)
  - Support Python (__all__, fonctions/classes publiques)
  - Support Dart (export, classes/fonctions publiques)

- **Graphe de dépendances inverse** : Savoir "qui dépend de ce fichier"
  - Construction automatique du graphe inverse
  - Méthode `get_dependents()` pour trouver les fichiers impactés
  - Profondeur configurable

- **Analyse d'impact des bugs** : Calcul automatique des fichiers impactés par chaque bug
  - IDs de bugs uniques au format `BUG-XXXXXXXX`
  - Extraction des bugs depuis les analyses (sécurité, risques, incohérences)
  - Cache des bugs dans `.bugs_cache.json`

### 🔧 Modifications

- **Orchestrateur** : Ajout de 3 nouveaux stages de workflow
  - `EXPORT_ANALYSIS` : Extraction des exports
  - `REVERSE_DEPENDENCY` : Construction du graphe inverse
  - `IMPACT_ANALYSIS` : Analyse d'impact des bugs

- **Configuration** : Nouvelles options
  - `enable_export_analysis` : Activer l'extraction des exports
  - `enable_reverse_dependency` : Activer le graphe de dépendances inverses
  - `enable_impact_analysis` : Activer l'analyse d'impact
  - `max_impact_depth` : Profondeur maximale pour l'analyse d'impact
  - `enable_claude_code_fix` : Activer l'intégration Claude Code
  - `fix_severity_threshold` : Seuil de sévérité minimale pour les corrections

### 📦 Nouveaux modules

- `src/services/export_analyzer.py` : Extraction des exports multi-langage
- `src/services/impact_analyzer.py` : Analyse d'impact des bugs
- `src/services/claude_code_integration.py` : Intégration avec Claude Code CLI

### 📝 Documentation

- Mise à jour du README avec documentation complète de `aetheris fix`
- Mise à jour de `docs/PLUGINS.md` avec les nouveaux hooks
- Exemples d'utilisation des nouveaux stages

## [2.0.1] - 2025-01-16

### 🔧 Corrections

- **Migration de dépendance** : Remplacement de `duckduckgo-search` par `ddgs` (package renommé)
- **Correction modèle Gemini** : Changement du modèle par défaut de `gemini-1.5-flash` vers `gemini-1.5-pro` pour compatibilité avec l'API v1beta
- **Mise à jour dépendances** : `google-generativeai>=0.8.5` pour meilleur support des modèles récents

### 📦 Dépendances

- `ddgs>=1.0.0` remplace `duckduckgo-search>=6.0.0`
- `google-generativeai>=0.8.5` (au lieu de >=0.8.0)

## [2.0.0] - 2025-01-16

### ✨ Nouvelles fonctionnalités

- **Orchestrateur dédié** : Système d'orchestration séparé pour une meilleure maintenabilité et testabilité
- **Système de cache** : Cache basé sur git SHA + timestamp pour réduire les coûts API de 60-80%
- **Parallélisation intelligente** : Analyse des fichiers indépendants en parallèle basée sur le graphe de dépendances
- **Système de priorités** : Priorisation automatique des fichiers modifiés dans les PR (HIGH) et leurs dépendances (MEDIUM)
- **Métriques et monitoring** : Collecte complète de métriques de performance avec export JSON
- **Analyse incrémentale améliorée** : Détection automatique des fichiers dépendants avec profondeur configurable
- **Gestion d'erreurs améliorée** : Circuit breaker et backoff exponentiel pour une meilleure résilience

### 🔧 Modifications

- **Architecture** : Refactorisation de `CodeAnalyzer` pour utiliser un orchestrateur interne
- **Workflow** : Système de workflow avec étapes, dépendances et hooks
- **Configuration** : Nouvelles options (`enable_cache`, `cache_ttl_days`, `analyze_dependent_files`, `max_dependency_depth`, `enable_metrics`, `enable_priority_analysis`)
- **BaseAgent** : Intégration du circuit breaker pour éviter les appels répétés en cas d'erreur
- **Orchestrateur** : Support des hooks pour extensibilité et collecte de métriques

### 📦 Nouveaux modules

- `src/core/orchestrator.py` : Orchestrateur principal avec système de workflow
- `src/core/cache.py` : Système de cache avec stockage disque
- `src/core/error_handler.py` : Gestion d'erreurs avec circuit breaker
- `src/core/parallel_analyzer.py` : Parallélisation intelligente basée sur dépendances
- `src/core/priority_manager.py` : Gestionnaire de priorités pour PR reviews
- `src/core/metrics.py` : Collecteur de métriques de performance

### 📝 Documentation

- Documentation complète du système de plugins/hooks dans `docs/PLUGINS.md`
- Exemples d'utilisation et guide pour créer des plugins personnalisés

### 🔄 Compatibilité

- **Backward compatible** : L'API publique de `CodeAnalyzer` reste inchangée
- Les nouvelles fonctionnalités sont activées par défaut mais peuvent être désactivées via configuration

## [1.1.0] - 2025-01-15

### ✨ Nouvelles fonctionnalités

- **Affichage du reasoning** : Possibilité d'afficher le processus de raisonnement des modèles AI (si disponible)
- **Support OpenAI o1** : Support du reasoning pour les modèles o1-preview et o1-mini d'OpenAI
- **Panneau de reasoning** : Affichage du reasoning dans un panneau Rich dédié avec syntax highlighting

### 🔧 Modifications

- **AIProvider** : Ajout de la méthode `generate_content_with_reasoning()` pour récupérer le reasoning
- **BaseAgent** : Ajout de `_call_ai_with_reasoning()` pour utiliser le reasoning si activé
- **Configuration** : Ajout de l'option `show_reasoning` dans `AnalysisConfig`
- **Agents** : Passage de `progress_manager` aux agents pour afficher le reasoning

### 📝 Documentation

- Mise à jour du README avec explication du reasoning
- Ajout de la variable d'environnement `SHOW_REASONING` dans la documentation

## [1.0.9] - 2025-01-15

### ✨ Nouvelles fonctionnalités

- **Barre de progression moderne** : Ajout d'une barre de progression interactive avec Rich pour un suivi visuel clair de l'analyse
- **Affichage en temps réel** : Progression détaillée pour chaque étape (scan, analyse, rapports)
- **Statistiques visuelles** : Affichage du temps écoulé, temps restant et pourcentage de progression

### 🔧 Modifications

- **CodeAnalyzer** : Intégration de `ProgressManager` pour remplacer les logs simples par des barres de progression
- **Points d'entrée** : `main.py` et `src/cli.py` créent automatiquement un `ProgressManager` si le terminal le supporte
- **Fallback automatique** : Si Rich n'est pas disponible ou si on n'est pas dans un terminal interactif, le système utilise les logs simples

### 📦 Dépendances

- Ajout de `rich>=13.0.0` pour les barres de progression modernes

### 📝 Documentation

- Mise à jour du README avec description de la barre de progression

## [1.0.8] - 2025-01-15

### ✨ Nouvelles fonctionnalités

- **Support multi-fournisseurs AI** : Ajout du support pour OpenAI, Claude (Anthropic) et Gemini
- **Choix du modèle** : Possibilité de choisir le modèle AI selon le fournisseur sélectionné
- **Abstraction des providers** : Architecture modulaire permettant d'ajouter facilement de nouveaux fournisseurs AI
- **Documentation des coûts** : Ajout d'un tableau détaillé des coûts d'analyse dans le README
- **Modèles à jour** : Mise à jour avec les derniers modèles disponibles (Gemini 2.5 Pro, GPT-4o, Claude 3.5 Sonnet)

### 🔧 Modifications

- **Configuration** : Remplacement de `gemini_api_key` et `gemini_model` par `ai_api_key` et `ai_model` génériques
- **Variables d'environnement** : Ajout de `AI_PROVIDER` pour choisir le fournisseur (gemini, openai, claude)
- **BaseAgent** : Refactorisation pour utiliser l'abstraction `AIProvider` au lieu de Gemini directement
- **CodeGenerator** : Adaptation pour utiliser l'abstraction `AIProvider`

### 📦 Dépendances

- Ajout de `openai>=1.0.0` pour le support OpenAI
- Ajout de `anthropic>=0.25.0` pour le support Claude

### 📝 Documentation

- Ajout de la section "Choix du fournisseur AI" dans le README
- Ajout du tableau des modèles supportés par fournisseur
- Ajout de la section "Coûts d'analyse" avec estimations pour différents scénarios
- Mise à jour des instructions de configuration pour les différents fournisseurs

### 🔄 Compatibilité

- **Breaking change** : Les variables `GEMINI_API_KEY` et `GEMINI_MODEL` sont remplacées par `AI_PROVIDER`, `AI_API_KEY` (selon provider) et `AI_MODEL`
- Pour la rétrocompatibilité, si `AI_PROVIDER` n'est pas défini, le système utilise Gemini par défaut

## [1.0.7] - 2025-11-21

### 🔧 Corrections et améliorations

- **Dépendance obligatoire** : `ddgs` (anciennement `duckduckgo-search`) est maintenant une dépendance obligatoire au lieu d'optionnelle
- **Simplification du code** : Suppression des vérifications conditionnelles pour `ddgs` dans tout le codebase
- **Amélioration des imports** : Simplification des imports dans `main.py` et `src/cli.py` avec gestion d'erreur unifiée
- **Suppression des avertissements inutiles** : L'avertissement pour `ddgs` ne s'affiche plus si la recherche web est désactivée dans la configuration

### 📦 Dépendances

- `ddgs>=1.0.0` (anciennement `duckduckgo-search>=6.0.0`) déplacé des dépendances optionnelles vers les dépendances principales dans `pyproject.toml` et `requirements.txt`

### 📝 Documentation

- Mise à jour du README pour indiquer que `ddgs` est une dépendance obligatoire

## [1.0.6] - 2025-11-21

### 🔧 Corrections et améliorations

- **Workflows manuels uniquement** : Les workflows `code-review.yml` et `run-aetheris.yml` ne s'exécutent maintenant que manuellement
- **Installation PyPI** : Le workflow `run-aetheris.yml` utilise maintenant PyPI au lieu de GitHub Packages
- **Documentation** : Mise à jour complète de README, CHANGELOG, .gitignore, .gitattributes et scripts
- **Correction URLs** : Correction des URLs du repository dans pyproject.toml
- **Amélioration .gitignore** : Ajout des fichiers de packaging Python (build/, dist/, \*.egg-info, etc.)
- **Amélioration .gitattributes** : Ajout des règles de fin de ligne pour différents types de fichiers

### 📝 Documentation

- Mise à jour du README avec les liens PyPI et repository GitHub
- Documentation améliorée des scripts utilitaires
- CHANGELOG mis à jour avec toutes les versions

## [1.0.5] - 2025-11-21

### 🚀 Publication sur PyPI

- **Publication sur PyPI** : Le package est maintenant disponible sur PyPI (Python Package Index)
- **Installation simplifiée** : Plus besoin de `--extra-index-url`, installez simplement avec `pip install adryserage-aetheris`
- Correction du workflow de publication (suppression de GitHub Packages avec URL incorrecte)
- Workflow GitHub Actions mis à jour pour publier uniquement sur PyPI

### 📦 Package

- Nom du package : `adryserage-aetheris`
- Commande CLI : `aetheris` (inchangée)
- Installation : `pip install adryserage-aetheris` (depuis PyPI)

## [1.0.4] - 2025-11-21

### 🔧 Corrections

- Ajout du support PyPI dans le workflow de publication
- Configuration du token PyPI comme secret GitHub
- Mise à jour des workflows avec les dernières versions des actions GitHub (checkout@v4, setup-python@v5)

## [1.0.3] - 2025-11-21

### 🚀 Publication

- Renommage du package Python en `adryserage-aetheris` pour publication
- Configuration complète du package avec `pyproject.toml`
- Ajout de la commande CLI `aetheris` avec sous-commandes (`aetheris analysis`)
- Workflow GitHub Actions pour publication automatique lors des tags de version
- Documentation mise à jour avec instructions d'installation

## [1.0.2] - 2025-11-21

### 🔧 Corrections

- Correction de la commande `gh pr diff` qui utilisait des flags invalides (`--json` et `--jq` non supportés)
- Remplacement par `gh pr view` avec filtrage approprié pour exclure les fichiers supprimés
- Alignement du comportement entre les modes PR et commit pour exclure les fichiers supprimés (cohérence avec `git diff --diff-filter=ACMR`)

## [1.0.1] - 2025-11-21

### 🔧 Corrections

- Correction du workflow GitHub Actions pour utiliser `gh pr view` au lieu de `gh pr diff` pour récupérer les fichiers modifiés dans les pull requests

## [1.0.0] - 2025-11-21

### ✨ Fonctionnalités

- Ajout du support pour analyser uniquement les fichiers modifiés dans le Code Analyzer
- Support des analyses ciblées pour les Pull Requests et commits
- Mode `--changed-files-only` avec support des fichiers spécifiés via arguments ou variables d'environnement
- Support du numéro de PR pour enrichir les rapports d'analyse

### 📚 Documentation

- Documentation complète du système dans le README.md
- Instructions d'installation et de configuration détaillées
- Guide d'utilisation avec exemples
- Documentation des agents d'analyse et de leurs fonctionnalités

### 🏗️ Infrastructure

- Workflow GitHub Actions pour l'analyse automatique de code
- Support des analyses complètes et ciblées
- Génération automatique de rapports en tant qu'artifacts GitHub

### 🎉 Version initiale

- Système d'analyse de code multi-agents avec 6 agents spécialisés :
  - Code Analysis Expert (CAE)
  - Architect Analysis Agent (AAA)
  - Security Analysis Agent (SSA)
  - Code Metrics Agent (CMA)
  - Dependency Vulnerability Agent (DVA)
  - Quality Assurance Agent (QAA)
- Support de multiples langages de programmation
- Analyse des vulnérabilités via l'API OSV
- Génération de rapports détaillés en Markdown
- Configuration flexible via variables d'environnement

[2.1.0]: https://github.com/adryserage/aetheris/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/adryserage/aetheris/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/adryserage/aetheris/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/adryserage/aetheris/compare/v1.0.9...v1.1.0
[1.0.9]: https://github.com/adryserage/aetheris/compare/v1.0.8...v1.0.9
[1.0.8]: https://github.com/adryserage/aetheris/compare/v1.0.7...v1.0.8
[1.0.7]: https://github.com/adryserage/aetheris/compare/v1.0.6...v1.0.7
[1.0.6]: https://github.com/adryserage/aetheris/compare/v1.0.5...v1.0.6
[1.0.5]: https://github.com/adryserage/aetheris/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/adryserage/aetheris/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/adryserage/aetheris/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/adryserage/aetheris/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/adryserage/aetheris/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/adryserage/aetheris/releases/tag/v1.0.0
