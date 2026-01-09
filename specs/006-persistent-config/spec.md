# Feature Specification: Persistent Configuration & Local Config File

**Feature Branch**: `006-persistent-config`
**Created**: 2025-01-07
**Status**: Draft
**Target Version**: v3.0

## Overview

Migrer la configuration de l'outil depuis les variables d'environnement (`.env`) vers un fichier de configuration dédié et structuré (`config.json`). Cette migration permet une meilleure gestion des paramètres complexes, le versionnage des règles de projet et une séparation nette entre secrets et préférences.

## Config.json Schema (Reference)

Ce schema intègre toutes les options des specs pré-v3.0 (002-timeout, 003-stats, 005-cicd) et les profils de sécurité:

```json
{
  "ai": {
    "provider": "gemini",
    "model": "default",
    "timeout": "60m",
    "heartbeat_interval": "10m",
    "max_retries": 3
  },
  "analysis": {
    "exclude_patterns": ["**/node_modules/**", "**/.git/**", "**/__pycache__/**"],
    "changed_files_only": false,
    "default_preset": "full-scan"
  },
  "security": {
    "profile": "safe",
    "custom_allowlist": [],
    "audit_log_enabled": false,
    "audit_log_path": "aetheris-audit.jsonl"
  },
  "stats": {
    "hourly_rate": null,
    "region": "auto",
    "currency": "auto",
    "heuristics": {
      "bug_simple_minutes": 37.5,
      "bug_moderate_minutes": 90,
      "bug_complex_minutes": 240
    }
  },
  "output": {
    "format": "markdown",
    "directory": "docs/analyses"
  }
}
```

### Security Profiles

| Profile | Description | Use Case |
|---------|-------------|----------|
| `safe` | Mode restreint, opérations lecture seule | Développement local, première utilisation |
| `ci` | Mode CI/CD, écritures autorisées dans dossiers spécifiques | Pipelines automatisés |
| `unrestricted` | Accès complet, toutes opérations autorisées | Utilisateurs avancés, environnements contrôlés |

### Options détaillées

| Section | Clé | Type | Défaut | Description | Source |
|---------|-----|------|--------|-------------|--------|
| `ai` | `provider` | enum | `"gemini"` | Provider AI (gemini, openai, claude) | - |
| `ai` | `model` | string | `"default"` | Modèle spécifique ou "default" | - |
| `ai` | `timeout` | string | `"60m"` | Timeout par défaut (formats: 120, 30m, 1h, no-limit) | 002 |
| `ai` | `heartbeat_interval` | string | `"10m"` | Intervalle des messages heartbeat | 002 |
| `ai` | `max_retries` | int | `3` | Nombre de retries API | - |
| `analysis` | `exclude_patterns` | string[] | `[...]` | Patterns glob à exclure | 005 |
| `analysis` | `changed_files_only` | bool | `false` | Analyser uniquement fichiers modifiés | 005 |
| `analysis` | `default_preset` | string | `"full-scan"` | Preset par défaut | - |
| `security` | `profile` | enum | `"safe"` | Profil de sécurité (safe, ci, unrestricted) | - |
| `security` | `custom_allowlist` | string[] | `[]` | Commandes additionnelles autorisées | - |
| `security` | `audit_log_enabled` | bool | `false` | Activer le logging des opérations | - |
| `security` | `audit_log_path` | string | `"aetheris-audit.jsonl"` | Chemin du fichier d'audit | - |
| `stats` | `hourly_rate` | float\|null | `null` | Taux horaire custom (null = régional) | 003 |
| `stats` | `region` | enum | `"auto"` | Région pour taux (auto, EUR, CAD, USD) | 003 |
| `stats` | `currency` | enum | `"auto"` | Devise affichage (auto, EUR, CAD, USD) | 003 |
| `stats.heuristics` | `bug_simple_minutes` | float | `37.5` | Temps moyen bug simple | 003 |
| `stats.heuristics` | `bug_moderate_minutes` | float | `90` | Temps moyen bug modéré | 003 |
| `stats.heuristics` | `bug_complex_minutes` | float | `240` | Temps moyen bug complexe | 003 |
| `output` | `format` | enum | `"markdown"` | Format de sortie (markdown, json) | - |
| `output` | `directory` | string | `"docs/analyses"` | Dossier de sortie | - |

## User Scenarios & Testing

### User Story 1 - Configuration Cascade (Priority: P1)

