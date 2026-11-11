# Feature Specification: Documentation Update

**Feature Branch**: `007-docs-update`
**Created**: 2025-01-07
**Status**: Draft
**Target Version**: v2.10

## Overview

Mettre à jour l'ensemble de la documentation (README.md et dossier docs/) pour refléter toutes les fonctionnalités implémentées depuis la v2.4.0, incluant les nouvelles commandes, les améliorations de performance, et les options CLI ajoutées. Cette mise à jour vise à garantir que la documentation reste synchronisée avec le code source.

## User Scenarios & Testing

### User Story 1 - Updated README Quick Reference (Priority: P1)

En tant que nouvel utilisateur, je veux que le README reflète toutes les commandes disponibles pour savoir ce que l'outil peut faire.

**Why this priority**: Le README est le premier point de contact - doit être à jour.

**Independent Test**: Lire le README et vérifier que chaque commande mentionnée existe dans le CLI.

**Acceptance Scenarios**:

1. **Given** le README, **When** je consulte la section Commands, **Then** toutes les commandes actuelles sont listées (analysis, fix, pr, issues, pr-gen, stats)
2. **Given** le README, **When** je cherche une option CLI, **Then** les options principales sont documentées avec des exemples
3. **Given** le README, **When** je consulte les badges, **Then** la version Python indique 3.9+ (pas 3.8+)

---

### User Story 2 - Complete Command Documentation (Priority: P1)

En tant qu'utilisateur avancé, je veux une documentation détaillée de chaque commande dans docs/commands/ pour utiliser toutes les options.

**Why this priority**: Documentation de référence essentielle pour l'utilisation quotidienne.

**Independent Test**: Pour chaque commande, exécuter `aetheris <cmd> --help` et vérifier que docs/commands/<cmd>.md couvre toutes les options.

**Acceptance Scenarios**:

1. **Given** la commande `aetheris stats`, **When** je consulte docs/commands/stats.md, **Then** toutes les options sont documentées
2. **Given** la commande `aetheris fix`, **When** je consulte docs/commands/fix.md, **Then** les options `--timeout`, `--batch-size`, `--severity` sont expliquées
3. **Given** chaque fichier dans docs/commands/, **When** je le compare à `--help`, **Then** 100% des options sont couvertes

---

### User Story 3 - Configuration Reference (Priority: P2)

En tant qu'utilisateur configurant l'outil, je veux une référence complète du système de configuration (config.json, hiérarchie, commande `settings`).

**Why this priority**: Nécessaire pour personnaliser l'outil mais pas critique pour commencer.

**Independent Test**: Comparer docs/configuration.md avec le schéma config.json et les options de `aetheris settings`.

**Acceptance Scenarios**:

1. **Given** docs/configuration.md, **When** je consulte la structure, **Then** le format config.json est documenté avec toutes les options disponibles
2. **Given** docs/configuration.md, **When** je cherche la hiérarchie, **Then** l'ordre de priorité est expliqué (CLI > Local config > Global config > Env vars > Defaults)
3. **Given** docs/configuration.md, **When** je cherche la config AI, **Then** les 3 providers (Gemini, Claude, OpenAI) sont documentés avec leurs modèles
4. **Given** docs/configuration.md, **When** je cherche la commande settings, **Then** l'utilisation de `aetheris settings` et `aetheris init` est documentée
5. **Given** docs/configuration.md, **When** je cherche les secrets, **Then** la séparation secrets (.env) vs préférences (config.json) est expliquée

---

### User Story 4 - Features Overview (Priority: P2)

En tant qu'évaluateur potentiel, je veux une vue d'ensemble des fonctionnalités pour comprendre ce que l'outil fait.

**Why this priority**: Important pour l'adoption mais pas bloquant pour l'usage.

**Independent Test**: Comparer docs/features.md avec les fonctionnalités réellement disponibles.

**Acceptance Scenarios**:

1. **Given** docs/features.md, **When** je consulte la liste, **Then** les nouvelles fonctionnalités (multi-provider consensus, caching, parallel analysis) sont documentées
2. **Given** docs/features.md, **When** je cherche le ROI, **Then** les métriques de statistiques sont expliquées
3. **Given** docs/features.md, **When** je cherche la sécurité, **Then** le security agent et l'OSV API sont mentionnés

---

### User Story 5 - GitHub Actions Integration (Priority: P2)

