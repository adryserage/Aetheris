# Vue d'ensemble de l'architecture

*Généré le 2026-01-07 16:59:50*
*Nombre de fichiers analysés: 124*
*Fichiers réussis: 124*
*Fichiers échoués: 0*

---

Voici le rapport d'architecture complet basé sur l'analyse des 124 fichiers fournis du projet **Aetheris**.

# Rapport d'Architecture Logiciel - Projet Aetheris

## Vue d'ensemble de l'architecture

Ce document présente une analyse architecturale approfondie du système **Aetheris**, un outil CLI d'analyse de code statique et dynamique propulsé par des agents IA (Multi-Agent System). Le projet est actuellement dans une phase critique de transition vers un modèle de distribution binaire fermée (via Cython), tout en adoptant une méthodologie de développement pilotée par des spécifications rigoureuses (SpecKit).

L'analyse révèle un cœur technologique solide en Python asynchrone, mais obscurci par une dette technique documentaire importante (références fantômes à une stack JS/Next.js) et des choix de distribution (Binary-Only) qui introduisent des risques significatifs pour la maintenabilité et la sécurité.

## Table des matières
1.  Architecture et patterns identifiés
2.  Cohérence inter-modules
3.  Redondances, dépendances et couplages
4.  Recommandations d'optimisation
5.  Plan de refactoring
6.  Gouvernance du code

---

## 1. Architecture et patterns identifiés

L'architecture d'Aetheris repose sur plusieurs modèles de conception distincts :

### A. Pattern Orchestrator & Multi-Agents
Le cœur du système (`src/core/orchestrator.py`) implémente le pattern **Orchestrator**. Il coordonne un ensemble d'agents spécialisés (`src/agents/`) :
*   **CAE (Code Analysis Expert) :** Analyse statique et syntaxique.
*   **SSA (Security & Safety Agent) :** Détection de vulnérabilités.
*   **DVA (Dependency Vulnerability Agent) :** Audit des paquets tiers.
*   **QAA (Quality Assurance Agent) :** Validation des normes.

**Analyse :** Ce découpage est sain et favorise la séparation des responsabilités (SoC). L'utilisation d'une classe de base `BaseAgent` standardise les interactions avec les fournisseurs d'IA (Gemini, OpenAI, Claude).

### B. Architecture "Spec-First" (SpecKit)
Le projet suit une méthodologie stricte où le code est piloté par des documents Markdown structurés (`specs/`).
*   **Flux :** Requirement -> Spec -> Plan -> Tasks -> Code.
*   **Observation :** Les scripts Python (`scripts/*.py`) et l'analyseur de spécifications tentent de parser ces fichiers Markdown via des Regex pour piloter le développement. C'est une forme agressive de "Documentation as Code".

### C. Stratégie de Distribution "Closed Source"
Le projet utilise **Cython** (`setup.py`) non pas pour la performance, mais comme mécanisme d'obfuscation pour distribuer uniquement des binaires (`.so` / `.pyd`) et interdire l'accès au code source (`sdist` désactivé).

---

## 2. Cohérence inter-modules

L'analyse révèle des incohérences critiques qui menacent l'intégrité conceptuelle du projet.

### A. La "Stack Fantôme" (Incohérence Majeure)
Plusieurs fichiers de documentation et rapports d'architecture (`docs/architecture_overview.md`, `README.md`, `docs/installation.md`) contiennent des références explicites à **Next.js**, **Node.js**, **React** et **npm install**, alors que le code source est quasi-exclusivement en **Python** (avec un peu de Cython).
*   **Impact :** Confusion totale pour les développeurs et les utilisateurs. Risque d'erreur lors de l'installation des dépendances.
*   **Cause probable :** Copier-coller non nettoyé d'un template de projet web ou pivot technologique mal documenté.

### B. Gestion des versions fragmentée
Il n'y a pas de "Single Source of Truth" (SSOT) pour la version du logiciel.
*   `setup.py` définit sa propre version.
*   Les workflows GitHub (`auto-release.yml`) tentent d'extraire la version via `tomllib` depuis `pyproject.toml` (qui semble incomplet ou en conflit avec `setup.py`).
*   Des scripts Regex (`extract_release_notes.py`) parsent le `CHANGELOG.md`.
*   **Risque :** Désynchronisation entre le tag Git, la release PyPI et la version affichée dans la CLI.

### C. Rupture de la chaîne de confiance (CI/CD)
Le workflow de distribution binaire (`specs/001-cython-binary-dist`) interdit la publication des sources (`sdist`). Cependant, les workflows GitHub utilisent des actions tierces avec des tags mutables (`@v2`) et installent des dépendances sans vérification de hachage.
*   **Incohérence :** On cherche à protéger le code (Cython) mais on laisse la porte ouverte aux attaques de la chaîne d'approvisionnement (Supply Chain Attacks) dans le pipeline de build.

---

## 3. Redondances, dépendances ou couplages excessifs

### A. Couplage Fort : Code <-> Documentation Markdown
Le système repose sur le parsing de fichiers Markdown (`specs/*.md`) via des expressions régulières pour valider l'avancement ou générer du cache (`generate_bugs_cache.py`).
*   **Problème :** Le Markdown est un format de présentation pour humains. Un simple changement d'espace, de niveau de titre ou de formatage brise les scripts d'automatisation.
*   **Diagnostic :** Couplage excessif entre la forme (doc) et la fonction (code).

