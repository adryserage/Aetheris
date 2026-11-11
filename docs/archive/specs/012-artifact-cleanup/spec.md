# Feature Specification: Nettoyage des Artefacts & Sécurisation des Paquets

**Feature Branch**: `012-artifact-cleanup`
**Created**: 2026-01-07
**Status**: Draft
**Target Version**: v2.6.2

## Overview

Réduire la taille des paquets distribués et prévenir la fuite accidentelle de secrets ou de fichiers de configuration de développement. Cette feature s'intègre au processus de build/publication pour garantir des paquets propres et sécurisés.

## User Scenarios & Testing

### User Story 1 - Automatic File Exclusion (Priority: P1)

En tant que mainteneur de package, je veux que les fichiers de développement soient automatiquement exclus du paquet distribué pour éviter les fuites accidentelles.

**Why this priority**: Sécurité de base - les fichiers sensibles ne doivent jamais être inclus dans les distributions.

**Independent Test**: Exécuter `aetheris build` ou `python setup.py sdist` et vérifier que les fichiers `.env`, `.git/`, etc. ne sont pas dans l'archive.

**Acceptance Scenarios**:

1. **Given** un projet avec un fichier `.env`, **When** le package est construit, **Then** le fichier `.env` n'est PAS inclus dans l'archive
2. **Given** un projet avec un dossier `.git/`, **When** le package est construit, **Then** le dossier `.git/` n'est PAS inclus
3. **Given** un projet avec des fichiers `.DS_Store`, **When** le package est construit, **Then** les fichiers `.DS_Store` ne sont PAS inclus
4. **Given** un projet avec `tsconfig.tsbuildinfo`, **When** le package est construit, **Then** ce fichier n'est PAS inclus
5. **Given** un projet avec un dossier `tests/` ou `__tests__/`, **When** le package est construit, **Then** ces dossiers ne sont PAS inclus

---

### User Story 2 - Build-Time Cleanup Process (Priority: P1)

En tant que mainteneur, je veux un processus de nettoyage intégré au build pour automatiser la suppression des artefacts inutiles.

**Why this priority**: Automatisation critique pour garantir la cohérence et éviter les oublis humains.

**Independent Test**: Exécuter `aetheris cleanup` ou le hook de pre-build et vérifier que les fichiers temporaires sont supprimés.

**Acceptance Scenarios**:

1. **Given** un projet avec des fichiers `*.pyc` et `__pycache__/`, **When** `aetheris cleanup` s'exécute, **Then** ces fichiers sont supprimés
2. **Given** un projet avec des fichiers de build (`dist/`, `build/`, `*.egg-info/`), **When** `aetheris cleanup --deep` s'exécute, **Then** ces dossiers sont supprimés
3. **Given** une configuration de cleanup personnalisée, **When** le cleanup s'exécute, **Then** les patterns personnalisés sont appliqués
4. **Given** le flag `--dry-run`, **When** le cleanup s'exécute, **Then** les fichiers à supprimer sont listés mais NON supprimés

---

### User Story 3 - Security Scan Before Package (Priority: P1)

En tant que mainteneur, je veux un scan de sécurité préventif pour m'assurer qu'aucun secret n'est inclus dans le package avant publication.

**Why this priority**: Sécurité critique - prévenir les fuites de credentials avant qu'elles ne se produisent.

**Independent Test**: Créer un fichier avec `API_KEY=secret123` et vérifier que le scan le détecte et bloque la publication.

**Acceptance Scenarios**:

1. **Given** un fichier contenant une chaîne `API_KEY=...`, **When** le scan s'exécute, **Then** le secret est détecté et signalé
2. **Given** un fichier contenant un pattern de clé AWS `AKIA...`, **When** le scan s'exécute, **Then** la clé est détectée
3. **Given** un fichier contenant un token JWT, **When** le scan s'exécute, **Then** le token est détecté
4. **Given** des secrets détectés, **When** le build est lancé, **Then** le build échoue avec un message explicite
5. **Given** aucun secret détecté, **When** le build est lancé, **Then** le build continue normalement
6. **Given** un faux positif connu, **When** le fichier est dans `.secretsignore`, **Then** il n'est pas signalé

---

### User Story 4 - Optional Minification (Priority: P3)