En tant qu'utilisateur, je veux que la configuration suive une hiérarchie claire pour savoir quelle valeur sera utilisée.

**Why this priority**: Fondement du système de configuration - détermine comment toutes les options sont résolues.

**Independent Test**: Définir une même option à plusieurs niveaux et vérifier que la priorité est respectée.

**Acceptance Scenarios**:

1. **Given** un argument CLI `--timeout 30m`, **When** le même paramètre est dans config.json avec une valeur différente, **Then** la valeur CLI est utilisée
2. **Given** une valeur dans config.json local, **When** la même valeur est dans config.json global, **Then** la valeur locale est utilisée
3. **Given** aucune configuration explicite, **When** le système démarre, **Then** les valeurs par défaut du config.json global sont utilisées
4. **Given** une clé API dans `.env`, **When** le système démarre, **Then** la clé est chargée depuis `.env` (secrets uniquement)

---

### User Story 2 - Initialize Config File (Priority: P1)

En tant qu'utilisateur, je veux pouvoir initialiser un fichier de configuration avec les valeurs par défaut pour personnaliser mon projet.

**Why this priority**: Nécessaire pour démarrer avec le nouveau système de configuration.

**Independent Test**: Exécuter `aetheris init` et vérifier qu'un config.json est créé à la racine.

**Acceptance Scenarios**:

1. **Given** aucun config.json dans le projet, **When** l'utilisateur exécute `aetheris init`, **Then** un config.json est créé avec les valeurs par défaut
2. **Given** un config.json existant, **When** l'utilisateur exécute `aetheris init`, **Then** un message demande confirmation avant d'écraser
3. **Given** `aetheris init --force`, **When** un config.json existe, **Then** le fichier est écrasé sans confirmation

---

### User Story 3 - Complex Configuration Types (Priority: P2)

En tant qu'utilisateur, je veux pouvoir configurer des options complexes (listes, objets imbriqués) que les variables d'environnement ne supportent pas bien.

**Why this priority**: Débloque des cas d'usage avancés impossibles avec .env.

**Independent Test**: Configurer une liste d'exclusions et un objet de paramètres par module.

**Acceptance Scenarios**:

1. **Given** une liste d'exclusions dans config.json, **When** l'analyse s'exécute, **Then** tous les patterns de la liste sont exclus
2. **Given** des paramètres par module (agents, services), **When** un module s'exécute, **Then** ses paramètres spécifiques sont appliqués
3. **Given** un tableau vide `[]`, **When** le système lit la config, **Then** aucune exclusion n'est appliquée

---

### User Story 4 - Secrets Separation (Priority: P2)

En tant qu'utilisateur, je veux que les secrets (clés API) restent dans .env pour ne pas les commiter accidentellement.

**Why this priority**: Sécurité - évite les fuites de credentials.

**Independent Test**: Vérifier que les clés API sont lues depuis .env et non config.json.

**Acceptance Scenarios**:

1. **Given** une clé API dans .env, **When** le système démarre, **Then** la clé est utilisée pour l'authentification
2. **Given** une clé API dans config.json (par erreur), **When** le système démarre, **Then** un avertissement recommande de déplacer vers .env
3. **Given** le fichier config.json commité, **When** un revieweur l'examine, **Then** aucun secret n'est visible

---

### User Story 5 - Interactive Settings Command (Priority: P2)

En tant qu'utilisateur, je veux pouvoir modifier la configuration via une commande interactive `aetheris settings` avec des onglets/catégories, similaire à l'expérience Claude Code.

**Why this priority**: Améliore considérablement l'expérience utilisateur - évite l'édition manuelle du JSON.

**Independent Test**: Exécuter `aetheris settings` et modifier une option via l'interface interactive.

**Acceptance Scenarios**:

1. **Given** la commande `aetheris settings`, **When** l'utilisateur l'exécute, **Then** une interface interactive s'affiche avec des onglets de catégories
2. **Given** l'interface settings ouverte, **When** l'utilisateur navigue avec les flèches, **Then** il peut basculer entre les onglets (AI, Analysis, I18n, Stats, Output)
3. **Given** une option sélectionnée, **When** l'utilisateur appuie sur Entrée, **Then** il peut modifier la valeur
4. **Given** une modification effectuée, **When** l'utilisateur sauvegarde, **Then** le config.json est mis à jour
5. **Given** l'option `--global`, **When** l'utilisateur exécute `aetheris settings --global`, **Then** le config.json global est modifié
6. **Given** une valeur invalide, **When** l'utilisateur tente de sauvegarder, **Then** un message d'erreur explicite s'affiche

