# Vue d'ensemble de l'architecture

*Généré le 2026-01-07 15:47:02*
*Nombre de fichiers analysés: 123*
*Fichiers réussis: 123*
*Fichiers échoués: 0*

---

Voici le rapport d'architecture complet basé sur l'analyse des 123 fichiers, des statistiques de dépendances et des synthèses fournies.

# Rapport d'Architecture Logicielle : Projet Aetheris

## Vue d'ensemble de l'architecture

**Aetheris** est un outil CLI (Command Line Interface) d'analyse de code basé sur une architecture **Multi-Agents (MAS)**, développé en Python (v3.8+). Il orchestre plusieurs agents spécialisés (Sécurité, Qualité, Architecture) alimentés par des LLM (Gemini, Claude, OpenAI) pour fournir des revues de code, générer des tests et corriger des bugs.

Le projet se distingue par une méthodologie de développement rigoureuse ("Spec-First") visible dans le dossier `specs/`, mais souffre d'une complexité accidentelle liée à sa stratégie de distribution (compilation binaire Cython) et à une dérive entre la documentation et l'implémentation.

### Indicateurs Clés
*   **Maturité Architecturale** : Moyenne à Élevée (Pattern Orchestrator bien défini, mais couplage fort).
*   **Dette Technique** : Moyenne (Dépendances implicites, fragilité des scripts CI/CD, incohérences Docs/Code).
*   **Sécurité** : Risque Modéré (Injection de commandes dans CI, gestion des secrets, stratégie d'obfuscation binaire discutable).

---

## Table des matières
1.  [Architecture et patterns identifiés](#architecture-et-patterns-identifiés)
2.  [Cohérence inter-modules](#cohérence-inter-modules)
3.  [Redondances et dépendances](#redondances-dépendances-ou-couplages-excessifs)
4.  [Recommandations d'optimisation](#recommandations-doptimisation)
5.  [Plan de refactoring](#plan-de-refactoring)
6.  [Gouvernance du code](#gouvernance-du-code)

---

## Architecture et patterns identifiés

### 1. Patterns Architecturaux
*   **Orchestrator Pattern** : Le fichier `src/core/orchestrator.py` agit comme le chef d'orchestre central. Il reçoit les commandes du CLI, initialise la configuration, et délègue les tâches aux agents (`src/agents/`). C'est un point central de contrôle efficace mais qui tend à devenir une "God Class".
*   **Agent-Based Architecture** : Les agents (`src/agents/*`) héritent probablement d'une `BaseAgent`. Chaque agent a une responsabilité unique (ex: `DependencyVulnerabilityAgent`, `CodeMetricsAgent`). C'est une excellente pratique pour la séparation des préoccupations (SoC).
*   **Strategy Pattern** : Utilisé implicitement pour la gestion des fournisseurs d'IA (`src/core/ai_providers.py`), permettant de changer de backend (Gemini, OpenAI) sans impacter la logique métier.
*   **Pipeline CI/CD** : Utilisation intensive de GitHub Actions pour l'automatisation. Le pattern de **Matrix Build** est bien utilisé pour la compilation multi-plateforme (`.github/workflows/build-wheels.yml`).

### 2. Choix de Design Critiques
*   **Distribution Binaire (Cython)** : Le choix de compiler tout le code Python en extensions C (`.so`/`.pyd`) via `setup.py` et `cibuildwheel` est atypique pour un outil CLI.
    *   *Avantage* : Obfuscation du code (protection IP).
    *   *Inconvénient* : Complexité massive du build, perte de portabilité (pas de `sdist`), débogage utilisateur impossible, et faux sentiment de sécurité ("Security by Obscurity").
*   **Architecture Asynchrone** : L'utilisation généralisée de `asyncio` (`main.py`, `src/services/`) est alignée avec la nature I/O bound des appels API aux LLM.

---

## Cohérence inter-modules

### 1. Communication et Interfaces
*   **CLI vs Core** : La séparation entre l'interface (`src/cli.py`) et la logique (`src/core/`) est respectée. Cependant, la gestion de la configuration est fragmentée. Les paramètres passent des arguments CLI aux variables d'env, puis à une classe `Config`, créant des risques d'incohérence (ex: valeurs par défaut dupliquées dans la Doc et le Code).
*   **Agents vs Services** : Les agents semblent consommer directement des services (`src/services/`), ce qui est correct, mais l'injection de dépendances n'est pas explicite, rendant les tests unitaires isolés difficiles.

### 2. Incohérences Détectées (Documentation vs Réalité)
*   **Contextes Conflictuels** : Des traces de documentation mentionnent "Next.js" (`docs/commands/user-story.md`) et des workflows npm, alors que le projet est structurellement du Python pur. Cela suggère un copier-coller de documentation ou un pivot mal nettoyé.
*   **Dépendances Fantômes** : Le code utilise `google-genai`, `requests`, `PyYAML` et `hashlib`, mais ces dépendances ne sont pas clairement centralisées dans un fichier de lock standard visible (`requirements.txt` ou `pyproject.toml` complet). L'analyseur signale des imports "introuvables" qui sont en réalité des dépendances externes non déclarées ou des modules stdlib mal détectés par l'environnement.
*   **Obsolescence des Specs** : Les checklists (`specs/*/checklists/*.md`) marquent des fonctionnalités comme "validées" à une date fixe, mais le code a évolué depuis. Le lien entre Spec et Code est rompu.

---

## Redondances, dépendances ou couplages excessifs

### 1. Couplage Fort dans le Build System
Le fichier `setup.py` est **trop couplé** à la structure des fichiers sources via `glob.glob(&quot;src/**/*.py&quot;)`.
*   *Risque* : Inclusion accidentelle de fichiers de tests ou de scripts temporaires dans le build binaire final.
*   *Problème* : Dépendance forte à `Cython` au moment de l'installation (`setup_requires`), ce qui complique l'installation pour les contributeurs sans environnement de compilation C++.

### 2. Redondance de Logique
*   **Parsing de Version** : La logique pour extraire la version est dupliquée et fragile.
    *   `setup.py` : Utilise probablement une méthode.
    *   `.github/workflows/auto-release.yml` : Utilise `grep` et `sed` (fragile).
    *   `scripts/extract_release_notes.py` : Utilise des Regex Python.
    *   *Impact* : Risque de désynchronisation où le tag Git, la release PyPI et le wheel ont des versions différentes.

### 3. Gestion des Dépendances
*   **Dépendances Implicites** : L'absence de `pyproject.toml` complet (contenant les dépendances runtime `[project.dependencies]`) rend l'installation déterministe impossible.
*   **Risque de Supply Chain** : Les actions GitHub utilisent des tags mutables (`@v4`), et les scripts d'installation (`pip install`) n'utilisent pas de vérification de hash.

---

## Recommandations d'optimisation

### 1. Architecture & Performance
*   **Abandonner la compilation Cython totale** : Sauf contrainte légale absolue, revenir à une distribution Python standard (`sdist` + `wheel`). Cela supprime 80% de la complexité CI/CD, améliore la portabilité (Alpine, ARM), et permet le débogage. Si la protection IP est critique, n'obfusquer que le cœur algorithmique (`src/core`), pas le CLI ou les utilitaires.
*   **Mise en cache sémantique** : Implémenter un cache sémantique (via Vector DB locale ou hash de contexte) pour les appels LLM afin de réduire les coûts et la latence, au lieu du simple cache fichier actuel.

### 2. Sécurité
*   **Sanitisation CI/CD** : Remplacer les interpolations directes `${{ inputs.x }}` dans les scripts shell des workflows GitHub par des variables d'environnement pour éviter les injections de commandes.
*   **Gestion des Secrets** : Interdire le passage de tokens via arguments CLI (`--token`). Utiliser uniquement des variables d'environnement ou des gestionnaires de secrets.
*   **Sécuriser le YAML** : Remplacer tout appel implicite ou `yaml.load` par `yaml.safe_load`.

### 3. Maintenabilité
*   **Centralisation de la Config** : Utiliser `Pydantic` pour définir un schéma de configuration unique qui charge `.env`, CLI args et fichiers de config avec validation de type stricte.
*   **Adoption de `pyproject.toml` (PEP 621)** : Migrer toutes les métadonnées et dépendances de `setup.py` vers `pyproject.toml`.

---

## Plan de refactoring

Ce plan est priorisé par impact sur la stabilité et la sécurité.

### Phase 1 : Sécurité et Stabilisation (Urgent)
1.  **Correctif CI/CD** : Réécrire `.github/workflows/*.yml` pour utiliser des variables d'environnement au lieu d'interpolations directes et épingler les Actions par SHA.
2.  **Gestion des Dépendances** : Créer un `pyproject.toml` complet listant toutes les dépendances (`google-genai`, `requests`, `PyYAML`, etc.) et geler les versions de dev.
3.  **Nettoyage Regex** : Remplacer les commandes `grep/sed` dans les workflows par un script Python robuste utilisant `tomli` pour lire la version.

### Phase 2 : Simplification Architecturale (Moyen Terme)
4.  **Refonte du Build** :
    *   Supprimer la compilation Cython globale.
    *   Configurer le build system standard (`hatch` ou `poetry`).
    *   Réactiver la génération de `sdist`.
5.  **Standardisation Config** : Implémenter `Pydantic Settings` pour unifier la gestion de la configuration (Env/CLI/File).

### Phase 3 : Qualité et Tests (Long Terme)
6.  **Tests Automatisés** : Ajouter des tests unitaires pour les Agents (en mockant les appels LLM).
7.  **Nettoyage Documentation** : Supprimer les références à Next.js/npm et aligner les Spec Docs avec le code actuel via un linter de documentation.

---

## Gouvernance du code

Pour maintenir la qualité architecturale à long terme :

1.  **Doc-as-Code** : Imposer que toute modification de code (`src/`) soit accompagnée d'une mise à jour de la documentation (`docs/` ou `specs/`) dans la même PR. Utiliser des outils pour vérifier la validité des liens et des snippets de code dans le Markdown.
2.  **Validation des Specs** : Ne plus utiliser de checklists manuelles statiques. Adopter un processus où les specs sont liées aux tests d'acceptation (Gherkin/PyTest BDD) qui échouent si le code ne respecte pas la spec.
3.  **Politique de Dépendances** : Interdire l'ajout de dépendances sans déclaration explicite dans `pyproject.toml`. Scanner les vulnérabilités (ex: `pip-audit`) dans le pipeline CI.
4.  **Standardisation des Logs** : Utiliser le logging structuré (JSON) en production pour faciliter l'analyse par les outils d'observabilité, plutôt que des `print` ou des logs texte simples.
