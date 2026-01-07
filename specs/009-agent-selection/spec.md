# Feature Specification: Agent Selection & Targeted Fix

**Feature Branch**: `feature/009-agent-selection`
**Created**: 2025-01-07
**Status**: Draft
**Target Version**: v3.0.2
**Depends On**: v3.0.1 (Extended Analysis Agents)

## Overview

Permettre aux utilisateurs de sélectionner précisément quels agents exécuter et de cibler les corrections (`aetheris fix`) sur des catégories spécifiques d'issues. Cette fonctionnalité permet une analyse focalisée et des corrections ciblées, réduisant le bruit et les coûts API.

## User Scenarios & Testing

### User Story 1 - Selective Agent Analysis (Priority: P1)

En tant qu'utilisateur, je veux exécuter uniquement certains agents pour une analyse focalisée et économique.

**Why this priority**: Réduit les coûts API et le temps d'analyse en ne lançant que les agents pertinents.

**Independent Test**: Exécuter `aetheris analysis --agents compliance` et vérifier que seul l'agent Data Privacy s'exécute.

**Acceptance Scenarios**:

1. **Given** `--agents performance`, **When** l'analyse s'exécute, **Then** seul l'agent Performance + core agents s'exécutent
2. **Given** `--agents compliance --compliance gdpr`, **When** l'analyse s'exécute, **Then** seul l'agent Data Privacy avec profil GDPR s'exécute
3. **Given** `--agents security,performance`, **When** l'analyse s'exécute, **Then** Security + Performance agents s'exécutent
4. **Given** `--agents none --compliance all`, **When** l'analyse s'exécute, **Then** seuls les agents de conformité s'exécutent (pas les core)

---

### User Story 2 - Targeted Fix by Agent Category (Priority: P1)

En tant qu'utilisateur, je veux corriger uniquement les issues d'une catégorie spécifique (ex: seulement les issues de conformité).

**Why this priority**: Permet des corrections focalisées sans toucher au reste du code.

**Independent Test**: Exécuter `aetheris fix --category compliance` et vérifier que seules les violations de conformité sont corrigées.

**Acceptance Scenarios**:

1. **Given** un rapport avec des issues de plusieurs catégories, **When** `aetheris fix --category compliance`, **Then** seules les PrivacyViolation sont corrigées
2. **Given** un rapport avec des issues performance, **When** `aetheris fix --category performance`, **Then** seules les PerformanceIssue sont corrigées
3. **Given** un rapport mixte, **When** `aetheris fix --category security,performance`, **Then** SecurityIssue + PerformanceIssue sont corrigées
4. **Given** `--category compliance --compliance gdpr`, **When** fix s'exécute, **Then** seules les violations GDPR sont corrigées

---

### User Story 3 - Agent Presets (Priority: P2)

En tant qu'utilisateur régulier, je veux des presets prédéfinis pour les combinaisons d'agents courantes.

**Why this priority**: Simplifie l'utilisation pour les cas d'usage fréquents.

**Independent Test**: Exécuter `aetheris analysis --preset security-audit` et vérifier la bonne combinaison d'agents.

**Acceptance Scenarios**:

1. **Given** `--preset security-audit`, **When** l'analyse s'exécute, **Then** Security + Data Privacy + Dependency agents s'exécutent
2. **Given** `--preset performance-review`, **When** l'analyse s'exécute, **Then** Performance + Metrics + Architecture agents s'exécutent
3. **Given** `--preset quick-scan`, **When** l'analyse s'exécute, **Then** seuls Code Analysis + Security s'exécutent (minimal)
4. **Given** `--preset compliance-gdpr`, **When** l'analyse s'exécute, **Then** Data Privacy avec profil GDPR s'exécute

---

### User Story 4 - Interactive Agent Selection (Priority: P2)

En tant qu'utilisateur, je veux sélectionner interactivement les agents avant l'analyse.

**Why this priority**: UX améliorée pour les utilisateurs qui ne connaissent pas tous les agents.

**Independent Test**: Exécuter `aetheris analysis --interactive` et vérifier l'affichage du menu de sélection.

**Acceptance Scenarios**:

1. **Given** `--interactive`, **When** l'analyse démarre, **Then** un menu checkbox avec tous les agents disponibles s'affiche
2. **Given** le menu interactif, **When** l'utilisateur sélectionne 3 agents, **Then** seuls ces 3 agents s'exécutent
3. **Given** le menu interactif, **When** l'utilisateur appuie sur Entrée sans sélection, **Then** tous les agents s'exécutent (défaut)
4. **Given** `--interactive --preset security-audit`, **When** le menu s'affiche, **Then** les agents du preset sont pré-sélectionnés

