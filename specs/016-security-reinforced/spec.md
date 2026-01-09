# Feature Specification: Sécurité Renforcée & Stratégie Git

**Feature Branch**: `016-security-reinforced`
**Created**: 2026-01-09
**Status**: Draft
**Target Version**: v3.1
**Depends On**: v3.0 (Persistent Config)

## Overview

Regrouper toutes les garanties de sécurité et d'hygiène de code avant de passer à l'échelle sur les agents autonomes. Cette version introduit des profils de sécurité configurables, une stratégie Git d'isolation par fix, et une transparence complète sur les opérations effectuées.

## User Scenarios & Testing

### User Story 1 - Security Profiles (Priority: P1)

En tant qu'utilisateur d'Aetheris, je veux pouvoir choisir un profil de sécurité adapté à mon contexte (développement local, CI/CD, avancé) pour contrôler le niveau de restrictions appliqué aux opérations automatiques.

**Why this priority**: Fondation de sécurité - toutes les opérations d'agents autonomes dépendent de ces profils pour éviter des actions non désirées.

**Independent Test**: Lancer `aetheris fix --auto --profile safe` et vérifier que les commandes réseau sont bloquées et que seules les commandes whitelistées s'exécutent.

**Acceptance Scenarios**:

1. **Given** l'utilisateur utilise le profil `safe` (défaut), **When** un agent tente d'exécuter une commande réseau, **Then** la commande est bloquée avec un message explicatif
2. **Given** l'utilisateur utilise le profil `safe`, **When** un agent génère un diff >50 lignes, **Then** une confirmation est demandée avant application
3. **Given** l'utilisateur utilise le profil `ci`, **When** une opération s'exécute, **Then** aucune interaction n'est demandée et tout est loggué dans l'audit
4. **Given** l'utilisateur utilise le profil `unrestricted`, **When** un agent tente une opération, **Then** toutes les opérations sont autorisées sans restriction
5. **Given** un profil inconnu est spécifié, **When** l'utilisateur lance une commande, **Then** un message d'erreur liste les profils valides

---

### User Story 2 - Git Strategy "One Branch Per Fix" (Priority: P1)

En tant qu'utilisateur d'Aetheris, je veux que chaque correction automatique soit isolée dans sa propre branche Git temporaire pour éviter les conflits avec mon travail en cours et permettre un rollback facile.

**Why this priority**: Isolation critique - évite les corruptions du worktree principal et permet des corrections atomiques.

**Independent Test**: Lancer `aetheris fix --auto` sur un bug et vérifier qu'une branche `fix/issue-xxx` est créée, que le fix est appliqué, et que la branche peut être supprimée proprement si le fix échoue.

**Acceptance Scenarios**:

1. **Given** un fix automatique est lancé, **When** Aetheris commence le traitement, **Then** une branche temporaire `fix/{issue-id}` est créée depuis la branche courante
2. **Given** un fix est en cours sur une branche temporaire, **When** le fix réussit, **Then** l'utilisateur peut choisir de merger ou garder la branche pour review
3. **Given** un fix échoue, **When** Aetheris détecte l'échec, **Then** la branche temporaire est supprimée automatiquement et le worktree revient à l'état initial
4. **Given** plusieurs fixes sont lancés en parallèle, **When** ils s'exécutent, **Then** chaque fix a sa propre branche isolée sans interférence
5. **Given** l'utilisateur a des changements non commités, **When** il lance un fix, **Then** Aetheris refuse de procéder et demande de stash ou commit d'abord

---

### User Story 3 - Audit Logging & Transparency (Priority: P2)

En tant qu'utilisateur d'Aetheris, je veux avoir une trace complète et transparente de toutes les opérations effectuées par les agents pour pouvoir auditer et comprendre ce qui a été modifié.

**Why this priority**: Transparence essentielle - permet la confiance et la traçabilité des opérations automatiques.

