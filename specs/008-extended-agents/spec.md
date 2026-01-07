# Feature Specification: Extended Analysis Agents

**Feature Branch**: `008-extended-agents`
**Created**: 2025-01-07
**Status**: Draft
**Target Version**: v3.0.1
**Depends On**: v3.0 (Configuration Persistante & Fichier Local)

## Overview

Étendre le système d'analyse Aetheris de 6 à 10 agents spécialisés. Les 4 nouveaux agents couvrent des domaines d'analyse critiques non couverts actuellement: performance, contrats API, sécurité de typage, et conformité des données. La configuration des agents s'intègre au système config.json de la v3.0.

**Note**: Technical Debt et Documentation agents ont été retirés du scope car:
- Technical Debt: overlap avec Code Metrics (complexity) et Architect (circular deps)
- Documentation: les linters existants (ESLint, Pylint) font ce travail mieux

## User Scenarios & Testing

### User Story 1 - Selective Agent Activation (Priority: P1)

En tant qu'utilisateur, je veux activer/désactiver des agents spécifiques via config.json ou CLI pour personnaliser mon analyse.

**Why this priority**: Fondement de la flexibilité - permet aux utilisateurs de n'exécuter que les analyses pertinentes.

**Independent Test**: Configurer `enabled_agents: ["performance", "type_safety"]` et vérifier que seuls ces agents s'exécutent.

**Acceptance Scenarios**:

1. **Given** `enabled_agents: ["all"]` dans config.json, **When** l'analyse s'exécute, **Then** les 10 agents sont activés
2. **Given** `enabled_agents: ["performance", "api_contract"]`, **When** l'analyse s'exécute, **Then** seuls ces 2 agents + les 6 core s'exécutent
3. **Given** `--agents performance,api_contract` en CLI, **When** l'analyse s'exécute, **Then** le CLI override la config
4. **Given** `--skip-agents type_safety` en CLI, **When** l'analyse s'exécute, **Then** tous les agents sauf type_safety s'exécutent

---

### User Story 2 - Performance Analysis (Priority: P1)

En tant que développeur, je veux détecter les problèmes de performance (O(n²), N+1, memory leaks) avant qu'ils n'atteignent la production.

**Why this priority**: Les bugs de performance sont les plus coûteux en production.

**Independent Test**: Analyser un fichier avec une boucle O(n²) et vérifier que l'agent le détecte.

**Acceptance Scenarios**:

1. **Given** un fichier avec des boucles imbriquées sur la même collection, **When** l'analyse s'exécute, **Then** un issue de complexité O(n²) est rapporté
2. **Given** un fichier avec des requêtes DB dans une boucle, **When** l'analyse s'exécute, **Then** un issue N+1 query est rapporté
3. **Given** un fichier avec des ressources non fermées, **When** l'analyse s'exécute, **Then** un issue memory leak potentiel est rapporté
4. **Given** un fichier avec des opérations async bloquantes, **When** l'analyse s'exécute, **Then** un issue blocking async est rapporté

---

### User Story 3 - API Contract Analysis (Priority: P1)

En tant que développeur d'API, je veux détecter les violations de contrats REST et les breaking changes potentiels.

**Why this priority**: 80% des bugs se produisent aux frontières d'intégration.

**Independent Test**: Analyser une API avec des violations de nommage REST et vérifier la détection.

**Acceptance Scenarios**:

1. **Given** un endpoint GET avec un body, **When** l'analyse s'exécute, **Then** une violation HTTP method est rapportée
2. **Given** un endpoint avec nommage incohérent (camelCase vs snake_case), **When** l'analyse s'exécute, **Then** une violation naming est rapportée
3. **Given** un changement de type sur un champ existant, **When** l'analyse s'exécute, **Then** un breaking change potentiel est rapporté
4. **Given** un endpoint sans documentation OpenAPI, **When** l'analyse s'exécute, **Then** un undocumented endpoint est rapporté

---

### User Story 4 - Type Safety Analysis (Priority: P2)

En tant que développeur TypeScript/Python, je veux détecter les violations de type safety pour prévenir les erreurs runtime.

**Why this priority**: Les systèmes de types préviennent les bugs tôt - quantifier leur adoption.

**Independent Test**: Analyser un fichier TypeScript avec usage de `any` et vérifier la détection.

**Acceptance Scenarios**:

1. **Given** un fichier avec `any` ou `Any` usage, **When** l'analyse s'exécute, **Then** les usages sont comptés et localisés
2. **Given** un cast unsafe (`as any`, `# type: ignore`), **When** l'analyse s'exécute, **Then** un unsafe cast est rapporté
3. **Given** un accès potentiellement null sans vérification, **When** l'analyse s'exécute, **Then** un null safety issue est rapporté
4. **Given** des types de retour incohérents, **When** l'analyse s'exécute, **Then** un inconsistent return type est rapporté

---

### User Story 5 - Compliance/Privacy Analysis (Priority: P3)

En tant que responsable conformité, je veux détecter les violations GDPR/HIPAA/PCI pour éviter les sanctions.