---

### User Story 6 - Version Control Friendly (Priority: P3)

En tant que mainteneur de projet, je veux que le config.json soit versionnable pour partager les règles avec l'équipe.

**Why this priority**: Améliore la collaboration, mais non bloquant pour l'utilisation individuelle.

**Independent Test**: Commiter config.json et vérifier que les collègues ont les mêmes paramètres.

**Acceptance Scenarios**:

1. **Given** un config.json commité, **When** un collègue clone le repo, **Then** les paramètres du projet sont appliqués automatiquement
2. **Given** des modifications locales non commitées, **When** l'utilisateur lance une analyse, **Then** ses modifications locales sont utilisées
3. **Given** un merge conflict sur config.json, **When** le conflit est résolu, **Then** le format JSON reste valide

---

### Edge Cases

- Que se passe-t-il si le config.json est mal formaté (JSON invalide)?
- Comment gérer les clés de configuration inconnues (typos)?
- Que se passe-t-il si le config.json global est corrompu?
- Comment migrer les configurations .env existantes vers config.json?
- Que se passe-t-il si le terminal ne supporte pas l'interface interactive (pipe, CI)?
- Comment gérer les permissions d'écriture sur le config.json global?
- Que se passe-t-il si `timeout` a un format invalide (ex: "abc", "-10m")?
- Que se passe-t-il si `language` est une langue non supportée?
- Que se passe-t-il si `hourly_rate` est négatif?
- Que se passe-t-il si `region` est "auto" mais la locale système n'est pas reconnue?
- Comment valider les patterns glob dans `exclude_patterns`?
- Que se passe-t-il si `heuristics` contient des valeurs négatives?

## Requirements

### Functional Requirements

- **FR-001**: Le système DOIT supporter un fichier `config.json` pour la configuration
- **FR-002**: Le système DOIT respecter la hiérarchie: CLI > Local config > Global config > Env vars > Defaults
- **FR-003**: Le système DOIT fournir une commande `aetheris init` pour générer config.json
- **FR-004**: Le système DOIT supporter les types complexes (tableaux, objets imbriqués)
- **FR-005**: Le système DOIT lire les secrets (clés API) uniquement depuis `.env`
- **FR-006**: Le système DOIT avertir si des secrets sont détectés dans config.json
- **FR-007**: Le système DOIT valider le format JSON au chargement
- **FR-008**: Le système DOIT afficher un message d'erreur clair pour les JSON malformés
- **FR-009**: Le système DOIT ignorer les clés de configuration inconnues avec un avertissement
- **FR-010**: Le système DOIT stocker les valeurs par défaut dans un config.json global du package
- **FR-011**: Le système NE DOIT PAS avoir de valeurs par défaut hardcodées dans le code
- **FR-012**: Le système DOIT supporter `--force` pour écraser le config.json existant
- **FR-013**: Le système DOIT fournir une commande `aetheris settings` pour modifier la configuration interactivement
- **FR-014**: Le système DOIT organiser les options par catégories/onglets dans l'interface settings
- **FR-015**: Le système DOIT supporter la navigation clavier (flèches, Tab, Entrée, Échap)
- **FR-016**: Le système DOIT afficher la valeur actuelle et la source (local/global/default) pour chaque option
- **FR-017**: Le système DOIT supporter `--global` pour modifier le config.json global
- **FR-018**: Le système DOIT valider les valeurs en temps réel avant sauvegarde
- **FR-019**: Le système DOIT afficher une description/aide pour chaque option

#### Timeout (from 002-flexible-timeout)

- **FR-020**: Le système DOIT supporter `ai.timeout` avec formats: secondes (entier), minutes (suffixe "m"), heures (suffixe "h")
- **FR-021**: Le système DOIT supporter `ai.timeout: "no-limit"` ou `0` pour désactiver le timeout
- **FR-022**: Le système DOIT supporter `ai.heartbeat_interval` pour configurer l'intervalle des messages heartbeat

#### Security Profiles

