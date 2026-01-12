# Feature Specification: CI/CD Integration - GitHub Actions Template

**Feature Branch**: `005-cicd-template`
**Created**: 2025-01-07
**Status**: Draft
**Target Version**: v2.13
**Depends On**: v2.8 (Headless Mode)

## Overview

Faciliter l'intégration de l'outil Aetheris dans les pipelines de développement modernes via un template GitHub Actions prêt à l'emploi. Ce template permettra d'automatiser l'analyse de code et la résolution de bugs directement dans le workflow CI/CD.

## User Scenarios & Testing

### User Story 1 - Automatic Analysis on Push/PR (Priority: P1)

En tant que développeur, je veux que l'analyse Aetheris s'exécute automatiquement sur mes push et pull requests pour détecter les problèmes avant la review.

**Why this priority**: Automatisation de base - valeur ajoutée principale de l'intégration CI/CD.

**Independent Test**: Créer un push sur une branche et vérifier que le workflow s'exécute et produit un rapport.

**Acceptance Scenarios**:

1. **Given** le workflow est configuré avec trigger `push`, **When** un développeur pousse du code, **Then** l'analyse Aetheris s'exécute automatiquement
2. **Given** le workflow est configuré avec trigger `pull_request`, **When** une PR est créée, **Then** l'analyse Aetheris s'exécute et ajoute un commentaire à la PR
3. **Given** l'analyse détecte des problèmes, **When** le workflow se termine, **Then** le statut de la PR reflète les résultats (fail si critiques)

---

### User Story 2 - Manual Workflow Trigger (Priority: P1)

En tant que développeur, je veux pouvoir lancer une analyse ou résolution manuellement depuis l'interface GitHub pour des scans à la demande.

**Why this priority**: Flexibilité essentielle pour les analyses ponctuelles ou les résolutions ciblées.

**Independent Test**: Utiliser `workflow_dispatch` dans GitHub pour déclencher manuellement le workflow.

**Acceptance Scenarios**:

1. **Given** le workflow est configuré avec `workflow_dispatch`, **When** un utilisateur clique "Run workflow" dans GitHub, **Then** l'analyse s'exécute avec les paramètres par défaut
2. **Given** des paramètres d'entrée sont définis, **When** l'utilisateur lance le workflow manuellement, **Then** il peut spécifier le mode (analysis, fix) et les fichiers cibles
3. **Given** un workflow manuel est lancé, **When** il se termine, **Then** les résultats sont disponibles dans les artifacts

---

### User Story 3 - Easy Template Setup (Priority: P2)

En tant que développeur, je veux un template facile à copier et personnaliser pour intégrer Aetheris dans mon projet en quelques minutes.

**Why this priority**: Réduction du temps d'adoption - l'intégration doit être simple.

**Independent Test**: Copier le template, configurer un secret API, et exécuter le workflow avec succès.

**Acceptance Scenarios**:

1. **Given** un nouveau projet, **When** le développeur copie le template dans `.github/workflows/`, **Then** le workflow est prêt à exécuter après configuration du secret API
2. **Given** le template, **When** le développeur lit la documentation, **Then** il comprend comment personnaliser les options (timeout, fichiers exclus, etc.)
3. **Given** une clé API manquante, **When** le workflow s'exécute, **Then** un message d'erreur clair indique comment configurer le secret

---

### User Story 4 - Download Artifacts & Local Execution (Priority: P2)

En tant que développeur, je veux pouvoir télécharger les artifacts d'analyse et exécuter des commandes localement (fix, etc.) pour résoudre les problèmes détectés.

**Why this priority**: Permet un workflow complet analyse-correction sans refaire l'analyse localement.

**Independent Test**: Télécharger l'artifact, exécuter le script de setup, puis lancer `aetheris fix`.

**Acceptance Scenarios**:

1. **Given** le workflow a terminé l'analyse, **When** je télécharge l'artifact, **Then** j'obtiens un zip avec les rapports d'analyse et un script de setup
2. **Given** l'artifact téléchargé, **When** j'exécute le script de setup, **Then** le dossier `docs/analyses/` est créé avec les rapports
3. **Given** les rapports installés localement, **When** j'exécute `aetheris fix`, **Then** les bugs détectés par le CI peuvent être corrigés sans relancer l'analyse
4. **Given** l'artifact, **When** je consulte le README inclus, **Then** les instructions d'utilisation locale sont documentées
5. **Given** un workflow manuel avec mode `fix`, **When** le workflow se termine, **Then** les corrections sont commitées automatiquement (si configuré)

---

### User Story 5 - Changed Files Analysis (Priority: P2)

En tant que développeur, je veux que seuls les fichiers modifiés soient analysés pour optimiser le temps d'exécution.

**Why this priority**: Optimisation importante pour les grands projets avec beaucoup de fichiers.

**Independent Test**: Modifier 2 fichiers et vérifier que seuls ces 2 fichiers sont analysés.