---

### User Story 5 - Fix Progress by Category (Priority: P3)

En tant qu'utilisateur, je veux voir la progression des corrections par catégorie.

**Why this priority**: Visibilité sur l'avancement des corrections ciblées.

**Independent Test**: Exécuter `aetheris fix --category all` et vérifier l'affichage de progression par catégorie.

**Acceptance Scenarios**:

1. **Given** un fix en cours, **When** la progression s'affiche, **Then** chaque catégorie a sa propre barre de progression
2. **Given** `--category compliance`, **When** le fix termine, **Then** un résumé montre "Compliance: 5/5 fixed"
3. **Given** plusieurs catégories, **When** le fix termine, **Then** un tableau récapitulatif par catégorie s'affiche

---

### Edge Cases

- Que se passe-t-il si `--agents` contient un nom d'agent invalide?
- Que se passe-t-il si `--category` ne correspond à aucune issue dans le rapport?
- Comment gérer `--agents none` sans `--compliance`? (erreur ou warning?)
- Que se passe-t-il si un preset est combiné avec `--agents`? (override ou merge?)

## Requirements

### Functional Requirements

#### Agent Selection
- **FR-001**: Le CLI DOIT supporter `--agents <liste>` pour sélectionner les agents à exécuter
- **FR-002**: Les valeurs valides pour `--agents` sont: `all`, `none`, `core`, ou noms d'agents séparés par virgules
- **FR-003**: `--agents none` DOIT désactiver tous les agents optionnels (ne garde que core si spécifié)
- **FR-004**: `--agents core` DOIT exécuter uniquement les 6 agents de base
- **FR-005**: Les noms d'agents invalides DOIVENT générer une erreur avec la liste des agents valides

#### Targeted Fix
- **FR-006**: Le CLI `aetheris fix` DOIT supporter `--category <liste>` pour cibler les corrections
- **FR-007**: Les catégories valides sont: `security`, `performance`, `api_contract`, `type_safety`, `compliance`, `code_quality`, `architecture`, `metrics`
- **FR-008**: `--category all` DOIT corriger toutes les catégories (comportement par défaut)
- **FR-009**: `--category compliance --compliance gdpr` DOIT cibler uniquement les violations GDPR
- **FR-010**: Les issues non ciblées DOIVENT être ignorées mais préservées dans le rapport

#### Presets
- **FR-011**: Le CLI DOIT supporter `--preset <nom>` pour les combinaisons prédéfinies
- **FR-012**: Presets disponibles: `security-audit`, `performance-review`, `compliance-gdpr`, `compliance-hipaa`, `compliance-pci`, `quick-scan`, `full-analysis`
- **FR-013**: Les presets DOIVENT être configurables via config.json (custom presets)
- **FR-014**: `--preset` combiné avec `--agents` DOIT merger les sélections (union)

#### Interactive Mode
- **FR-015**: `--interactive` DOIT afficher un menu de sélection avec Rich/Textual
- **FR-016**: Le menu DOIT permettre la sélection multiple avec checkboxes
- **FR-017**: Le menu DOIT afficher une description courte de chaque agent
- **FR-018**: Les agents pré-sélectionnés par preset DOIVENT être cochés par défaut

#### Progress & Reporting
- **FR-019**: La progression du fix DOIT afficher le compteur par catégorie
- **FR-020**: Le rapport final DOIT inclure un résumé par catégorie (fixed/skipped/failed)

### Key Entities

- **AgentPreset**: Preset avec nom, description, liste d'agents, profils de conformité
- **FixCategory**: Catégorie de fix avec nom, agent source, types d'issues associés
- **CategoryProgress**: Progression par catégorie avec total, fixed, skipped, failed

## Success Criteria

### Measurable Outcomes

- **SC-001**: L'utilisateur peut exécuter une analyse avec un seul agent en <30s (vs ~2min pour tous)
- **SC-002**: `aetheris fix --category compliance` ne modifie que les fichiers avec violations de conformité
- **SC-003**: 100% des presets sont documentés avec leurs agents inclus
- **SC-004**: Le mode interactif s'affiche en <1s
- **SC-005**: Le rapport final affiche clairement les statistiques par catégorie

## Assumptions

- Les 10 agents (6 core + 4 extended) sont disponibles (v3.0.1)
- Le système config.json v3.0 est en place
- Les rapports d'analyse contiennent la catégorie/agent source de chaque issue
- Rich/Textual est disponible pour le mode interactif

## Out of Scope

- Création de nouveaux agents (couvert par v3.0.1)
- UI graphique (CLI only)
- Scheduling/cron pour analyses automatiques
- Notifications (email, Slack) sur completion
