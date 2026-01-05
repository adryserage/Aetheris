# Aetheris by Adryan - Système d'Analyse de Code Multi-Agents

[![PyPI version](https://badge.fury.io/py/adryserage-aetheris.svg)](https://badge.fury.io/py/adryserage-aetheris)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/adryserage/code_reviewer/code-review.yml?label=CI)](https://github.com/adryserage/code_reviewer/actions)
[![PyPI downloads](https://img.shields.io/pypi/dm/adryserage-aetheris.svg)](https://pypi.org/project/adryserage-aetheris/)
[![GitHub stars](https://img.shields.io/github/stars/adryserage/code_reviewer.svg?style=social&label=Star)](https://github.com/adryserage/code_reviewer)

Système d'analyse de code automatisé utilisant plusieurs agents coopérants pour fournir une analyse complète de la qualité, de la sécurité et de l'architecture de votre codebase.

## 🎯 Fonctionnalités

### Version 2.0.0 - Améliorations Majeures

- **🎼 Orchestrateur dédié** : Système d'orchestration séparé avec workflow à étapes, dépendances et hooks pour une meilleure maintenabilité
- **🚀 Cache intelligent** : Réduction des coûts API de 60-80% grâce au cache basé sur git SHA
- **⚡ Parallélisation intelligente** : Analyse des fichiers indépendants en parallèle pour des performances optimales
- **🎯 Système de priorités** : Priorisation automatique des fichiers PR pour des reviews plus rapides
- **📊 Métriques et monitoring** : Collecte complète de métriques de performance avec export JSON
- **🔄 Analyse incrémentale** : Détection automatique des fichiers dépendants avec profondeur configurable
- **🛡️ Gestion d'erreurs robuste** : Circuit breaker et backoff exponentiel pour une meilleure résilience
- **🔌 Système de plugins** : Hooks extensibles pour personnaliser le workflow (voir `docs/PLUGINS.md`)

### Version 2.1.0 - Correction de Bugs avec Claude Code

- **🔧 Commande `aetheris fix`** : Correction automatique des bugs avec Claude Code
- **📤 Analyse des exports** : Extraction des exports (TS/JS, Python, Dart) pour comprendre les relations
- **🔙 Graphe de dépendances inverse** : Savoir "qui dépend de ce fichier" pour l'analyse d'impact
- **💥 Analyse d'impact** : Calcul automatique des fichiers impactés par chaque bug
- **🔢 IDs de bugs uniques** : Chaque bug détecté a un ID unique (ex: `BUG-A1B2C3D4`)

### Version 2.2.0 - Gemini 3 Pro Preview & Fonctionnalités Avancées

- **🧠 Structured Outputs** : Réponses JSON garanties validées via Pydantic pour une analyse plus fiable
- **💭 Thinking/Reasoning** : Affichage du processus de raisonnement du modèle pour les analyses complexes
- **⚡ Code Execution** : Exécution de code Python en sandbox pour des analyses dynamiques (métriques AST, etc.)
- **🔧 Function Calling** : Appel automatique de fonctions Python par le modèle
- **📦 Context Caching** : Réduction des coûts API de ~50% via le cache de contexte Gemini
- **📊 Batch API** : Traitement en lot à -50% du prix pour les analyses volumineuses
- **🔍 Google Search** : Recherche web intégrée (grounding) pour des analyses enrichies
- **🛡️ Sécurité améliorée** : Identifiants CWE et catégories OWASP dans les rapports de sécurité
- **📈 Modèle Gemini 3 Pro Preview** : Support du nouveau modèle avec 1M tokens en entrée et 65K en sortie

### Architecture du Système

Le système utilise un **orchestrateur dédié** (`AnalysisOrchestrator`) qui coordonne l'exécution du workflow d'analyse avec :

- **Workflow à étapes** : Chaque étape (scan, analyse, rapports) est gérée indépendamment
- **Gestion des dépendances** : Les étapes s'exécutent dans l'ordre respectant leurs dépendances
- **Système de hooks** : Points d'extension pour personnaliser le comportement
- **Gestion d'erreurs** : Retry automatique et gestion des erreurs non critiques
- **Collecte de métriques** : Suivi automatique des performances à chaque étape

### Agents d'Analyse

Le système utilise **6 agents spécialisés** qui travaillent ensemble pour analyser votre code :

1. **Code Analysis Expert (CAE)**
   - Analyse chaque fichier individuellement
   - Identifie les objectifs et fonctions principales
   - Détecte les points forts et bonnes pratiques
   - Signale les risques et dettes techniques
   - Propose des suggestions d'amélioration
   - Analyse les dépendances entre fichiers

2. **Architect Analysis Agent (AAA)**
   - Produit une vue d'ensemble de l'architecture
   - Identifie les patterns architecturaux
   - Évalue la cohérence inter-modules
   - Détecte les redondances et couplages excessifs
   - Propose un plan de refactoring

3. **Security Analysis Agent (SSA)**
   - Détecte les vulnérabilités de sécurité
   - Identifie les injections (SQL, XSS, etc.)
   - Signale les secrets codés en dur
   - Vérifie la cryptographie faible
   - Analyse les problèmes d'authentification

4. **Code Metrics Agent (CMA)**
   - Calcule les métriques de code (complexité cyclomatique, etc.)
   - Détecte le code dupliqué
   - Mesure la profondeur d'imbrication
   - Calcule l'indice de maintenabilité

5. **Dependency Vulnerability Agent (DVA)**
   - Analyse les vulnérabilités des dépendances via l'API OSV
   - Supporte npm, PyPI, Pub (Dart)
   - Identifie les CVE et vulnérabilités connues
   - Propose les versions corrigées

6. **Quality Assurance Agent (QAA)**
   - Synthétise toutes les analyses
   - Génère un score de qualité global
   - Crée un plan d'action priorisé
   - Propose une roadmap d'amélioration

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Clé API pour l'un des fournisseurs supportés :
  - **Gemini** : [Obtenir une clé](https://makersuite.google.com/app/apikey)
  - **OpenAI** : [Obtenir une clé](https://platform.openai.com/api-keys)
  - **Claude** : [Obtenir une clé](https://console.anthropic.com/)

### Installation depuis PyPI (Recommandé)

Aetheris est disponible sur PyPI sous le nom `adryserage-aetheris`. Installation simple :

```bash
pip install adryserage-aetheris
```

C'est tout ! Le package est maintenant installé et la commande `aetheris` est disponible.

**Note** : Après l'installation, la commande CLI `aetheris` est disponible dans votre terminal.

### Installation depuis les sources

Si vous préférez installer depuis les sources :

```bash
git clone https://github.com/adryserage/aetheris.git
cd aetheris
pip install -r requirements.txt
```

Ou installez le package en mode développement :

```bash
git clone https://github.com/adryserage/aetheris.git
cd aetheris
pip install -e .
```

### Dépendances

- `google-genai` - Nouveau SDK Gemini avec Structured Outputs, Thinking, Code Execution (v2.2.0+)
- `pydantic` - Validation des schémas JSON pour les Structured Outputs (v2.2.0+)
- `openai` - API OpenAI pour l'analyse de code
- `anthropic` - API Claude (Anthropic) pour l'analyse de code
- `pathspec` - Gestion des patterns .gitignore
- `requests` - Requêtes HTTP pour l'API OSV (version >=2.32.0 pour corriger les vulnérabilités CVE-2024-47081 et CVE-2024-35195)
- `pyyaml` - Parsing des fichiers YAML (pubspec.yaml pour Dart/Flutter)
- `ddgs` - Recherche web pour enrichir les analyses (anciennement duckduckgo-search)

## 🏗️ Structure du Projet

Le projet est organisé en modules pour une meilleure maintenabilité :

```text
aetheris/
├── src/
│   ├── core/              # Modules principaux
│   │   ├── config.py      # Configuration (AnalysisConfig, load_env_file)
│   │   ├── logger.py     # Logging et encodage UTF-8
│   │   ├── analyzer.py   # Analyseur principal (CodeAnalyzer)
│   │   ├── orchestrator.py  # Orchestrateur avec système de workflow
│   │   ├── ai_providers.py  # Providers AI (Gemini, OpenAI, Claude) avec fonctionnalités avancées
│   │   ├── gemini_config.py  # Configuration des fonctionnalités avancées Gemini (v2.2.0+)
│   │   ├── cache.py      # Système de cache pour réduire les coûts API
│   │   ├── error_handler.py  # Gestion d'erreurs avec circuit breaker
│   │   ├── parallel_analyzer.py  # Parallélisation intelligente
│   │   ├── priority_manager.py  # Gestionnaire de priorités
│   │   ├── metrics.py    # Collecteur de métriques de performance
│   │   └── progress.py    # Gestionnaire de progression
│   ├── models/           # Modèles de données
│   │   ├── data_models.py  # Dataclasses (FileAnalysis, SecurityIssue, etc.)
│   │   └── analysis_schemas.py  # Schémas Pydantic pour Structured Outputs (v2.2.0+)
│   ├── agents/           # Agents d'analyse
│   │   ├── base_agent.py  # Classe de base pour tous les agents
│   │   ├── code_analysis_expert.py
│   │   ├── architect_analysis_agent.py
│   │   ├── security_analysis_agent.py
│   │   ├── code_metrics_agent.py
│   │   ├── dependency_vulnerability_agent.py
│   │   └── quality_assurance_agent.py
│   └── services/         # Services utilitaires
│       ├── code_generator.py
│       ├── documentation_searcher.py
│       └── dependency_analyzer.py
├── docs/                 # Documentation
│   └── PLUGINS.md        # Documentation du système de plugins/hooks
├── main.py               # Point d'entrée principal (pour développement)
├── src/
│   └── cli.py           # Interface CLI avec sous-commandes
├── scripts/              # Scripts utilitaires
│   ├── analyze_changes.py  # Analyse des fichiers modifiés
│   ├── extract_release_notes.py  # Extraction des notes de release
│   ├── create_missing_releases.py  # Création de releases GitHub
│   └── README.md
├── pyproject.toml        # Configuration du package Python
├── requirements.txt      # Dépendances Python
└── README.md            # Documentation
```

### Architecture Modulaire

- **`src/core/`** : Contient l'analyseur principal (`CodeAnalyzer`), l'orchestrateur (`AnalysisOrchestrator`), le cache, la gestion d'erreurs, la parallélisation, les priorités, les métriques et les utilitaires de configuration
- **`src/models/`** : Définit les structures de données utilisées pour échanger des informations entre les composants
- **`src/agents/`** : Chaque agent est un module indépendant héritant de `BaseAgent` pour la logique commune
- **`src/services/`** : Services utilitaires réutilisables (génération de code, recherche web, analyse de dépendances)
- **`docs/`** : Documentation du système, notamment le guide des plugins/hooks

Cette structure modulaire facilite :

- La maintenance et l'extension du code
- La réutilisation des composants
- Les tests unitaires
- La compréhension de l'architecture
- L'extensibilité via le système de hooks/plugins

## ⚙️ Configuration

### Choix du fournisseur AI

Aetheris supporte maintenant **trois fournisseurs AI** : Google Gemini, OpenAI et Anthropic Claude. Vous pouvez choisir le fournisseur et le modèle qui convient le mieux à vos besoins et à votre budget.

#### Configuration du fournisseur

Créez un fichier `.env` à la racine du projet :

```env
# Choisir le fournisseur (gemini, openai, claude)
AI_PROVIDER=gemini

# Clé API selon le fournisseur choisi
GEMINI_API_KEY=votre_cle_api_ici        # Pour Gemini
# OU
OPENAI_API_KEY=votre_cle_api_ici         # Pour OpenAI
# OU
ANTHROPIC_API_KEY=votre_cle_api_ici      # Pour Claude

# Modèle à utiliser (optionnel, défaut selon provider)
AI_MODEL=gemini-2.5-flash
```

Ou définissez les variables d'environnement :

**Windows (PowerShell):**

```powershell
$env:AI_PROVIDER='openai'
$env:OPENAI_API_KEY='votre_cle_api_ici'
```

**Linux/Mac:**

```bash
export AI_PROVIDER=claude
export ANTHROPIC_API_KEY=votre_cle_api_ici
```

#### Modèles supportés

##### Modèles avec reasoning (affichage du processus de raisonnement disponible via l'API)

| Fournisseur | Modèles avec reasoning  | Modèle par défaut | Notes                                                                                                            |
| ----------- | ----------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------- |
| **OpenAI**  | `o1-preview`, `o1-mini` | `o1-preview`      | Ces modèles exposent leur processus de raisonnement étape par étape via le champ `reasoning` dans la réponse API |

> **Note** : Seuls les modèles OpenAI `o1-preview` et `o1-mini` exposent actuellement leur reasoning via l'API. D'autres modèles (comme o3, GPT-5) peuvent avoir des capacités de reasoning internes mais ne l'exposent pas via l'API de la même manière.

##### Modèles sans reasoning (affichage standard)

| Fournisseur | Modèles disponibles                                                                                                                           | Modèle par défaut            | Notes                             |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | --------------------------------- |
| **Gemini**  | `gemini-2.5-flash` ⭐, `gemini-2.5-pro`, `gemini-2.0-flash-exp`, `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-pro` | `gemini-2.5-flash`       | Thinking disponible pour gemini-2.5+ |
| **OpenAI**  | `gpt-4o`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`, `gpt-4-turbo-preview`                                                                      | `gpt-4o`                     | Pas de reasoning exposé via l'API |
| **Claude**  | `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-haiku-20240307`                                                             | `claude-3-5-sonnet-20241022` | Pas de reasoning exposé via l'API |

##### Gemini 3 Pro Preview - Fonctionnalités Avancées (v2.2.0+)

Le modèle `gemini-2.5-flash` offre des capacités uniques :

| Fonctionnalité | Description | Activation |
|----------------|-------------|------------|
| **Structured Outputs** | Réponses JSON validées via Pydantic | `ENABLE_STRUCTURED_OUTPUTS=true` |
| **Thinking** | Affichage du processus de raisonnement | `ENABLE_THINKING=true` |
| **Code Execution** | Exécution Python en sandbox | `ENABLE_CODE_EXECUTION=true` |
| **Context Caching** | Cache de contexte (-50% coût) | `ENABLE_CONTEXT_CACHING=true` |
| **Batch API** | Traitement en lot (-50% coût) | `ENABLE_BATCH_MODE=true` |

**Limites du modèle :**
- Input : 1 048 576 tokens (1M)
- Output : 65 536 tokens (65K)

> **Note** : Pour utiliser le mode reasoning avec les modèles OpenAI `o1-preview` ou `o1-mini`, définissez `AI_MODEL=o1-preview` (ou `o1-mini`) et `SHOW_REASONING=true`. Le reasoning s'affichera dans un panneau dédié pendant l'analyse.

**Note importante** :

- **Codex (OpenAI)** : Le modèle Codex original a été déprécié. Pour l'analyse de code, utilisez **GPT-4o** ou **GPT-4 Turbo** qui offrent d'excellentes performances pour le code.
- Certains modèles spécialisés (comme GPT-5 Codex pour OpenAI ou Claude Opus 4.1) peuvent nécessiter un accès spécial ou ne pas être disponibles via l'API standard. Consultez la documentation officielle de chaque fournisseur pour les modèles les plus récents et leur disponibilité.

#### Obtenir les clés API

- **Gemini** : [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OpenAI** : [OpenAI Platform](https://platform.openai.com/api-keys)
- **Claude** : [Anthropic Console](https://console.anthropic.com/)

### Options de configuration

Vous pouvez personnaliser le comportement via des variables d'environnement ou le fichier `.env` :

| Variable                          | Description                                                  | Défaut                          |
| --------------------------------- | ------------------------------------------------------------ | ------------------------------- |
| `AI_PROVIDER`                     | Fournisseur AI à utiliser                                    | `gemini`                        |
| `AI_MODEL`                        | Modèle AI à utiliser                                         | Défaut selon provider           |
| `GEMINI_API_KEY`                  | Clé API Gemini (si provider=gemini)                          | -                               |
| `OPENAI_API_KEY`                  | Clé API OpenAI (si provider=openai)                          | -                               |
| `ANTHROPIC_API_KEY`               | Clé API Claude (si provider=claude)                          | -                               |
| `BATCH_SIZE`                      | Nombre de fichiers analysés en parallèle                     | `10`                            |
| `MAX_RETRIES`                     | Nombre de tentatives en cas d'erreur                         | `3`                             |
| `TIMEOUT_SECONDS`                 | Timeout pour chaque requête (secondes)                       | `60`                            |
| `OUTPUT_DIR`                      | Répertoire de sortie des analyses                            | `docs/analyses`                 |
| `ARCHITECTURE_REPORT`             | Chemin du rapport d'architecture                             | `docs/architecture_overview.md` |
| `ROOT_DIR`                        | Répertoire racine à analyser                                 | `.`                             |
| `ENABLE_WEB_SEARCH`               | Activer la recherche web                                     | `true`                          |
| `MAX_WEB_RESULTS`                 | Nombre max de résultats de recherche                         | `3`                             |
| `ENABLE_SECURITY_ANALYSIS`        | Activer l'analyse de sécurité                                | `true`                          |
| `ENABLE_METRICS_ANALYSIS`         | Activer l'analyse de métriques                               | `true`                          |
| `ENABLE_DEPENDENCY_VULNERABILITY` | Activer l'analyse des vulnérabilités                         | `true`                          |
| `ENABLE_CODE_GENERATION`          | Permettre la génération de code d'analyse                    | `true`                          |
| `SHOW_REASONING`                  | Afficher le processus de reasoning du modèle (si disponible) | `false`                         |
| `ENABLE_CACHE`                    | Activer le cache des analyses (réduit les coûts API)         | `true`                          |
| `CACHE_TTL_DAYS`                  | Durée de vie du cache en jours                               | `7`                             |
| `ANALYZE_DEPENDENT_FILES`         | Analyser les fichiers dépendants des fichiers modifiés       | `true`                          |
| `MAX_DEPENDENCY_DEPTH`            | Profondeur maximale pour l'analyse des dépendances            | `2`                             |
| `ENABLE_METRICS`                  | Activer la collecte de métriques de performance              | `true`                          |
| `ENABLE_PRIORITY_ANALYSIS`        | Activer l'analyse par priorité (PR files = HIGH)             | `true`                          |
| `ENABLE_EXPORT_ANALYSIS`          | Activer l'extraction des exports                             | `true`                          |
| `ENABLE_REVERSE_DEPENDENCY`       | Activer le graphe de dépendances inverses                    | `true`                          |
| `ENABLE_IMPACT_ANALYSIS`          | Activer l'analyse d'impact des bugs                          | `true`                          |
| `MAX_IMPACT_DEPTH`                | Profondeur maximale pour l'analyse d'impact                  | `3`                             |
| `ENABLE_CLAUDE_CODE_FIX`          | Activer l'intégration Claude Code pour la correction         | `true`                          |
| `FIX_SEVERITY_THRESHOLD`          | Seuil de sévérité minimale pour les corrections              | `medium`                        |
| `ENABLE_STRUCTURED_OUTPUTS`       | Activer les Structured Outputs Gemini (JSON validé Pydantic) | `true`                          |
| `ENABLE_THINKING`                 | Activer le mode Thinking/Reasoning de Gemini                 | `false`                         |
| `THINKING_BUDGET`                 | Budget de tokens pour le Thinking (min 128)                  | `1024`                          |
| `ENABLE_CODE_EXECUTION`           | Activer l'exécution de code Python en sandbox                | `false`                         |
| `ENABLE_FUNCTION_CALLING`         | Activer l'appel automatique de fonctions                     | `false`                         |
| `ENABLE_CONTEXT_CACHING`          | Activer le cache de contexte Gemini (-50% coût)              | `true`                          |
| `CONTEXT_CACHE_TTL_SECONDS`       | Durée de vie du cache de contexte (secondes)                 | `3600`                          |
| `ENABLE_BATCH_MODE`               | Activer le mode Batch API (-50% coût)                        | `false`                         |

### 💰 Coûts d'analyse

Les coûts d'analyse dépendent du fournisseur, du modèle choisi et de la taille de votre codebase. Voici des estimations pour différents scénarios :

#### Estimation des tokens

- **1 ligne de code** ≈ 10-20 tokens (input)
- **1 fichier** ≈ 500-2000 tokens selon la taille
- **Rapport généré** ≈ 1000-5000 tokens (output) par fichier analysé

#### Tableau des coûts estimés

| Scénario              | Fichiers | Lignes | Tokens Input | Tokens Output | **Gemini Pro** | **GPT-4** | **GPT-3.5 Turbo** | **Claude 3.5 Sonnet** | **Claude 3 Opus** |
| --------------------- | -------- | ------ | ------------ | ------------- | -------------- | --------- | ----------------- | --------------------- | ----------------- |
| **Petit projet**      | 10       | 1 000  | ~15 000      | ~15 000       | $0.10          | $0.75     | $0.05             | $0.27                 | $1.35             |
| **Projet moyen**      | 50       | 5 000  | ~75 000      | ~75 000       | $0.52          | $3.75     | $0.23             | $1.35                 | $6.75             |
| **Grand projet**      | 100      | 10 000 | ~150 000     | ~150 000      | $1.03          | $7.50     | $0.45             | $2.70                 | $13.50            |
| **Très grand projet** | 500      | 50 000 | ~750 000     | ~750 000      | $5.16          | $37.50    | $2.25             | $13.50                | $67.50            |

_Note : Les coûts sont approximatifs et peuvent varier selon la complexité du code et la longueur des réponses générées._

#### Tarifs par million de tokens (2024)

| Fournisseur | Modèle        | Input (par M tokens) | Output (par M tokens) |
| ----------- | ------------- | -------------------- | --------------------- |
| **Gemini**  | 3 Pro Preview | ~$3.50               | ~$10.50               |
| **Gemini**  | 2.5 Pro       | ~$3.50               | ~$10.50               |
| **Gemini**  | 1.5 Pro       | $3.50                | $10.50                |
| **Gemini**  | 1.5 Flash     | $0.35                | $1.05                 |
| **OpenAI**  | GPT-4o        | $2.50                | $10.00                |
| **OpenAI**  | GPT-4 Turbo   | $10.00               | $30.00                |
| **OpenAI**  | GPT-4         | $30.00               | $60.00                |
| **OpenAI**  | GPT-3.5 Turbo | $0.50                | $1.50                 |
| **Claude**  | 3.5 Sonnet    | $3.00                | $15.00                |
| **Claude**  | 3 Opus        | $15.00               | $75.00                |
| **Claude**  | 3 Haiku       | $0.25                | $1.25                 |

_Note : Les tarifs peuvent varier. Consultez les pages de tarification officielles pour les tarifs les plus récents._

#### Recommandations selon le budget

- **Budget serré** : Utilisez **Gemini 1.5 Flash** ou **GPT-3.5 Turbo** pour des analyses rapides et économiques
- **Équilibre qualité/prix** : Utilisez **Gemini 1.5 Pro**, **GPT-4o** ou **Claude 3.5 Sonnet** pour une bonne qualité à un prix raisonnable
- **Qualité maximale** : Utilisez **GPT-4**, **Claude 3 Opus** ou **Gemini 2.5 Pro** pour les analyses les plus approfondies
- **Spécialisé code** : Pour l'analyse de code, **GPT-4o** et **Claude 3.5 Sonnet** offrent d'excellentes performances

_Note : Consultez les pages de tarification officielles pour les tarifs les plus récents :_

- [Tarification Gemini](https://ai.google.dev/gemini-api/docs/pricing)
- [Tarification OpenAI](https://openai.com/api/pricing/)
- [Tarification Claude](https://www.anthropic.com/pricing)

## 📖 Utilisation

### Commande principale

Une fois installé, utilisez la commande `aetheris` :

```bash
# Afficher l'aide
aetheris --help

# Afficher l'aide pour la sous-commande analysis
aetheris analysis --help
```

### Analyse de base

```bash
aetheris analysis
```

La commande va :

1. Scanner tous les fichiers du répertoire courant
2. Analyser chaque fichier avec les agents appropriés
3. Générer des rapports détaillés dans `docs/analyses/`
4. Créer un rapport d'architecture global
5. Générer un rapport d'assurance qualité

### Analyse d'un répertoire spécifique

```bash
ROOT_DIR=./mon_projet aetheris analysis
```

### Analyse des fichiers modifiés uniquement

Pour analyser uniquement les fichiers modifiés (utile pour les PR/commits) :

```bash
# Avec une liste de fichiers (séparés par virgules)
aetheris analysis --changed-files-only --files src/file1.py,src/file2.py

# Avec une liste JSON (depuis GitHub Actions)
aetheris analysis --changed-files-only --files '["src/file1.py", "src/file2.py"]'

# Avec un numéro de PR (pour information)
aetheris analysis --changed-files-only --files src/file1.py --pr-number 123
```

### Utilisation depuis les sources (sans installation)

Si vous avez cloné le repository et installé les dépendances :

```bash
# Utiliser directement main.py
python main.py

# Ou utiliser le module CLI
python -m src.cli analysis
```

### Correction de bugs avec Claude Code (v2.1.0+)

La nouvelle commande `aetheris fix` permet de corriger automatiquement les bugs détectés en utilisant Claude Code.

#### Prérequis

- **Claude Code** doit être installé sur votre machine :
  ```bash
  npm install -g @anthropic-ai/claude-code
  ```

#### Commande fix

```bash
# Corriger les bugs depuis le cache existant
aetheris fix

# Lancer une analyse puis corriger
aetheris fix --analyze-first

# Corriger uniquement les bugs critiques et high
aetheris fix --severity high

# Mode automatique (sans confirmations entre les bugs)
aetheris fix --auto
```

#### Options disponibles

| Option | Description |
|--------|-------------|
| `--analyze-first` | Lancer une analyse avant de corriger |
| `--severity` | Sévérité minimale des bugs à corriger (`critical`, `high`, `medium`, `low`) |
| `--auto` | Mode automatique sans confirmations entre les bugs |

#### Fonctionnement

1. **Détection de Claude Code** : Vérifie si Claude Code est installé
2. **Chargement des bugs** : Lit le cache `.bugs_cache.json` ou lance une analyse
3. **Filtrage par sévérité** : Filtre les bugs selon le seuil choisi
4. **Affichage du tableau** : Montre un récapitulatif des bugs à corriger
5. **Correction séquentielle** : Pour chaque bug :
   - Affiche les détails du bug
   - Lance Claude Code dans une **nouvelle fenêtre de terminal**
   - Attend la confirmation de l'utilisateur
   - Passe au bug suivant

#### Support multi-plateforme

La commande détecte automatiquement le système d'exploitation et lance Claude Code dans le terminal approprié :

| OS | Terminal utilisé |
|----|------------------|
| **Windows** | `cmd` avec `start` |
| **macOS** | Terminal.app via AppleScript |
| **Linux** | `gnome-terminal`, `konsole`, `xfce4-terminal`, `xterm`, ou `x-terminal-emulator` |

## 🔄 GitHub Actions

Le projet inclut un workflow GitHub Actions pour automatiser l'analyse de code directement dans votre repository.

### Configuration

1. **Ajouter le secret GitHub** :
   - Allez dans votre repository → Settings → Secrets and variables → Actions
   - Cliquez sur "New repository secret"
   - Nom : `GEMINI_API_KEY`, `OPENAI_API_KEY` ou `ANTHROPIC_API_KEY` selon le provider choisi
   - Valeur : Votre clé API correspondante
   - Cliquez sur "Add secret"
   - Optionnel : Ajoutez `AI_PROVIDER` et `AI_MODEL` pour personnaliser le provider et le modèle

2. **Le workflow est déjà configuré** dans `.github/workflows/code-review.yml`

### Déclencheurs disponibles

Le workflow s'exécute automatiquement dans les cas suivants :

- **Push vers main/master** : Analyse complète de la codebase
- **Pull Request** : Analyse uniquement des fichiers modifiés dans la PR
- **Exécution manuelle** : Via l'onglet Actions de GitHub avec options :
  - Mode `full` : Analyse complète
  - Mode `changed` : Analyse des fichiers modifiés (peut spécifier un numéro de PR)

### Résultats

Les rapports d'analyse sont disponibles en tant qu'**artifacts GitHub** :

- Allez dans l'onglet Actions
- Sélectionnez l'exécution du workflow
- Téléchargez l'artifact "code-analysis-reports"
- Les rapports incluent :
  - Rapports individuels par fichier (`docs/analyses/*.md`)
  - Rapport d'architecture (`docs/architecture_overview.md`)
  - Rapport d'assurance qualité (`docs/analyses/quality_assurance_report.md`)
  - Rapport de vulnérabilités (`docs/analyses/vulnerabilities_report.md`)

### Exemple d'utilisation

1. Créez ou modifiez une Pull Request
2. Le workflow s'exécute automatiquement
3. Consultez les résultats dans l'onglet Actions
4. Téléchargez les rapports depuis les artifacts

### Personnalisation

Vous pouvez personnaliser le workflow en modifiant `.github/workflows/code-review.yml` :

- Changer les branches déclencheuses
- Modifier les chemins exclus (`paths-ignore`)
- Ajuster les options d'analyse
- Ajouter des notifications (email, Slack, etc.)

## 🚀 Nouvelles Fonctionnalités v2.0.0

### Cache Intelligent

Le système de cache réduit significativement les coûts API en évitant les ré-analyses inutiles :

- **Cache basé sur git SHA** : Invalidation automatique si le fichier est modifié
- **Stockage disque** : Cache persistant dans `.cache/aetheris/`
- **TTL configurable** : Durée de vie du cache ajustable (défaut: 7 jours)
- **Réduction des coûts** : 60-80% de réduction des appels API

```bash
# Désactiver le cache si nécessaire
ENABLE_CACHE=false aetheris analysis
```

### Parallélisation Intelligente

Analyse optimisée basée sur le graphe de dépendances :

- **Détection automatique** : Identification des fichiers indépendants
- **Analyse parallèle** : Fichiers du même niveau analysés simultanément
- **Respect des dépendances** : Les fichiers dépendants sont analysés après leurs dépendances
- **Performance améliorée** : Réduction significative du temps d'analyse

### Système de Priorités

Optimisation des PR reviews avec priorisation automatique :

- **HIGH** : Fichiers modifiés dans la PR
- **MEDIUM** : Dépendances directes des fichiers PR
- **LOW** : Autres fichiers
- **Ordre d'analyse** : HIGH → MEDIUM → LOW pour des résultats plus rapides

### Métriques et Monitoring

Collecte complète de métriques de performance :

- **Métriques par étape** : Temps d'exécution, taux de succès, fichiers traités
- **Métriques par agent** : Appels, durées, tokens estimés
- **Export JSON** : Métriques sauvegardées dans `docs/metrics/`
- **Statistiques agrégées** : Cache hit rate, success rate, coûts estimés

### Analyse Incrémentale Améliorée

Détection automatique des fichiers impactés :

- **Dépendances transitives** : Analyse jusqu'à N niveaux de profondeur
- **Configuration flexible** : Profondeur maximale ajustable (défaut: 2)
- **Optimisation PR** : Analyse uniquement des fichiers impactés par les changements

### Gestion d'Erreurs Robuste

Système de résilience amélioré :

- **Circuit breaker** : Évite les appels répétés en cas d'erreur
- **Backoff exponentiel** : Retry intelligent avec délais croissants
- **Classification d'erreurs** : Temporaire/permanente/critique
- **Logging structuré** : Contexte complet pour le débogage

### Système de Plugins

Extensibilité via hooks personnalisés :

- **Hooks par étape** : Exécution de code avant/après chaque étape
- **Contexte partagé** : Accès aux données du workflow
- **Documentation complète** : Guide dans `docs/PLUGINS.md`

## 🧠 Nouvelles Fonctionnalités v2.2.0

### Structured Outputs (Gemini)

Les Structured Outputs garantissent des réponses JSON validées via Pydantic :

```python
# Exemple d'utilisation interne
from src.models.analysis_schemas import SecurityAnalysisResult

result = await agent._call_ai_structured(prompt, SecurityAnalysisResult)
# result est un objet Pydantic validé avec des types stricts
```

**Avantages :**
- Réponses JSON garanties (pas de parsing manuel)
- Validation automatique des types
- Schémas Pydantic réutilisables
- Meilleure fiabilité des analyses

### Thinking/Reasoning Mode (Gemini 2.5+)

Le mode Thinking affiche le processus de raisonnement du modèle :

```bash
# Activer le mode Thinking
ENABLE_THINKING=true THINKING_BUDGET=2048 aetheris analysis
```

**Utilisation :**
- Déboguer les analyses complexes
- Comprendre les décisions du modèle
- Améliorer la transparence
- Budget minimum : 128 tokens

### Code Execution (Gemini)

Exécution de code Python en sandbox pour des analyses dynamiques :

```bash
# Activer l'exécution de code
ENABLE_CODE_EXECUTION=true aetheris analysis
```

**Cas d'usage :**
- Parsing AST pour métriques avancées
- Calculs de complexité
- Détection de patterns via code
- Analyse dynamique du code source

### Context Caching (Gemini)

Réduction des coûts API de ~50% via le cache de contexte :

```bash
# Activer le cache de contexte (1 heure)
ENABLE_CONTEXT_CACHING=true CONTEXT_CACHE_TTL_SECONDS=3600 aetheris analysis
```

**Avantages :**
- Réduction des coûts de 50%
- Réutilisation du contexte entre requêtes
- TTL configurable
- Idéal pour les analyses volumineuses

### Batch API (Gemini)

Traitement en lot à -50% du prix :

```bash
# Activer le mode batch
ENABLE_BATCH_MODE=true aetheris analysis
```

**Cas d'usage :**
- Analyses de gros projets
- Traitement non-urgent
- Optimisation des coûts

### Sécurité Améliorée

Les rapports de sécurité incluent maintenant :

- **CWE ID** : Identifiants Common Weakness Enumeration (ex: CWE-79 pour XSS)
- **Catégories OWASP** : Classification OWASP Top 10 (ex: A01:2021)
- **Recommandations détaillées** : Corrections spécifiques par vulnérabilité

## 📊 Rapports générés

### Rapports individuels

Chaque fichier analysé génère un rapport Markdown dans `docs/analyses/` avec :

- Objectif et fonction principale
- Points forts et bonnes pratiques
- Relations et dépendances
- Risques et dettes techniques
- Suggestions d'amélioration
- Problèmes de sécurité détectés
- Métriques de code

### Rapport d'architecture

`docs/architecture_overview.md` contient :

- Vue d'ensemble de l'architecture
- Patterns identifiés
- Cohérence inter-modules
- Redondances et dépendances
- Recommandations d'optimisation
- Plan de refactoring
- Gouvernance du code

### Rapport d'assurance qualité

`docs/analyses/quality_assurance_report.md` contient :

- Score de qualité global (sur 100)
- Analyse par dimension (Sécurité, Maintenabilité, Architecture, etc.)
- Plan d'action priorisé
- Roadmap d'amélioration

### Rapport des vulnérabilités

`docs/analyses/vulnerabilities_report.md` contient :

- Liste des vulnérabilités détectées dans les dépendances
- Répartition par sévérité (critical, high, medium, low)
- CVE et identifiants de vulnérabilités
- Versions corrigées disponibles

### Métriques de performance

`docs/metrics/metrics_YYYYMMDD_HHMMSS.json` contient :

- Durée totale d'exécution
- Métriques par étape du workflow
- Métriques par agent (appels, succès, durées)
- Statistiques de cache (hit rate)
- Taux de succès global
- Tokens estimés et coûts API

## 🔍 Langages supportés

Le système détecte automatiquement et analyse :

- **Dart/Flutter** (`.dart`)
- **TypeScript/JavaScript** (`.ts`, `.tsx`, `.js`, `.jsx`)
- **Python** (`.py`)
- **Java** (`.java`)
- **Kotlin** (`.kt`)
- **Swift** (`.swift`)
- **Go** (`.go`)
- **Rust** (`.rs`)
- **C/C++** (`.c`, `.cpp`, `.h`)
- **C#** (`.cs`)
- **PHP** (`.php`)
- **Ruby** (`.rb`)
- Et autres langages de programmation

## 🛡️ Fichiers exclus

Le système exclut automatiquement :

- Dossiers de build (`build/`, `dist/`, `node_modules/`, etc.)
- Fichiers générés (`.g.dart`, `.d.ts`, `.pyc`, etc.)
- Fichiers de lock (`package-lock.json`, `yarn.lock`, etc.)
- Fichiers binaires (> 1MB)
- Dossiers cachés (`.git/`, `.venv/`, etc.)

Les règles `.gitignore` sont respectées automatiquement.

## 📝 Exemple de sortie

### Avec barre de progression (terminal interactif)

Lorsque vous exécutez Aetheris dans un terminal interactif, vous verrez des barres de progression modernes avec Rich :

```text
🚀 Aetheris by Adryan - Démarrage de l'analyse de code
============================================================

📁 Répertoire racine: .
📂 Répertoire de sortie: docs/analyses
🤖 Provider AI: GEMINI
🤖 Modèle: gemini-1.5-flash

🌐 Recherche web activée pour les documentations

🔍 Scan des fichiers...                    ████████████████████ 100% 0:00:01
✅ 25 fichiers trouvés à analyser

🔗 Initialisation de l'analyseur de dépendances...  ████████████████████ 100%

📦 Analyse des fichiers...                 ████████████████████ 100% 0:02:15
  📦 Batch 1/3 (10 fichiers)...
  📦 Analyse: main.py ✅
  📦 Analyse: utils.py ✅
  ...

✅ Analyse de 25 fichiers terminée

🔄 Analyse des dépendances et détection des cycles...  ████████████████████ 100%
✅ Aucun cycle de dépendances détecté

🏗️  Génération du rapport d'architecture...  ████████████████████ 100%
✅ Rapport d'architecture sauvegardé: docs/architecture_overview.md

🔒 Analyse des vulnérabilités des dépendances via OSV API...  ████████████████████ 100%
✅ Analyse terminée: 15 package(s) vérifié(s), 2 vulnérabilité(s) trouvée(s)

📋 Génération du rapport d'assurance qualité...  ████████████████████ 100%
✅ Rapport d'assurance qualité sauvegardé: docs/analyses/quality_assurance_report.md

📊 Statistiques:
  - Fichiers analysés: 25
  - Succès: 25
  - Échecs: 0

  Répartition par langage:
    - Python: 15
    - TypeScript: 8
    - Markdown: 2

============================================================
✅ Analyse terminée avec succès!
============================================================
```

### Mode non-interactif

Si vous exécutez Aetheris dans un environnement non-interactif (CI/CD, redirection de sortie), le système utilise automatiquement des logs simples sans barres de progression.

## 🤔 Affichage du Reasoning (v1.1.0+)

Certains modèles AI (comme OpenAI o1-preview, o1-mini) exposent leur processus de raisonnement. Vous pouvez activer l'affichage du reasoning pour voir comment le modèle arrive à ses conclusions.

### Activation

Définissez la variable d'environnement `SHOW_REASONING=true` :

```env
SHOW_REASONING=true
```

Ou via la ligne de commande :

```bash
SHOW_REASONING=true aetheris analysis
```

### Modèles avec reasoning disponibles

- **OpenAI o1-preview** : Affiche le reasoning complet
- **OpenAI o1-mini** : Affiche le reasoning complet
- **Autres modèles** : Le reasoning n'est pas disponible via l'API

Le reasoning s'affiche dans un panneau dédié pendant l'analyse, particulièrement utile pour les analyses d'architecture et d'assurance qualité.

## 🐛 Dépannage

### Erreur: "Variable d'environnement [API_KEY] non définie"

Créez un fichier `.env` avec votre clé API selon le provider choisi :

- `GEMINI_API_KEY` pour Gemini
- `OPENAI_API_KEY` pour OpenAI
- `ANTHROPIC_API_KEY` pour Claude

Ou définissez la variable d'environnement correspondante.

### Erreur: "ModuleNotFoundError"

Installez les dépendances :

```bash
pip install -r requirements.txt
```

### Les logs ne s'affichent pas

Le script utilise `log_print()` avec flush automatique. Si les logs ne s'affichent toujours pas, vérifiez que votre terminal supporte UTF-8.

### Analyse lente

Réduisez `BATCH_SIZE` ou augmentez `TIMEOUT_SECONDS` dans votre `.env`.

## 📄 Licence

Ce projet est fourni tel quel, sans garantie.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 🔌 Extensibilité

Aetheris v2.0.0 inclut un système de plugins/hooks pour étendre le comportement du système. Consultez `docs/PLUGINS.md` pour :

- Guide complet du système de hooks
- Exemples d'utilisation
- Création de plugins personnalisés
- Liste des hooks disponibles

## 📚 Ressources

- [Documentation Google Gemini](https://ai.google.dev/docs)
- [Documentation OpenAI](https://platform.openai.com/docs)
- [Documentation Claude](https://docs.anthropic.com)
- [API OSV (Open Source Vulnerabilities)](https://osv.dev/)
- [Documentation pathspec](https://github.com/cpburnz/python-pathspec)
- [Repository GitHub](https://github.com/adryserage/aetheris)
- [Package PyPI](https://pypi.org/project/adryserage-aetheris/)
- [Documentation Plugins](docs/PLUGINS.md)