- **FR-023**: Le système DOIT supporter `security.profile` avec valeurs "safe", "ci", "unrestricted" (défaut: "safe")
- **FR-024**: Le système DOIT supporter `security.custom_allowlist` pour étendre les commandes autorisées
- **FR-025**: Le système DOIT supporter `security.audit_log_enabled` pour activer le logging des opérations
- **FR-026**: Le système DOIT écrire les opérations en format JSONL si `audit_log_enabled: true`
- **FR-027**: Le profil `safe` DOIT restreindre les opérations à la lecture seule
- **FR-028**: Le profil `ci` DOIT autoriser les écritures dans les dossiers de sortie configurés
- **FR-029**: Le profil `unrestricted` DOIT autoriser toutes les opérations

#### Stats ROI (from 003-advanced-stats)

- **FR-030**: Le système DOIT supporter `stats.hourly_rate` pour surcharger le taux horaire régional
- **FR-031**: Le système DOIT supporter `stats.region` avec valeurs "auto", "EUR", "CAD", "USD"
- **FR-032**: Le système DOIT détecter automatiquement la région via locale système si `stats.region: "auto"`
- **FR-033**: Le système DOIT supporter `stats.heuristics` pour personnaliser les temps de bug estimation
- **FR-034**: Le système DOIT utiliser les taux régionaux par défaut: 85€/h (EUR), 120$CAD/h (CAD), 95$USD/h (USD)

#### Analysis (from 005-cicd-template)

- **FR-035**: Le système DOIT supporter `analysis.exclude_patterns` comme tableau de patterns glob
- **FR-036**: Le système DOIT supporter `analysis.changed_files_only` pour le mode analyse incrémentale

### Key Entities

- **ConfigFile**: Fichier JSON de configuration (local ou global)
- **ConfigHierarchy**: Ordre de priorité des sources de configuration
- **ConfigSchema**: Structure et types des options de configuration (ai, analysis, security, stats, output)
- **SecretKeys**: Liste des clés considérées comme secrets (API keys, tokens)
- **SettingsUI**: Interface terminal interactive avec onglets (Rich/Textual)
- **TimeoutParser**: Parser pour formats timeout (120, 30m, 1h, no-limit)
- **RegionDetector**: Détection automatique région via locale système
- **HeuristicsConfig**: Configuration des temps estimés par type de bug
- **SecurityProfile**: Profil de sécurité (safe, ci, unrestricted)
- **AuditLogger**: Logger JSONL pour traçabilité des opérations

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% des options configurables sont accessibles via config.json
- **SC-002**: Le temps de chargement de la configuration n'excède pas 100ms
- **SC-003**: 0% des secrets sont stockés dans config.json (validation automatique)
- **SC-004**: 95% des utilisateurs peuvent personnaliser leur configuration sans documentation extensive
- **SC-005**: Les configurations de projet peuvent être partagées via git (100% compatibles)
- **SC-006**: L'interface `aetheris settings` permet de modifier n'importe quelle option en moins de 30 secondes
- **SC-007**: La navigation par onglets couvre 100% des options de configuration

## Assumptions

- Le format JSON est suffisant pour tous les besoins de configuration
- Les utilisateurs sont familiers avec l'édition de fichiers JSON
- Le config.json global est stocké dans le répertoire d'installation du package (`~/.aetheris/config.json`)
- Les secrets sont limités aux clés API des providers (GEMINI, OPENAI, ANTHROPIC)
- La détection de région via locale système couvre les cas courants (fr_FR → EUR, en_CA → CAD, en_US → USD)
- Les formats de timeout suivent la convention standard: entier (secondes), suffixe "m" (minutes), suffixe "h" (heures)
- Les patterns glob dans `exclude_patterns` suivent la syntaxe standard (**, *, ?)

## Out of Scope

- Interface graphique externe (GUI desktop/web) - l'interface terminal interactive est IN scope
- Configuration via serveur distant
- Chiffrement du fichier de configuration
- Support d'autres formats (YAML, TOML)
- Migration automatique des anciennes configurations
- Validation de schéma JSON avancée
- Logique métier du timeout (implémentée dans 002-flexible-timeout)
- Logique métier des stats ROI (implémentée dans 003-advanced-stats)
- Logique métier de l'analyse incrémentale (implémentée dans 005-cicd-template)

## Cross-Spec Dependencies

Cette spec définit le **système de stockage** des configurations. La logique métier est implémentée dans les specs sources:

| Option config.json | Logique implémentée dans |
|--------------------|--------------------------|
| `ai.timeout`, `ai.heartbeat_interval` | 002-flexible-timeout |
| `stats.*` | 003-advanced-stats |
| `analysis.exclude_patterns`, `analysis.changed_files_only` | 005-cicd-template |
| `security.*` | Cette spec (v3.0) |