En tant que mainteneur, je veux optionnellement minifier les fichiers de code pour réduire la taille du package.

**Why this priority**: Optimisation optionnelle - utile mais non critique pour la fonctionnalité de base.

**Independent Test**: Activer la minification et vérifier que les commentaires sont supprimés et la taille réduite.

**Acceptance Scenarios**:

1. **Given** l'option `--minify` activée, **When** le build s'exécute, **Then** les commentaires Python sont supprimés
2. **Given** l'option `--minify` activée, **When** le build s'exécute, **Then** les docstrings non-publics sont optionnellement supprimées
3. **Given** aucune option de minification, **When** le build s'exécute, **Then** les fichiers restent intacts
4. **Given** un fichier déjà minifié, **When** la minification s'exécute, **Then** le fichier n'est pas re-traité

---

### User Story 5 - Pre-publish Validation Hook (Priority: P2)

En tant que mainteneur, je veux un hook de pre-publication qui valide automatiquement le package avant upload sur PyPI.

**Why this priority**: Filet de sécurité final avant publication - important mais peut être contourné si nécessaire.

**Independent Test**: Exécuter `aetheris validate-package` et vérifier que toutes les vérifications passent.

**Acceptance Scenarios**:

1. **Given** un package prêt à publier, **When** `aetheris validate-package` s'exécute, **Then** la taille, les exclusions et le scan de secrets sont vérifiés
2. **Given** un package avec des secrets, **When** la validation s'exécute, **Then** la publication est bloquée
3. **Given** un package valide, **When** la validation s'exécute, **Then** un rapport de validation est affiché
4. **Given** l'option `--fix`, **When** la validation échoue, **Then** les corrections automatiques sont proposées

---

### Edge Cases

- Que se passe-t-il si un fichier `.env.example` (template) doit être inclus?
- Comment gérer les secrets dans les fichiers de configuration de test (fixtures)?
- Que se passe-t-il si le cleanup supprime un fichier nécessaire au build?
- Comment gérer les faux positifs du scan de secrets (ex: hash SHA256)?
- Que se passe-t-il si la minification casse le code (imports dynamiques)?
- Comment gérer les symlinks lors du cleanup?
- Que se passe-t-il si l'utilisateur a des patterns d'exclusion personnalisés contradictoires?

## Requirements

### Functional Requirements

#### Exclusion automatique

- **FR-001**: Le système DOIT exclure automatiquement les fichiers `.env`, `.env.*` (sauf `.env.example`)
- **FR-002**: Le système DOIT exclure le dossier `.git/` et tous ses contenus
- **FR-003**: Le système DOIT exclure les fichiers `.DS_Store`, `Thumbs.db`, `desktop.ini`
- **FR-004**: Le système DOIT exclure les fichiers de build TypeScript (`tsconfig.tsbuildinfo`, `*.tsbuildinfo`)
- **FR-005**: Le système DOIT exclure les configurations de linting non requises en prod (`eslint.config.js`, `.eslintrc*`, `.prettierrc*`)
- **FR-006**: Le système DOIT exclure les dossiers de tests (`tests/`, `test/`, `__tests__/`, `*_test.py`, `test_*.py`)
- **FR-007**: Le système DOIT exclure les dossiers de mocks (`mocks/`, `__mocks__/`, `fixtures/`)
- **FR-008**: Le système DOIT exclure les fichiers Python compilés (`*.pyc`, `__pycache__/`, `*.pyo`)

#### Processus de nettoyage

- **FR-009**: Le système DOIT fournir une commande `aetheris cleanup` pour nettoyer les artefacts
- **FR-010**: Le système DOIT supporter `--dry-run` pour prévisualiser les suppressions sans exécuter
- **FR-011**: Le système DOIT supporter `--deep` pour inclure les dossiers de build (`dist/`, `build/`, `*.egg-info/`)
- **FR-012**: Le système DOIT supporter une liste de patterns personnalisés via config ou CLI
- **FR-013**: Le système DOIT afficher un résumé des fichiers/dossiers supprimés avec leur taille totale
- **FR-014**: Le système DOIT intégrer le cleanup comme hook de pre-build optionnel

#### Scan de sécurité

