# Aetheris by Allowebs - Système d'Analyse de Code Multi-Agents

[![PyPI version](https://badge.fury.io/py/adryserage-aetheris.svg)](https://badge.fury.io/py/adryserage-aetheris)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/adryserage/code_reviewer/code-review.yml?label=CI)](https://github.com/adryserage/code_reviewer/actions)
[![PyPI downloads](https://img.shields.io/pypi/dm/adryserage-aetheris.svg)](https://pypi.org/project/adryserage-aetheris/)
[![GitHub stars](https://img.shields.io/github/stars/adryserage/code_reviewer.svg?style=social&label=Star)](https://github.com/adryserage/code_reviewer)

Système d'analyse de code automatisé utilisant plusieurs agents coopérants pour fournir une analyse complète de la qualité, de la sécurité et de l'architecture de votre codebase.

## 🎯 Fonctionnalités

Le système utilise **6 agents spécialisés** qui travaillent ensemble pour analyser votre code :

### Agents d'Analyse

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

- `google-generativeai` - API Gemini pour l'analyse de code
- `openai` - API OpenAI pour l'analyse de code
- `anthropic` - API Claude (Anthropic) pour l'analyse de code
- `pathspec` - Gestion des patterns .gitignore
- `requests` - Requêtes HTTP pour l'API OSV (version >=2.32.0 pour corriger les vulnérabilités CVE-2024-47081 et CVE-2024-35195)
- `pyyaml` - Parsing des fichiers YAML (pubspec.yaml pour Dart/Flutter)
- `duckduckgo-search` - Recherche web pour enrichir les analyses

## 🏗️ Structure du Projet

Le projet est organisé en modules pour une meilleure maintenabilité :

```
aetheris/
├── src/
│   ├── core/              # Modules principaux
│   │   ├── config.py      # Configuration (AnalysisConfig, load_env_file)
│   │   ├── logger.py     # Logging et encodage UTF-8
│   │   └── analyzer.py   # Orchestrateur principal (CodeAnalyzer)
│   ├── models/           # Modèles de données
│   │   └── data_models.py  # Dataclasses (FileAnalysis, SecurityIssue, etc.)
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
├── main.py               # Point d'entrée principal (pour développement)
├── src/
│   └── cli.py           # Interface CLI avec sous-commandes
├── scripts/              # Scripts utilitaires
│   ├── analyze_changes.py  # Analyse des fichiers modifiés
│   └── README.md
├── pyproject.toml        # Configuration du package Python
├── requirements.txt      # Dépendances Python
└── README.md            # Documentation
```

### Architecture Modulaire

- **`src/core/`** : Contient l'orchestrateur principal (`CodeAnalyzer`) et les utilitaires de configuration et logging
- **`src/models/`** : Définit les structures de données utilisées pour échanger des informations entre les composants
- **`src/agents/`** : Chaque agent est un module indépendant héritant de `BaseAgent` pour la logique commune
- **`src/services/`** : Services utilitaires réutilisables (génération de code, recherche web, analyse de dépendances)

Cette structure modulaire facilite :

- La maintenance et l'extension du code
- La réutilisation des composants
- Les tests unitaires
- La compréhension de l'architecture

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
AI_MODEL=gemini-3-pro-preview
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

| Fournisseur | Modèles disponibles                                                                          | Modèle par défaut            |
| ----------- | -------------------------------------------------------------------------------------------- | ---------------------------- |
| **Gemini**  | `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-1.5-flash`, `gemini-3-pro-preview`, `gemini-pro` | `gemini-1.5-pro`             |
| **OpenAI**  | `gpt-4o`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`, `gpt-4-turbo-preview`                     | `gpt-4o`                     |
| **Claude**  | `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`, `claude-3-haiku-20240307`            | `claude-3-5-sonnet-20241022` |

**Note importante** :

- **Codex (OpenAI)** : Le modèle Codex original a été déprécié. Pour l'analyse de code, utilisez **GPT-4o** ou **GPT-4 Turbo** qui offrent d'excellentes performances pour le code.
- Certains modèles spécialisés (comme GPT-5 Codex pour OpenAI ou Claude Opus 4.1) peuvent nécessiter un accès spécial ou ne pas être disponibles via l'API standard. Consultez la documentation officielle de chaque fournisseur pour les modèles les plus récents et leur disponibilité.

#### Obtenir les clés API

- **Gemini** : [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OpenAI** : [OpenAI Platform](https://platform.openai.com/api-keys)
- **Claude** : [Anthropic Console](https://console.anthropic.com/)

### Options de configuration

Vous pouvez personnaliser le comportement via des variables d'environnement ou le fichier `.env` :

| Variable                          | Description                               | Défaut                          |
| --------------------------------- | ----------------------------------------- | ------------------------------- |
| `AI_PROVIDER`                     | Fournisseur AI à utiliser                 | `gemini`                        |
| `AI_MODEL`                        | Modèle AI à utiliser                      | Défaut selon provider           |
| `GEMINI_API_KEY`                  | Clé API Gemini (si provider=gemini)       | -                               |
| `OPENAI_API_KEY`                  | Clé API OpenAI (si provider=openai)       | -                               |
| `ANTHROPIC_API_KEY`               | Clé API Claude (si provider=claude)       | -                               |
| `BATCH_SIZE`                      | Nombre de fichiers analysés en parallèle  | `10`                            |
| `MAX_RETRIES`                     | Nombre de tentatives en cas d'erreur      | `3`                             |
| `TIMEOUT_SECONDS`                 | Timeout pour chaque requête (secondes)    | `60`                            |
| `OUTPUT_DIR`                      | Répertoire de sortie des analyses         | `docs/analyses`                 |
| `ARCHITECTURE_REPORT`             | Chemin du rapport d'architecture          | `docs/architecture_overview.md` |
| `ROOT_DIR`                        | Répertoire racine à analyser              | `.`                             |
| `ENABLE_WEB_SEARCH`               | Activer la recherche web                  | `true`                          |
| `MAX_WEB_RESULTS`                 | Nombre max de résultats de recherche      | `3`                             |
| `ENABLE_SECURITY_ANALYSIS`        | Activer l'analyse de sécurité             | `true`                          |
| `ENABLE_METRICS_ANALYSIS`         | Activer l'analyse de métriques            | `true`                          |
| `ENABLE_DEPENDENCY_VULNERABILITY` | Activer l'analyse des vulnérabilités      | `true`                          |
| `ENABLE_CODE_GENERATION`          | Permettre la génération de code d'analyse | `true`                          |

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

```
============================================================
🚀 Démarrage de l'analyse de code
============================================================

📁 Répertoire racine: .
📂 Répertoire de sortie: docs/analyses
🤖 Provider AI: GEMINI
🤖 Modèle: gemini-3-pro-preview

🌐 Recherche web activée pour les documentations

🔍 Scan des fichiers...
✅ 25 fichiers trouvés à analyser

🔗 Initialisation de l'analyseur de dépendances...
✅ Analyseur de dépendances initialisé

📦 Batch 1/3 (10 fichiers)...
  ✅ src/main.py
  ✅ src/utils.py
  ...

✅ Analyse de 25 fichiers terminée

🔄 Analyse des dépendances et détection des cycles...
✅ Aucun cycle de dépendances détecté

🏗️  Génération du rapport d'architecture...
✅ Rapport d'architecture sauvegardé: docs/architecture_overview.md

🔒 Analyse des vulnérabilités des dépendances via OSV API...
✅ Analyse terminée: 15 package(s) vérifié(s), 2 vulnérabilité(s) trouvée(s)

📋 Génération du rapport d'assurance qualité...
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

## 📚 Ressources

- [Documentation Google Gemini](https://ai.google.dev/docs)
- [Documentation OpenAI](https://platform.openai.com/docs)
- [Documentation Claude](https://docs.anthropic.com)
- [API OSV (Open Source Vulnerabilities)](https://osv.dev/)
- [Documentation pathspec](https://github.com/cpburnz/python-pathspec)
- [Repository GitHub](https://github.com/adryserage/aetheris)
- [Package PyPI](https://pypi.org/project/adryserage-aetheris/)