**Acceptance Scenarios**:

1. **Given** un push avec 3 fichiers modifiés, **When** l'analyse s'exécute, **Then** seuls les 3 fichiers modifiés sont analysés
2. **Given** une PR avec des modifications, **When** l'analyse s'exécute, **Then** le rapport mentionne uniquement les fichiers de la PR
3. **Given** l'option full-scan activée, **When** l'analyse s'exécute, **Then** tous les fichiers du projet sont analysés

---

### Edge Cases

- Que se passe-t-il si le workflow atteint la limite de temps GitHub Actions (6 heures)?
- Comment gérer les erreurs de rate-limiting de l'API Aetheris?
- Que se passe-t-il si aucun fichier n'a été modifié (merge vide)?
- Comment gérer les conflits entre analyses concurrentes sur la même branche?
- Que se passe-t-il si l'artifact est téléchargé sur un OS différent (Windows vs Linux)?
- Comment gérer les permissions du script de setup sur différents systèmes?
- Que se passe-t-il si le dossier docs/analyses/ existe déjà localement?
- Comment gérer le mode fix si aucune clé API n'est configurée localement?

## Requirements

### Functional Requirements

- **FR-001**: Le template DOIT supporter le trigger `push` pour l'analyse automatique
- **FR-002**: Le template DOIT supporter le trigger `pull_request` pour l'analyse des PRs
- **FR-003**: Le template DOIT supporter le trigger `workflow_dispatch` pour l'exécution manuelle
- **FR-004**: Le template DOIT permettre de configurer le mode d'exécution (analysis, fix)
- **FR-005**: Le template DOIT détecter automatiquement les fichiers modifiés dans le commit/PR
- **FR-006**: Le template DOIT publier les résultats dans les artifacts GitHub
- **FR-007**: Le template DOIT ajouter un commentaire de résumé sur les PRs
- **FR-008**: Le template DOIT gérer la clé API via GitHub Secrets
- **FR-009**: Le template DOIT échouer (exit code non-zero) si des problèmes critiques sont détectés
- **FR-010**: Le template DOIT être documenté avec des commentaires explicatifs
- **FR-011**: Le template DOIT permettre de configurer les fichiers/dossiers à exclure
- **FR-012**: Le template DOIT supporter la configuration du timeout via input
- **FR-013**: L'artifact DOIT inclure un script de setup (`setup-local.sh` / `setup-local.ps1`) pour installer les rapports localement
- **FR-014**: L'artifact DOIT inclure un README avec les instructions d'utilisation locale
- **FR-015**: Le script de setup DOIT créer le dossier `docs/analyses/` et y copier les rapports
- **FR-016**: Le template DOIT supporter un mode `fix` qui exécute les corrections et commit les changements
- **FR-017**: L'artifact DOIT être structuré pour être directement compatible avec `aetheris fix`

### Key Entities

- **WorkflowTemplate**: Fichier YAML du workflow GitHub Actions
- **WorkflowInputs**: Paramètres configurables (mode, timeout, exclusions)
- **AnalysisResult**: Résultat de l'analyse (succès/échec, rapport)
- **AnalysisArtifact**: Archive ZIP contenant rapports, scripts de setup, et README

## Success Criteria

### Measurable Outcomes

- **SC-001**: Un développeur peut intégrer Aetheris dans son projet en moins de 5 minutes
- **SC-002**: 100% des workflows avec triggers configurés s'exécutent automatiquement
- **SC-003**: Les résultats d'analyse sont visibles dans la PR dans les 2 minutes suivant la fin
- **SC-004**: Le template fonctionne sans modification sur 90% des projets standards
- **SC-005**: L'analyse des fichiers modifiés réduit le temps d'exécution d'au moins 50% vs full scan
- **SC-006**: Un développeur peut télécharger l'artifact et lancer `aetheris fix` en moins de 2 minutes
- **SC-007**: Le script de setup fonctionne sur Windows, macOS et Linux sans modification

## Assumptions

- Les utilisateurs ont un compte GitHub avec accès aux Actions
- Les utilisateurs ont une clé API Aetheris valide
- Les projets utilisent une structure standard (src/, lib/, etc.)
- GitHub Actions est activé sur le repository cible

## Out of Scope

- Support d'autres plateformes CI/CD (GitLab CI, Jenkins, CircleCI)
- Interface de configuration graphique
- Intégration avec les outils de code review tiers
- Workflow de déploiement automatique des corrections
- Support des repositories privés avec runners self-hosted
- Stockage des patterns d'exclusion → **Voir 006-persistent-config** (section `analysis.*`)

## Config Integration (v3.0+)

À partir de v3.0, les options d'analyse seront configurables via `config.json`:

```json
{
  "analysis": {
    "exclude_patterns": ["**/node_modules/**", "**/.git/**"],
    "changed_files_only": false
  }
}
```

Le workflow GitHub Actions peut lire ces options depuis le config.json du projet.
