# Feature Specification: Flexible Timeout Management

**Feature Branch**: `002-flexible-timeout`
**Created**: 2025-01-07
**Status**: Draft
**Target Version**: v2.6.1

## Overview

Le timeout par défaut actuel est trop court pour la résolution de bugs complexes. Certains processus de débogage ou d'analyse profonde peuvent nécessiter plus d'une heure. Une interruption brutale (timeout) entraîne l'échec de la tâche et la perte du contexte de résolution.

Cette fonctionnalité implémente une gestion flexible du temps d'exécution pour s'adapter à la complexité des tâches.

## User Scenarios & Testing

### User Story 1 - Default Timeout Extension (Priority: P1)

En tant qu'utilisateur exécutant des analyses complexes, je veux que le timeout par défaut soit suffisamment long pour que mes analyses puissent se terminer sans interruption.

**Why this priority**: Le timeout actuel cause des échecs de tâches complexes, résultant en perte de temps et frustration utilisateur.

**Independent Test**: Lancer une analyse complexe et vérifier qu'elle peut s'exécuter pendant au moins 60 minutes sans timeout.

**Acceptance Scenarios**:

1. **Given** l'utilisateur lance une analyse sans paramètre de timeout, **When** l'analyse dure 45 minutes, **Then** l'analyse se termine normalement sans timeout
2. **Given** l'utilisateur lance une analyse sans paramètre de timeout, **When** l'analyse dure 65 minutes, **Then** l'analyse est interrompue par timeout après 60 minutes

---

### User Story 2 - Custom Timeout Configuration (Priority: P1)

En tant qu'utilisateur, je veux pouvoir définir un timeout personnalisé via la ligne de commande pour adapter le temps d'exécution à mes besoins spécifiques.

**Why this priority**: Essentiel pour les utilisateurs ayant des besoins variés (analyses rapides vs analyses profondes).

**Independent Test**: Exécuter une commande avec `--timeout 120m` et vérifier que le timeout appliqué est de 120 minutes.

**Acceptance Scenarios**:

1. **Given** l'utilisateur lance `aetheris analysis --timeout 30m`, **When** l'analyse dure 25 minutes, **Then** l'analyse se termine normalement
2. **Given** l'utilisateur lance `aetheris analysis --timeout 30m`, **When** l'analyse dure 35 minutes, **Then** l'analyse est interrompue après 30 minutes
3. **Given** l'utilisateur lance `aetheris analysis --timeout 0`, **When** l'analyse dure plusieurs heures, **Then** l'analyse continue sans limite de temps
4. **Given** l'utilisateur lance `aetheris analysis -t 3600`, **When** le timeout est appliqué, **Then** le timeout est de 3600 secondes (1 heure)

---

### User Story 3 - Progress Heartbeat (Priority: P2)

En tant qu'utilisateur exécutant une analyse longue, je veux voir un indicateur de progression régulier pour savoir que le processus n'est pas gelé.

**Why this priority**: Améliore l'expérience utilisateur en fournissant un feedback visuel, mais non bloquant pour la fonctionnalité de base.

**Independent Test**: Lancer une analyse longue et vérifier qu'un indicateur de progression s'affiche toutes les 10 minutes après les premières 10 minutes.

**Acceptance Scenarios**:

1. **Given** l'utilisateur lance une analyse, **When** 10 minutes se sont écoulées, **Then** un message "heartbeat" s'affiche dans la console
2. **Given** l'utilisateur lance une analyse, **When** 20 minutes se sont écoulées, **Then** un deuxième message "heartbeat" s'affiche
3. **Given** l'utilisateur lance une analyse, **When** l'analyse se termine en moins de 10 minutes, **Then** aucun message "heartbeat" n'est affiché

---

### Edge Cases

- Que se passe-t-il si l'utilisateur entre une valeur de timeout négative?
- Que se passe-t-il si l'utilisateur entre une valeur de timeout invalide (ex: "abc")?
- Que se passe-t-il si le processus consomme trop de mémoire avant le timeout?
- Comment gérer l'interruption gracieuse (Ctrl+C) pendant une longue analyse?

## Requirements

### Functional Requirements

- **FR-001**: Le système DOIT avoir un timeout par défaut de 60 minutes pour toutes les commandes d'analyse
- **FR-002**: Le système DOIT accepter un paramètre CLI `--timeout` (ou `-t`) pour définir un timeout personnalisé
- **FR-003**: Le système DOIT supporter les formats de timeout suivants: secondes (entier), minutes (suffixe "m"), heures (suffixe "h")
- **FR-004**: Le système DOIT permettre de désactiver le timeout avec la valeur `0` ou `no-limit`
- **FR-005**: Le système DOIT afficher un message "heartbeat" toutes les 10 minutes après les premières 10 minutes d'exécution
- **FR-006**: Le système DOIT valider les valeurs de timeout et afficher un message d'erreur clair pour les valeurs invalides
- **FR-007**: Le système DOIT interrompre gracieusement le processus lors d'un timeout, en sauvegardant le contexte si possible

### Key Entities

- **TimeoutConfig**: Configuration du timeout (valeur, unité, activé/désactivé)
- **HeartbeatMonitor**: Gestionnaire de l'indicateur de progression périodique

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% des analyses de plus de 30 minutes peuvent se terminer sans timeout par défaut
- **SC-002**: Les utilisateurs peuvent configurer un timeout personnalisé via CLI dans 100% des cas
- **SC-003**: Le message heartbeat s'affiche dans les 10 secondes suivant chaque intervalle de 10 minutes
- **SC-004**: 0% des analyses échouent à cause d'un timeout trop court par défaut (vs situation actuelle)
- **SC-005**: Les utilisateurs comprennent le statut du processus grâce au feedback visuel (réduction des questions "est-ce que ça tourne encore?")

## Assumptions

- Le timeout par défaut actuel est significativement inférieur à 60 minutes
- Les utilisateurs ont des analyses qui peuvent durer de quelques secondes à plusieurs heures
- L'interface CLI supporte déjà les arguments avec des valeurs
- Le système dispose de mécanismes pour afficher des messages dans la console pendant l'exécution

## Out of Scope

- Configuration du timeout via fichier de configuration → **Voir 006-persistent-config** (`ai.timeout`, `ai.heartbeat_interval`)
- Interface graphique pour le monitoring
- Notifications push ou email lors de la fin d'une analyse
- Parallélisation des analyses pour réduire le temps d'exécution

## Config Integration (v3.0+)

À partir de v3.0, les options de timeout seront également configurables via `config.json`:

```json
{
  "ai": {
    "timeout": "60m",
    "heartbeat_interval": "10m"
  }
}
```

La hiérarchie reste: CLI (`--timeout`) > config.json local > config.json global > défaut (60m)