En tant que DevOps, je veux une documentation CI/CD complète pour intégrer Aetheris dans mes pipelines.

**Why this priority**: Critique pour l'adoption en entreprise mais pas pour l'usage local.

**Independent Test**: Copier l'exemple GitHub Actions et vérifier qu'il fonctionne.

**Acceptance Scenarios**:

1. **Given** docs/github-actions.md, **When** je copie le workflow, **Then** l'analyse s'exécute correctement sur une PR
2. **Given** docs/github-actions.md, **When** je cherche les variables secrets, **Then** les API keys requises sont listées
3. **Given** docs/github-actions.md, **When** je cherche l'analyse de fichiers modifiés, **Then** l'option `--changed-files-only` est documentée

---

### User Story 6 - Troubleshooting Guide (Priority: P3)

En tant qu'utilisateur rencontrant un problème, je veux un guide de dépannage à jour pour résoudre les erreurs courantes.

**Why this priority**: Utile mais pas critique pour la majorité des utilisateurs.

**Independent Test**: Pour chaque erreur courante, vérifier que la solution est documentée.

**Acceptance Scenarios**:

1. **Given** docs/troubleshooting.md, **When** je cherche une erreur API, **Then** les solutions pour les 3 providers sont documentées
2. **Given** docs/troubleshooting.md, **When** je cherche les erreurs de rate limit, **Then** les stratégies de retry sont expliquées
3. **Given** docs/troubleshooting.md, **When** je cherche les erreurs de timeout, **Then** l'option `--timeout` est mentionnée

---

### Edge Cases

- Comment gérer les sections de documentation obsolètes?
- Comment versionner la documentation (match avec le code)?
- Comment gérer les screenshots/GIFs qui peuvent devenir obsolètes?
- Comment maintenir la cohérence entre README et docs/?

## Requirements

### Functional Requirements

- **FR-001**: Le README DOIT lister toutes les commandes disponibles (analysis, fix, pr, issues, pr-gen, stats)
- **FR-002**: Le README DOIT afficher la version Python requise (3.9+, pas 3.8+)
- **FR-003**: Chaque commande DOIT avoir un fichier docs/commands/<cmd>.md
- **FR-004**: docs/commands/stats.md DOIT documenter la commande `aetheris stats` (à créer)
- **FR-005**: Chaque option CLI DOIT être documentée avec description et exemple
- **FR-006**: docs/configuration.md DOIT documenter le système config.json (structure, hiérarchie, commandes init/settings)
- **FR-007**: docs/features.md DOIT inclure les nouvelles fonctionnalités (caching, parallel, consensus)
- **FR-008**: docs/github-actions.md DOIT fournir un exemple de workflow fonctionnel
- **FR-009**: docs/troubleshooting.md DOIT couvrir les erreurs courantes des 3 providers
- **FR-010**: La documentation DOIT utiliser des exemples de code exécutables
- **FR-011**: Les liens internes entre documents DOIVENT être fonctionnels
- **FR-012**: Le CHANGELOG DOIT être à jour avec toutes les versions récentes

### Key Entities

- **README.md**: Point d'entrée principal de la documentation
- **docs/commands/**: Documentation détaillée par commande
- **docs/configuration.md**: Référence du système config.json (structure, hiérarchie, commandes)
- **docs/features.md**: Vue d'ensemble des fonctionnalités
- **docs/github-actions.md**: Guide d'intégration CI/CD
- **docs/troubleshooting.md**: Guide de dépannage
- **CHANGELOG.md**: Historique des versions

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% des commandes CLI sont documentées dans le README et docs/commands/
- **SC-002**: 100% des options `--help` correspondent à la documentation
- **SC-003**: 100% des options config.json sont documentées avec leur hiérarchie de priorité
- **SC-004**: 0 liens cassés dans la documentation
- **SC-005**: Les exemples de code dans la documentation sont exécutables sans modification
- **SC-006**: Le temps pour trouver une information spécifique n'excède pas 30 secondes

## Assumptions

- La documentation utilise le format Markdown standard
- Les exemples de code sont testables manuellement
- La documentation est en anglais avec des notes en français si nécessaire
- Les captures d'écran ne sont pas nécessaires (CLI text-based)

## Out of Scope

- Documentation multilingue (FR/EN séparée)
- Site de documentation statique (MkDocs, Docusaurus)
- Documentation API générée automatiquement
- Tutoriels vidéo
- Documentation interactive (playgrounds)
