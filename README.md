# Aetheris by Allowebs - Système d'Analyse de Code Multi-Agents

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
- Clé API Google Gemini ([Obtenir une clé](https://makersuite.google.com/app/apikey))

### Installation depuis PyPI (Recommandé)

Aetheris est disponible sur PyPI sous le nom `adryserage-aetheris`. Installation simple :

```bash
pip install adryserage-aetheris
```

C'est tout ! Le package est maintenant installé et la commande `aetheris` est disponible.

### Installation depuis GitHub Packages (Alternative)

Si vous préférez installer depuis GitHub Packages :

1. **Créer un Personal Access Token (PAT)** :
   - Allez dans GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Créez un nouveau token avec le scope `read:packages`
   - Copiez le token

2. **Installer le package** :

```bash
# Linux/Mac
pip install --extra-index-url https://USERNAME:TOKEN@pypi.github.com/adryserage/code_reviewer/simple/ adryserage-aetheris

# Windows (PowerShell)
pip install --extra-index-url https://USERNAME:TOKEN@pypi.github.com/adryserage/code_reviewer/simple/ adryserage-aetheris
```

Remplacez `USERNAME` par votre nom d'utilisateur GitHub et `TOKEN` par votre Personal Access Token.

**Alternative avec variable d'environnement** :

```bash
export PIP_EXTRA_INDEX_URL="https://USERNAME:TOKEN@pypi.github.com/adryserage/code_reviewer/simple/"
pip install adryserage-aetheris
```

**Note** : Après l'installation, la commande CLI reste `aetheris` (définie dans le package).

### Installation depuis les sources

Si vous préférez installer depuis les sources :

```bash
git clone https://github.com/Allowebs/code_reviewer.git
cd code_reviewer
pip install -r requirements.txt
```

### Dépendances

- `google-generativeai` - API Gemini pour l'analyse de code
- `pathspec` - Gestion des patterns .gitignore
- `requests` - Requêtes HTTP pour l'API OSV (version >=2.32.0 pour corriger les vulnérabilités CVE-2024-47081 et CVE-2024-35195)
- `pyyaml` - Parsing des fichiers YAML (pubspec.yaml pour Dart/Flutter)
- `duckduckgo-search` - Recherche web pour enrichir les analyses (optionnel)

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
├── main.py               # Point d'entrée principal
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

### Configuration de la clé API Gemini

Créez un fichier `.env` à la racine du projet (vous pouvez utiliser `.env.example` comme modèle) :

```env
GEMINI_API_KEY=votre_cle_api_ici
```

Ou définissez la variable d'environnement :

**Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY='votre_cle_api_ici'
```

**Linux/Mac:**

```bash
export GEMINI_API_KEY=votre_cle_api_ici
```

### Options de configuration

Vous pouvez personnaliser le comportement via des variables d'environnement ou le fichier `.env` :

| Variable                          | Description                               | Défaut                          |
| --------------------------------- | ----------------------------------------- | ------------------------------- |
| `GEMINI_MODEL`                    | Modèle Gemini à utiliser                  | `gemini-3-pro-preview`          |
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
   - Nom : `GEMINI_API_KEY`
   - Valeur : Votre clé API Gemini
   - Cliquez sur "Add secret"

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
🤖 Modèle Gemini: gemini-3-pro-preview

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

### Erreur: "Variable d'environnement GEMINI_API_KEY non définie"

Créez un fichier `.env` avec votre clé API ou définissez la variable d'environnement.

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
- [API OSV (Open Source Vulnerabilities)](https://osv.dev/)
- [Documentation pathspec](https://github.com/cpburnz/python-pathspec)