**Why this priority**: Conformité configurable séparément pour raisons légales.

**Independent Test**: Configurer `compliance_agents: ["gdpr"]` et vérifier la détection de PII.

**Acceptance Scenarios**:

1. **Given** `compliance_agents: ["gdpr"]`, **When** des emails sont loggés, **Then** un PII logged violation est rapporté
2. **Given** `compliance_agents: ["hipaa"]`, **When** des données de santé non chiffrées sont détectées, **Then** un PHI violation est rapporté
3. **Given** `compliance_agents: ["pci_dss"]`, **When** des numéros de carte sont détectés, **Then** un PCI violation est rapporté
4. **Given** `compliance_agents: ["none"]`, **When** l'analyse s'exécute, **Then** aucune analyse de conformité n'est effectuée

---

### Edge Cases

- Que se passe-t-il si un agent échoue pendant l'analyse?
- Comment gérer les langages non supportés par certains agents?
- Que se passe-t-il si la configuration contient un nom d'agent invalide?
- Comment gérer les conflits entre agents (même issue détectée différemment)?
- Que se passe-t-il si compliance_agents contient des frameworks contradictoires?

## Requirements

### Functional Requirements

#### Configuration (intégré à v3.0)
- **FR-001**: Le système DOIT supporter `enabled_agents` dans config.json (valeurs: "all" ou liste d'agents)
- **FR-002**: Le système DOIT supporter `compliance_agents` dans config.json (valeurs: "none", "all", ou liste: gdpr, hipaa, pci_dss, ccpa)
- **FR-003**: Le système DOIT supporter `--agents` en CLI pour override la config
- **FR-004**: Le système DOIT supporter `--skip-agents` en CLI pour exclure des agents
- **FR-005**: Le système DOIT supporter `--compliance` en CLI pour activer les profils de conformité

#### Performance Analysis Agent
- **FR-006**: L'agent DOIT détecter les patterns O(n²) et O(n³) (boucles imbriquées)
- **FR-007**: L'agent DOIT détecter les N+1 query patterns
- **FR-008**: L'agent DOIT détecter les memory leak patterns (ressources non fermées)
- **FR-009**: L'agent DOIT détecter les opérations async bloquantes
- **FR-010**: L'agent DOIT estimer l'impact de performance pour chaque issue

#### API Contract Agent
- **FR-011**: L'agent DOIT détecter les violations de méthodes HTTP (GET avec body, etc.)
- **FR-012**: L'agent DOIT détecter les incohérences de nommage REST
- **FR-013**: L'agent DOIT détecter les breaking changes potentiels
- **FR-014**: L'agent DOIT détecter les endpoints non documentés

#### Type Safety Agent
- **FR-015**: L'agent DOIT compter et localiser les usages de `any`/`Any`
- **FR-016**: L'agent DOIT détecter les casts unsafe
- **FR-017**: L'agent DOIT détecter les violations de null safety

#### Data Privacy Agent
- **FR-018**: L'agent DOIT détecter les PII dans les logs (emails, SSN, téléphones)
- **FR-019**: L'agent DOIT détecter les données sensibles non chiffrées
- **FR-020**: L'agent DOIT associer chaque violation au framework de conformité approprié

### Key Entities

- **PerformanceIssue**: Issue de performance avec type, sévérité, impact estimé
- **APIContractViolation**: Violation de contrat API avec endpoint, méthode, type
- **TypeSafetyIssue**: Issue de type safety avec type, code snippet, suggestion
- **PrivacyViolation**: Violation de conformité avec framework, catégorie, remédiation

## Success Criteria

### Measurable Outcomes

- **SC-001**: Les 4 nouveaux agents s'exécutent en parallèle avec les 6 existants sans dégradation de performance (temps total +30% max)
- **SC-002**: 100% des options config.json pour les agents sont respectées
- **SC-003**: Chaque agent produit un rapport distinct dans docs/analyses/
- **SC-004**: Les violations de conformité sont catégorisées par framework (GDPR/HIPAA/PCI)
- **SC-005**: L'utilisateur peut activer/désactiver chaque agent individuellement
- **SC-006**: Les rapports sont exploitables par `aetheris fix` pour corrections automatiques

## Assumptions

- Les 6 agents core (existants) restent toujours actifs par défaut
- Les nouveaux agents sont opt-in par défaut (`enabled_agents: ["all"]` les active tous)
- Les agents de conformité sont opt-in et désactivés par défaut (`compliance_agents: ["none"]`)
- Chaque agent hérite de BaseAgent et utilise les mêmes patterns d'AI
- Les dataclasses de sortie suivent les conventions existantes dans data_models.py

## Out of Scope

- Correction automatique par les nouveaux agents (phase ultérieure)
- UI graphique pour la configuration des agents
- Agents spécifiques à un framework (React, Django, etc.)
- Analyse de performance runtime (profiling)
- Intégration avec des outils de conformité externes
- **Technical Debt Agent** (overlap avec Code Metrics et Architect existants)
- **Documentation Agent** (utiliser ESLint/Pylint plugins à la place)