### B. Gestion des Dépendances (Manquantes et Implicites)
L'analyse des imports Python vs les fichiers de configuration révèle de graves lacunes :
*   **Imports orphelins :** `google.genai`, `requests`, `PyYAML`, `rich` sont utilisés massivement mais absents d'un fichier de verrouillage central fiable (le `setup.py` est incomplet et le `pyproject.toml` semble ne gérer que le build system).
*   **Dépendances système :** Certains scripts assument la présence de `gh` (GitHub CLI) ou de `npm` sans vérification robuste au runtime.

### C. Redondance des scripts de configuration
Présence de `setup-local.sh` et `setup-local.ps1` (mentionnés dans `docs/cicd-template`).
*   **Risque :** Divergence logique classique entre les scripts Shell et PowerShell. Une modification sur l'un est souvent oubliée sur l'autre.

---

## 4. Recommandations d'optimisation

### A. Architecture de Build (Priorité Haute)
Abandonner l'approche `setup.py` impérative au profit d'une configuration déclarative moderne (**PEP 621**).
*   **Action :** Centraliser toutes les métadonnées, dépendances et scripts de build dans `pyproject.toml`.
*   **Outil recommandé :** **Hatch** ou **Poetry** pour gérer les environnements virtuels et les builds de manière déterministe.

### B. Sécurisation du Pipeline CI/CD
*   **Pinning :** Remplacer tous les tags d'actions (ex: `actions/checkout@v4`) par leurs SHA immuables.
*   **Permissions :** Appliquer le principe de moindre privilège dans tous les workflows YAML (supprimer les droits d'écriture globaux).
*   **Sanitization :** Corriger les injections de variables directes dans les scripts shell (`${{ inputs.x }}`).

### C. Refonte de la Distribution Binaire
La stratégie "Cython-only" sans `sdist` est fragile (casse sur Alpine/musllinux, architectures futures).
*   **Optimisation :** Utiliser **PyInstaller** ou **Nuitka** si l'objectif est de créer un exécutable autonome. Ces outils sont conçus pour cela, contrairement à Cython qui est conçu pour l'interfaçage C/Performance.
*   **Alternative :** Si Cython est maintenu, rétablir la publication des sources (`sdist`) pour la compatibilité, ou assurer une matrice de build exhaustive (incluant `musllinux`).

---

## 5. Plan de refactoring

Ce plan est priorisé par criticité (Sécurité > Stabilité > Fonctionnalité).

### Phase 1 : Assainissement et Sécurité (Semaine 1)
1.  **Nettoyage Contextuel :** Supprimer toutes les références à Next.js/Node.js/React de la documentation et des fichiers de configuration (`docs/*`, `README.md`).
2.  **Sécurisation Secrets :** Supprimer les arguments CLI `--token` dans les scripts et la documentation. Forcer l'usage exclusif de variables d'environnement (`GITHUB_TOKEN`).
3.  **Fix GitHub Actions :**
    *   Ajouter `permissions: contents: read` par défaut.
    *   Épingler les actions par SHA.
    *   Supprimer les injections de shell (`run: ... ${{ inputs }} ...`).

### Phase 2 : Standardisation des Dépendances (Semaine 2)
1.  **Adoption PEP 621 :** Créer un `pyproject.toml` complet.
2.  **Freeze des dépendances :** Générer un fichier de lock avec hachages (via `uv` ou `pip-tools`) pour garantir que `requests`, `google-genai`, etc., sont installés dans des versions testées.
3.  **Correction Imports :** Ajouter les bibliothèques manquantes (`types-requests`, `types-PyYAML`) pour satisfaire le typage statique.

### Phase 3 : Découplage Docs/Code (Semaine 3)
1.  **Migration des Specs :** Cesser de parser le Markdown. Si les specs doivent piloter le code, les convertir en format structuré (YAML/JSON) avec un schéma JSON Schema validation.
2.  **Génération de Docs :** Inverser le flux : générer la documentation lisible (Markdown) à partir des fichiers de définition structurés (et non l'inverse).

### Phase 4 : Architecture de Distribution (Semaine 4)
1.  **Réévaluation Cython :** Lancer un POC avec **Nuitka**. Si concluant (binaire unique, pas de dépendance Python système chez le client), remplacer la pipeline Cython complexe.
2.  **Pipeline de Release :** Unifier la gestion de version. Utiliser `setuptools_scm` ou `hatch-vcs` pour que le tag Git soit l'unique source de vérité pour la version du package.

---

## 6. Gouvernance du code

Pour maintenir la qualité architecturale sur le long terme :

1.  **Règle "Zero Hallucination" :** Toute référence technologique dans la documentation (ex: "Node.js") doit correspondre à une dépendance réelle dans le fichier de lock. Un linter de documentation doit être mis en place.
2.  **Tests Automatisés Obligatoires :** La spécification actuelle indique "No automated tests requested". C'est inacceptable pour un produit distribué.
    *   **Imposer :** Tests unitaires (`pytest`) pour chaque Agent.
    *   **Imposer :** Tests d'intégration pour le build binaire avant release.
3.  **Workflow de Spécification :**
    *   Arrêter l'utilisation de regex fragiles pour valider les specs.
    *   Utiliser des templates de Pull Request GitHub pour valider manuellement ou via des outils structurés que les specs sont respectées.
4.  **Gestion des Secrets :** Interdire strictement le commit de fichiers `.env` (via `pre-commit hooks` type `detect-secrets`) et l'affichage de secrets dans les logs CLI.
