# Feature Specification: Architecture Headless Déterministe

**Feature Branch**: `017-headless-deterministic`
**Created**: 2026-01-09
**Status**: Draft
**Target Version**: v2.8
**Depends On**: None (standalone feature)

## Overview

Rendre Aetheris utilisable de manière programmatique et fiable, sans dépendre d'une interface humaine. Cette architecture est un pré-requis indispensable pour l'automatisation avancée (CI/CD, scripts) et les agents autonomes (v4.x). Le mode headless garantit des résultats déterministes et parseables par des machines.

## User Scenarios & Testing

### User Story 1 - Task File Input (Priority: P1)

En tant que développeur DevOps, je veux pouvoir soumettre des tâches à Aetheris via un fichier structuré (JSON/YAML) pour automatiser l'analyse et la correction dans mes pipelines CI/CD.

**Why this priority**: Fondation de l'automatisation - permet l'intégration dans n'importe quel système d'orchestration.

**Independent Test**: Créer un fichier `task.json` avec une demande d'analyse, l'exécuter avec `aetheris run task.json`, et vérifier que le résultat est un JSON structuré.

**Acceptance Scenarios**:

1. **Given** un fichier de tâche JSON valide, **When** l'utilisateur exécute `aetheris run task.json`, **Then** la tâche s'exécute et produit un résultat JSON
2. **Given** un fichier de tâche YAML valide, **When** l'utilisateur exécute `aetheris run task.yaml`, **Then** la tâche s'exécute de la même manière
3. **Given** un fichier de tâche invalide, **When** l'utilisateur l'exécute, **Then** un message d'erreur JSON est retourné avec le détail de l'erreur
4. **Given** un fichier de tâche avec des paramètres optionnels manquants, **When** l'utilisateur l'exécute, **Then** les valeurs par défaut sont utilisées

---

### User Story 2 - Structured JSON Output (Priority: P1)

En tant que système automatisé, je veux recevoir les résultats d'Aetheris dans un format JSON strict et documenté pour pouvoir les parser et les traiter programmatiquement.

**Why this priority**: Interopérabilité - permet l'intégration avec n'importe quel système capable de lire du JSON.

**Independent Test**: Exécuter une analyse et vérifier que la sortie est un JSON valide avec les champs documentés (status, diff, logs, exit_code).

**Acceptance Scenarios**:

1. **Given** une exécution réussie, **When** la tâche se termine, **Then** le résultat contient `{"status": "success", ...}`
2. **Given** une exécution échouée, **When** la tâche se termine, **Then** le résultat contient `{"status": "error", "error": {...}}`
3. **Given** une exécution avec diff généré, **When** la tâche se termine, **Then** le champ `diff` contient le diff en format unified
4. **Given** n'importe quelle exécution, **When** elle se termine, **Then** le champ `exit_code` reflète le statut de sortie

---

### User Story 3 - Non-Interactive Mode (Priority: P1)

En tant que pipeline CI/CD, je veux exécuter Aetheris sans aucune interaction utilisateur pour garantir une exécution automatique complète.

**Why this priority**: Automatisation complète - aucune intervention humaine ne doit être requise.

**Independent Test**: Exécuter une tâche qui normalement demanderait confirmation et vérifier qu'elle s'exécute ou échoue sans attendre d'input.

**Acceptance Scenarios**:

1. **Given** le mode headless est activé, **When** une opération nécessite normalement confirmation, **Then** la décision est prise selon la configuration ou le profil de sécurité
2. **Given** le mode headless est activé, **When** une erreur se produit, **Then** l'erreur est retournée dans le JSON sans demander d'action
3. **Given** le mode headless est activé avec profil `ci`, **When** une tâche s'exécute, **Then** toutes les opérations autorisées s'exécutent automatiquement
4. **Given** une opération bloquée par le profil de sécurité, **When** elle est tentée en mode headless, **Then** le JSON indique le blocage sans attendre

---

### User Story 4 - Stdout/Stderr Capture (Priority: P2)

En tant qu'opérateur, je veux capturer toutes les sorties (stdout, stderr, logs) de manière structurée pour faciliter le debugging et l'audit.

**Why this priority**: Observabilité - permet de comprendre ce qui s'est passé dans une exécution automatisée.

**Independent Test**: Exécuter une tâche et vérifier que les champs `stdout`, `stderr`, `logs` contiennent les outputs appropriés.

**Acceptance Scenarios**:

1. **Given** une exécution avec output console, **When** la tâche se termine, **Then** le champ `logs` contient tous les messages
2. **Given** une exécution avec erreurs, **When** la tâche se termine, **Then** le champ `stderr` contient les messages d'erreur
3. **Given** une exécution avec output verbose, **When** l'option verbose est activée, **Then** les logs détaillés sont inclus

---

### User Story 5 - Deterministic Execution (Priority: P2)

En tant que développeur, je veux que les mêmes inputs produisent toujours les mêmes outputs pour garantir la reproductibilité des résultats.

**Why this priority**: Fiabilité - permet de débugger et de reproduire des comportements.

**Independent Test**: Exécuter la même tâche deux fois et vérifier que les résultats sont identiques (hors timestamps).

**Acceptance Scenarios**:

1. **Given** une tâche avec les mêmes inputs, **When** exécutée deux fois, **Then** les résultats sont identiques (hors metadata temporelle)
2. **Given** une seed aléatoire configurée, **When** la tâche s'exécute, **Then** le comportement pseudo-aléatoire est reproductible
3. **Given** des dépendances externes (API), **When** elles sont mockées, **Then** les résultats sont déterministes

