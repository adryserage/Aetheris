# Feature Specification: Internationalization & Multilingual Support

**Feature Branch**: `004-i18n-multilingual`
**Created**: 2025-01-07
**Status**: Draft
**Target Version**: v2.8

## Overview

Permettre l'utilisation de l'outil par des utilisateurs anglophones et francophones sans dupliquer la logique interne des prompts. Le système doit supporter le français (FR) et l'anglais (EN) pour tous les messages d'interface et les réponses de l'IA.

## User Scenarios & Testing

### User Story 1 - Language Detection (Priority: P1)

En tant qu'utilisateur, je veux que l'outil détecte automatiquement ma langue préférée pour recevoir les messages dans ma langue.

**Why this priority**: Expérience utilisateur de base - l'outil doit "parler" la langue de l'utilisateur dès le premier lancement.

**Independent Test**: Configurer `LANG=en` et vérifier que tous les messages s'affichent en anglais.

**Acceptance Scenarios**:

1. **Given** la variable d'environnement `LANG=fr`, **When** l'utilisateur lance une commande, **Then** tous les messages s'affichent en français
2. **Given** la variable d'environnement `LANG=en`, **When** l'utilisateur lance une commande, **Then** tous les messages s'affichent en anglais
3. **Given** aucune variable `LANG` définie, **When** l'utilisateur lance une commande, **Then** les messages s'affichent en français (langue par défaut)

---

### User Story 2 - CLI Language Override (Priority: P1)

En tant qu'utilisateur, je veux pouvoir forcer la langue via un paramètre CLI pour surcharger la détection automatique.

**Why this priority**: Flexibilité essentielle pour les utilisateurs multilingues ou les environnements partagés.

**Independent Test**: Exécuter `aetheris analysis --lang en` et vérifier que la sortie est en anglais.

**Acceptance Scenarios**:

1. **Given** `LANG=fr`, **When** l'utilisateur exécute `aetheris --lang en analysis`, **Then** les messages s'affichent en anglais
2. **Given** `LANG=en`, **When** l'utilisateur exécute `aetheris --lang fr analysis`, **Then** les messages s'affichent en français
3. **Given** une langue invalide `--lang de`, **When** l'utilisateur lance une commande, **Then** un message d'erreur indique les langues supportées

---

### User Story 3 - AI Response Language (Priority: P1)

En tant qu'utilisateur anglophone, je veux que les rapports d'analyse générés par l'IA soient en anglais, même si les prompts internes sont en français.

**Why this priority**: Critical pour les utilisateurs anglophones - les rapports doivent être dans leur langue.

**Independent Test**: Configurer `--lang en` et vérifier que le rapport d'analyse est entièrement en anglais.

**Acceptance Scenarios**:

1. **Given** la langue configurée en anglais, **When** l'IA génère un rapport, **Then** le rapport est entièrement en anglais
2. **Given** la langue configurée en français, **When** l'IA génère un rapport, **Then** le rapport est en français
3. **Given** un changement de langue entre analyses, **When** une nouvelle analyse est lancée, **Then** le nouveau rapport utilise la langue actuellement configurée

---

### User Story 4 - Static Text Externalization (Priority: P2)

En tant que mainteneur, je veux que tous les textes statiques (messages d'erreur, aide, etc.) soient externalisés pour faciliter les traductions.

**Why this priority**: Facilite la maintenance et l'ajout de nouvelles langues à l'avenir.

**Independent Test**: Vérifier que tous les messages proviennent d'un fichier de ressources et non de chaînes codées en dur.

**Acceptance Scenarios**:

1. **Given** le système en français, **When** un message d'erreur est affiché, **Then** il provient du dictionnaire français
2. **Given** le système en anglais, **When** un message d'erreur est affiché, **Then** il provient du dictionnaire anglais
3. **Given** une clé de message manquante, **When** le message est demandé, **Then** la clé est affichée (fallback)

---

### Edge Cases

- Que se passe-t-il si le fichier de ressources linguistiques est corrompu?
- Comment gérer les langues partiellement traduites?
- Que se passe-t-il si l'IA ne respecte pas l'instruction de langue?
- Comment gérer les termes techniques qui ne doivent pas être traduits (noms de fichiers, commandes)?

## Requirements

### Functional Requirements

- **FR-001**: Le système DOIT supporter le français (FR) et l'anglais (EN)
- **FR-002**: Le système DOIT détecter la langue via la variable d'environnement `LANG`
- **FR-003**: Le système DOIT permettre de surcharger la langue via `--lang` (ou `-l`)
- **FR-004**: Le système DOIT externaliser tous les textes statiques dans des fichiers de ressources
- **FR-005**: Le système DOIT charger dynamiquement le dictionnaire selon la langue choisie
- **FR-006**: Le système DOIT injecter une instruction système à l'IA pour forcer la langue de réponse
- **FR-007**: Le système DOIT utiliser le français comme langue par défaut si aucune n'est spécifiée
- **FR-008**: Le système DOIT afficher un message d'erreur clair pour les langues non supportées
- **FR-009**: Les prompts internes DOIVENT rester en français (source unique) avec injection dynamique pour les autres langues
- **FR-010**: Les termes techniques (noms de fichiers, commandes, variables) NE DOIVENT PAS être traduits

### Key Entities

- **LanguageConfig**: Configuration de la langue actuelle (code, source de détection)
- **MessageDictionary**: Dictionnaire de messages traduits par langue
- **AILanguageInstruction**: Instruction système pour forcer la langue de l'IA

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% des messages utilisateur sont traduits dans les langues supportées
- **SC-002**: 95% des réponses IA sont dans la langue configurée
- **SC-003**: Le changement de langue prend effet immédiatement (sans redémarrage)
- **SC-004**: Aucun texte codé en dur ne reste dans le code source
- **SC-005**: Le temps de chargement n'augmente pas de plus de 100ms à cause de l'i18n

## Assumptions

- Les prompts sources restent en français pour une maintenance unique
- L'IA (Gemini/OpenAI/Claude) respecte les instructions de langue dans la plupart des cas
- Les utilisateurs ont soit `LANG=fr` soit `LANG=en` dans leur environnement
- Les fichiers de ressources utilisent un format simple (YAML ou JSON)

## Out of Scope

- Support d'autres langues que FR et EN (prévu pour versions futures)
- Interface de gestion des traductions
- Traduction automatique des messages
- Localisation des formats de date/nombre
- Support des langues RTL (right-to-left)