**Independent Test**: Lancer plusieurs opérations et vérifier que le fichier d'audit contient toutes les actions avec timestamps, commandes exécutées, et résultats.

**Acceptance Scenarios**:

1. **Given** une opération sensible est effectuée, **When** elle se termine, **Then** une entrée est ajoutée au fichier d'audit avec timestamp, action, résultat
2. **Given** le mode verbose est activé, **When** une opération s'exécute, **Then** les détails sont affichés en temps réel dans la console
3. **Given** l'utilisateur veut consulter l'historique, **When** il exécute `aetheris audit`, **Then** les dernières opérations sont affichées de façon lisible
4. **Given** le fichier d'audit atteint une taille limite, **When** une nouvelle entrée est ajoutée, **Then** les anciennes entrées sont archivées ou rotées

---

### User Story 4 - Command Allowlist (Priority: P2)

En tant qu'utilisateur d'Aetheris, je veux pouvoir définir une liste de commandes autorisées pour les agents afin de contrôler précisément ce qu'ils peuvent exécuter.

**Why this priority**: Contrôle granulaire - permet d'adapter les restrictions aux besoins spécifiques du projet.

**Independent Test**: Configurer une allowlist personnalisée et vérifier que seules ces commandes peuvent être exécutées par les agents.

**Acceptance Scenarios**:

1. **Given** une allowlist par défaut existe, **When** un agent tente une commande autorisée, **Then** la commande s'exécute normalement
2. **Given** une allowlist est configurée, **When** un agent tente une commande non autorisée, **Then** la commande est bloquée avec un message explicatif
3. **Given** l'utilisateur veut personnaliser l'allowlist, **When** il modifie `config.json`, **Then** les nouvelles règles sont appliquées immédiatement
4. **Given** le profil `unrestricted` est actif, **When** un agent tente une commande, **Then** l'allowlist est ignorée

---

### User Story 5 - No Force Push Guarantee (Priority: P3)

En tant qu'utilisateur d'Aetheris, je veux avoir la garantie qu'aucune opération ne fera de force-push sur mes branches protégées pour éviter toute perte de données.

**Why this priority**: Garantie de sécurité - protection contre les erreurs catastrophiques.

**Independent Test**: Tenter de configurer ou exécuter une opération de force-push et vérifier qu'elle est systématiquement bloquée.

**Acceptance Scenarios**:

1. **Given** une opération Git est exécutée, **When** elle implique `--force` ou `-f`, **Then** l'opération est bloquée avec un avertissement
2. **Given** la branche `main` ou `master` est la cible, **When** une opération de push est tentée, **Then** une vérification supplémentaire empêche le force-push
3. **Given** l'utilisateur veut explicitement force-push, **When** il utilise le profil `unrestricted`, **Then** un avertissement clair est affiché mais l'opération reste bloquée par défaut

---

### Edge Cases

| Edge Case | Solution |
|-----------|----------|
| Profil invalide spécifié | Afficher erreur avec liste des profils valides (safe, ci, unrestricted) |
| Changements non commités avant fix | Bloquer et demander stash/commit avec message explicatif |
| Branche fix existe déjà | Générer un suffixe unique (fix/issue-xxx-1, fix/issue-xxx-2) |
| Conflit lors du merge de fix | Garder la branche, notifier l'utilisateur, ne pas auto-résoudre |
| Fichier d'audit corrompu | Créer un nouveau fichier, archiver l'ancien avec avertissement |
| Commande dans allowlist mais dangereuse | Ajouter validation secondaire pour commandes critiques (rm -rf, etc.) |
| Opération Git échoue mid-fix | Rollback complet, supprimer branche temporaire, restaurer état |
| Disk full pendant audit logging | Continuer l'opération, warning dans console, retry logging après |

## Requirements

### Functional Requirements

#### Security Profiles