- **FR-015**: Le système DOIT scanner les fichiers pour détecter les patterns de secrets courants (API keys, tokens)
- **FR-016**: Le système DOIT détecter les clés AWS (`AKIA...`), GCP, Azure, et autres providers cloud
- **FR-017**: Le système DOIT détecter les tokens JWT, Bearer tokens, et auth headers
- **FR-018**: Le système DOIT détecter les patterns `PASSWORD=`, `SECRET=`, `API_KEY=`, `TOKEN=`
- **FR-019**: Le système DOIT supporter un fichier `.secretsignore` pour les faux positifs connus
- **FR-020**: Le système DOIT bloquer le build si des secrets sont détectés (sauf override explicite)
- **FR-021**: Le système DOIT afficher la ligne et le fichier où le secret a été détecté (masqué partiellement)

#### Minification (optionnel)

- **FR-022**: Le système DOIT supporter `--minify` pour supprimer les commentaires Python
- **FR-023**: Le système DOIT supporter `--strip-docstrings` pour supprimer les docstrings non-publics
- **FR-024**: Le système NE DOIT PAS minifier les fichiers déjà minifiés ou les binaires

#### Validation pre-publish

- **FR-025**: Le système DOIT fournir une commande `aetheris validate-package`
- **FR-026**: Le système DOIT vérifier la taille du package et alerter si > seuil configurable
- **FR-027**: Le système DOIT vérifier que les exclusions par défaut sont appliquées
- **FR-028**: Le système DOIT exécuter le scan de secrets comme partie de la validation
- **FR-029**: Le système DOIT supporter `--fix` pour corriger automatiquement les problèmes détectés

### Non-Functional Requirements

- **NFR-001**: Le scan de secrets doit s'exécuter en moins de 5 secondes pour un projet de 10k fichiers
- **NFR-002**: Les patterns de détection doivent avoir un taux de faux positifs < 5%
- **NFR-003**: Le cleanup doit être idempotent (peut être exécuté plusieurs fois sans effet)

### Key Entities

- **ExclusionList**: Liste des patterns de fichiers/dossiers à exclure (défauts + personnalisés)
- **CleanupConfig**: Configuration du processus de nettoyage (patterns, deep mode, dry-run)
- **SecretScanner**: Moteur de détection de secrets avec patterns regex
- **SecretPattern**: Pattern regex pour détecter un type de secret spécifique
- **SecretsIgnore**: Liste des faux positifs à ignorer (fichier `.secretsignore`)
- **ValidationReport**: Rapport de validation du package (taille, exclusions, secrets)
- **Minifier**: Processeur optionnel de minification Python

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% des fichiers de la liste d'exclusion par défaut sont exclus des packages
- **SC-002**: 0 secret détecté dans les packages publiés après scan
- **SC-003**: La taille des packages est réduite d'au moins 30% par rapport à un build sans cleanup
- **SC-004**: Le scan de secrets s'exécute en < 5s pour des projets standards
- **SC-005**: Moins de 5% de faux positifs sur les scans de secrets
- **SC-006**: La commande `aetheris validate-package` catch 100% des problèmes de sécurité connus

## Assumptions

- Le projet utilise une structure Python standard (setup.py, pyproject.toml, ou setup.cfg)
- Les patterns de secrets courants sont suffisants pour la majorité des cas
- L'utilisateur a les permissions nécessaires pour supprimer les fichiers lors du cleanup
- Le fichier `.secretsignore` suit un format similaire à `.gitignore`

## Out of Scope

- Chiffrement des secrets détectés (seulement détection et blocage)
- Intégration avec des gestionnaires de secrets externes (Vault, AWS Secrets Manager)
- Support de langages autres que Python pour la minification
- Scan des dépendances pour secrets (uniquement le code source)
- Rotation automatique des secrets détectés

## Config Integration (v3.0+)

À partir de v3.0, les options de cleanup seront configurables via `config.json`:

```json
{
  "cleanup": {
    "auto_run_on_build": false,
    "deep_clean": false,
    "extra_exclude_patterns": [],
    "minify": false,
    "strip_docstrings": false
  },
  "security": {
    "scan_for_secrets": true,
    "block_on_secrets": true,
    "max_package_size_mb": 50,
    "secrets_ignore_file": ".secretsignore"
  }
}
```

Voir **006-persistent-config** pour la hiérarchie de configuration.