---

### Edge Cases

| Edge Case | Solution |
|-----------|----------|
| Fichier de tâche introuvable | Retourner JSON d'erreur avec `file_not_found` et exit_code 1 |
| Fichier de tâche mal formé | Retourner JSON d'erreur avec `parse_error` et détails de syntaxe |
| Timeout pendant l'exécution | Retourner JSON avec `status: timeout` et logs partiels |
| Interruption (SIGINT/SIGTERM) | Graceful shutdown, retourner JSON avec `status: interrupted` |
| Disk full pendant écriture | Retourner JSON minimal en mémoire, log sur stderr |
| Task file trop volumineux | Rejeter avec erreur si >1MB |
| Encoding non-UTF8 dans task file | Rejeter avec erreur de décodage |
| Circular dependency dans tasks | Détecter et rejeter avec erreur explicite |

## Requirements

### Functional Requirements

#### Task Input

- **FR-001**: Le système DOIT accepter des fichiers de tâche au format JSON
- **FR-002**: Le système DOIT accepter des fichiers de tâche au format YAML
- **FR-003**: Le système DOIT valider le schéma du fichier de tâche avant exécution
- **FR-004**: Le système DOIT fournir un schéma JSON documenté pour les fichiers de tâche
- **FR-005**: Le système DOIT supporter les chemins relatifs et absolus pour les fichiers de tâche

#### JSON Output

- **FR-006**: Le système DOIT produire une sortie JSON valide pour toute exécution
- **FR-007**: La sortie DOIT contenir les champs: status, exit_code, duration_ms
- **FR-008**: La sortie DOIT contenir le champ `logs` avec les messages d'exécution
- **FR-009**: La sortie DOIT contenir le champ `diff` si des modifications ont été générées
- **FR-010**: La sortie DOIT contenir le champ `error` en cas d'échec avec message et type
- **FR-011**: Le système DOIT supporter l'option `--output-file` pour écrire le JSON dans un fichier

#### Non-Interactive Mode

- **FR-012**: Le système DOIT fournir un flag `--headless` pour désactiver toute interaction
- **FR-013**: En mode headless, le système NE DOIT PAS attendre d'input utilisateur
- **FR-014**: En mode headless, les confirmations DOIVENT être résolues par le profil de sécurité
- **FR-015**: En mode headless, le système DOIT utiliser les valeurs par défaut pour les paramètres optionnels

#### Runner Command

- **FR-016**: Le système DOIT fournir une commande `aetheris run <task-file>`
- **FR-017**: La commande run DOIT être non-interactive par défaut
- **FR-018**: La commande run DOIT retourner un exit code approprié (0=success, 1=error, 2=warning)
- **FR-019**: La commande run DOIT supporter `--dry-run` pour valider sans exécuter

#### Determinism

- **FR-020**: Le système DOIT supporter une option `--seed` pour la reproductibilité
- **FR-021**: Les timestamps dans la sortie DOIVENT être optionnellement désactivables
- **FR-022**: Le système DOIT documenter les sources de non-déterminisme (API externes, etc.)

### Non-Functional Requirements

- **NFR-001**: La validation du fichier de tâche DOIT s'exécuter en <100ms
- **NFR-002**: La sortie JSON DOIT être générée même en cas de crash (graceful degradation)
- **NFR-003**: Le mode headless DOIT fonctionner sans TTY attaché

### Key Entities

- **TaskFile**: Fichier d'entrée avec task_type, parameters, options, target_files
- **ExecutionResult**: Résultat structuré avec status, exit_code, duration_ms, logs, diff, error
- **TaskRunner**: Orchestrateur d'exécution non-interactive
- **OutputFormatter**: Formatteur de sortie JSON/YAML

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% des exécutions produisent une sortie JSON valide
- **SC-002**: 0% d'interaction utilisateur requise en mode headless
- **SC-003**: Exit codes cohérents pour toutes les catégories d'erreur
- **SC-004**: <100ms pour valider et parser un fichier de tâche standard
- **SC-005**: 100% de reproductibilité pour les exécutions avec même seed
- **SC-006**: Documentation complète du schéma JSON pour inputs et outputs

## Task File Schema (Reference)

```json
{
  "version": "1.0",
  "task": {
    "type": "analysis|fix|pr",
    "target": {
      "files": ["src/**/*.py"],
      "changed_only": true
    },
    "options": {
      "timeout": 300,
      "profile": "ci",
      "agents": ["security", "quality"]
    }
  },
  "output": {
    "format": "json",
    "include_diff": true,
    "include_logs": true
  }
}
```

## Output Schema (Reference)

```json
{
  "status": "success|error|timeout|interrupted",
  "exit_code": 0,
  "duration_ms": 1234,
  "task": {
    "type": "analysis",
    "files_processed": 15
  },
  "results": {
    "issues_found": 3,
    "issues_fixed": 2
  },
  "diff": "--- a/file.py\n+++ b/file.py\n...",
  "logs": ["INFO: Starting analysis...", "..."],
  "error": null
}
```

## Assumptions

- Le système de fichiers est accessible pour lire les task files
- Python 3.9+ est disponible
- Les dépendances v3.0 (config) et v3.1 (security) sont implémentées
- Les API externes (AI providers) peuvent avoir des comportements non-déterministes