- **FR-001**: Le système DOIT supporter trois profils de sécurité: `safe` (défaut), `ci`, et `unrestricted`
- **FR-002**: Le profil `safe` DOIT bloquer toutes les commandes réseau sortantes
- **FR-003**: Le profil `safe` DOIT limiter les diffs à 50 lignes sans confirmation
- **FR-004**: Le profil `safe` DOIT utiliser une allowlist de commandes autorisées
- **FR-005**: Le profil `ci` DOIT être non-interactif (aucune confirmation demandée)
- **FR-006**: Le profil `ci` DOIT logger toutes les opérations dans l'audit
- **FR-007**: Le profil `unrestricted` DOIT autoriser toutes les opérations sans restriction
- **FR-008**: Le système DOIT permettre de spécifier le profil via `--profile` CLI flag
- **FR-009**: Le système DOIT permettre de configurer le profil par défaut dans `config.json`

#### Git Strategy

- **FR-010**: Le système DOIT créer une branche temporaire pour chaque fix automatique
- **FR-011**: Le format de branche DOIT être `fix/{issue-id}` ou `fix/{description}`
- **FR-012**: Le système DOIT vérifier l'absence de changements non commités avant de créer une branche
- **FR-013**: Le système DOIT supprimer la branche temporaire en cas d'échec du fix
- **FR-014**: Le système DOIT proposer de merger ou garder la branche en cas de succès
- **FR-015**: Le système DOIT garantir qu'aucun force-push n'est effectué
- **FR-016**: Le système DOIT empêcher les opérations sur `main`/`master` sans confirmation explicite

#### Audit & Transparency

- **FR-017**: Le système DOIT logger toutes les opérations sensibles dans un fichier d'audit
- **FR-018**: Chaque entrée d'audit DOIT contenir: timestamp, action, paramètres, résultat, durée
- **FR-019**: Le fichier d'audit DOIT être au format JSONL (une ligne JSON par entrée)
- **FR-020**: Le système DOIT fournir une commande `aetheris audit` pour consulter l'historique
- **FR-021**: Le système DOIT supporter la rotation/archivage des logs d'audit

#### Command Allowlist

- **FR-022**: Le système DOIT fournir une allowlist par défaut de commandes sécurisées
- **FR-023**: L'allowlist DOIT être configurable dans `config.json`
- **FR-024**: L'allowlist DOIT supporter les patterns glob pour les commandes
- **FR-025**: Le système DOIT afficher un message explicatif quand une commande est bloquée

### Non-Functional Requirements

- **NFR-001**: La vérification de profil DOIT s'exécuter en <10ms
- **NFR-002**: L'écriture d'audit DOIT être asynchrone pour ne pas bloquer les opérations
- **NFR-003**: Le fichier d'audit DOIT supporter au moins 100,000 entrées avant rotation

### Key Entities

- **SecurityProfile**: Représente un profil de sécurité avec ses restrictions (network_blocked, max_diff_lines, allowlist_enabled, interactive)
- **AuditEntry**: Une entrée d'audit avec timestamp, action, params, result, duration_ms
- **CommandAllowlist**: Liste de patterns de commandes autorisées avec descriptions
- **GitBranch**: Représente une branche temporaire de fix avec status, created_at, parent_branch
- **OperationResult**: Résultat d'une opération avec success, error, rollback_performed

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% des commandes réseau sont bloquées en profil `safe`
- **SC-002**: 100% des opérations sensibles sont loggées dans l'audit
- **SC-003**: 0% de force-push effectués, même en mode `unrestricted`
- **SC-004**: <1s pour créer et basculer sur une branche de fix
- **SC-005**: 100% des branches de fix échouées sont nettoyées automatiquement
- **SC-006**: Le fichier d'audit peut être parsé par des outils standard (jq, etc.)

## Assumptions

- Le système de fichiers local est accessible en lecture/écriture
- Git est installé et configuré sur le système
- L'utilisateur a les permissions Git nécessaires pour créer/supprimer des branches
- Le fichier `config.json` de v3.0 est disponible pour la configuration des profils
