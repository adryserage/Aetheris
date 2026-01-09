# Feature Specification: Migration Gemini CLI & Intégration Skills

**Feature Branch**: `015-gemini-cli-skills`
**Created**: 2026-01-09
**Status**: Draft
**Target Version**: v2.8

## Overview

Transitionner de l'utilisation directe de l'API Gemini vers une architecture "CLI Wrapper" unifiée, similaire à Claude CLI. Cette version introduit des capacités d'agents actifs ("Skills") pour les deux modèles (Claude et Gemini) et un orchestrateur ("Conductor") spécifique pour Gemini, ainsi que l'intégration du Model Context Protocol (MCP).

## User Scenarios & Testing

### User Story 1 - Unified CLI Interface (Priority: P1)

En tant qu'utilisateur d'Aetheris, je veux pouvoir utiliser une interface CLI unifiée qui abstrait les différences entre les providers AI (Claude et Gemini), afin de ne pas avoir à modifier mes commandes selon le provider choisi.

**Why this priority**: Fondation de l'architecture - toutes les autres fonctionnalités dépendent de cette abstraction unifiée.

**Independent Test**: Exécuter `aetheris analysis --provider gemini` et `aetheris analysis --provider claude` avec les mêmes paramètres et obtenir des résultats de format identique.

**Acceptance Scenarios**:

1. **Given** un utilisateur configure `--provider gemini`, **When** il lance une commande d'analyse, **Then** la CLI utilise le wrapper Gemini de manière transparente
2. **Given** un utilisateur configure `--provider claude`, **When** il lance une commande d'analyse, **Then** la CLI utilise le wrapper Claude de manière transparente
3. **Given** aucun provider spécifié, **When** l'utilisateur lance une commande, **Then** le provider par défaut (configuré) est utilisé
4. **Given** un provider non supporté, **When** l'utilisateur lance une commande, **Then** un message d'erreur explicite est affiché

---

### User Story 2 - Agent Skills for Claude (Priority: P1)

En tant qu'utilisateur d'Aetheris avec Claude, je veux que l'IA puisse interagir avec mon système de fichiers et exécuter des commandes, afin d'automatiser les corrections de code suggérées.

**Why this priority**: Capacité d'action critique - permet l'auto-fix et l'automatisation des corrections.

**Independent Test**: Lancer `aetheris fix --auto --provider claude` et vérifier que Claude modifie effectivement les fichiers sur le disque.

**Acceptance Scenarios**:

1. **Given** une analyse avec des issues détectées, **When** l'utilisateur demande un fix automatique avec Claude, **Then** Claude utilise ses skills pour modifier les fichiers concernés
2. **Given** un skill de lecture de fichier, **When** Claude a besoin de contexte, **Then** il peut lire les fichiers nécessaires sans intervention utilisateur
3. **Given** un skill d'exécution de commande, **When** Claude doit vérifier une correction, **Then** il peut exécuter des tests ou linters
4. **Given** une action potentiellement dangereuse, **When** Claude tente de l'exécuter, **Then** une confirmation utilisateur est requise (mode safe)

---

### User Story 3 - Agent Skills for Gemini (Priority: P1)

En tant qu'utilisateur d'Aetheris avec Gemini, je veux bénéficier des mêmes capacités d'action que Claude via Function Calling, afin d'avoir une parité fonctionnelle entre les providers.

**Why this priority**: Parité fonctionnelle - les utilisateurs de Gemini doivent avoir les mêmes capacités.

**Independent Test**: Lancer `aetheris fix --auto --provider gemini` et vérifier que Gemini modifie effectivement les fichiers sur le disque via Function Calling.

**Acceptance Scenarios**:

1. **Given** une analyse avec des issues détectées, **When** l'utilisateur demande un fix avec Gemini, **Then** Gemini utilise Function Calling pour modifier les fichiers
2. **Given** les mêmes skills disponibles pour Claude, **When** Gemini est utilisé, **Then** les mêmes skills sont disponibles via Function Calling
3. **Given** un skill échoue, **When** Gemini reçoit l'erreur, **Then** il peut adapter sa stratégie et réessayer

---

### User Story 4 - Gemini Conductor Orchestration (Priority: P2)

En tant qu'utilisateur d'Aetheris avec Gemini, je veux qu'un module "Conductor" décompose les requêtes complexes en étapes planifiées, afin d'améliorer la qualité des réponses sur les tâches multi-étapes.

**Why this priority**: Amélioration de qualité - le Conductor permet de mieux gérer les tâches complexes avec Gemini.

**Independent Test**: Soumettre une tâche complexe (ex: "Analyse le projet et corrige tous les problèmes de sécurité critiques") et vérifier que le Conductor décompose en étapes.

**Acceptance Scenarios**:

1. **Given** une requête complexe multi-étapes, **When** elle est soumise à Gemini, **Then** le Conductor crée un plan d'exécution
2. **Given** un plan d'exécution créé, **When** le Conductor l'exécute, **Then** chaque étape est déléguée au skill approprié
3. **Given** une étape échoue, **When** le Conductor détecte l'échec, **Then** il peut re-planifier ou reporter l'erreur
4. **Given** le mode verbose activé, **When** le Conductor s'exécute, **Then** le plan et la progression sont affichés

---

### User Story 5 - MCP Integration (Priority: P2)

En tant qu'utilisateur d'Aetheris, je veux que l'outil supporte le Model Context Protocol (MCP), afin de pouvoir connecter des sources de contexte externes et des outils tiers.

**Why this priority**: Extensibilité - MCP permet l'intégration avec l'écosystème d'outils AI existant.

**Independent Test**: Configurer un serveur MCP local et vérifier qu'Aetheris peut l'utiliser comme source de contexte ou d'outils.

**Acceptance Scenarios**:

1. **Given** un serveur MCP configuré, **When** Aetheris démarre, **Then** il se connecte et découvre les ressources disponibles
2. **Given** des outils MCP disponibles, **When** l'AI a besoin d'une action, **Then** les outils MCP sont disponibles comme skills
3. **Given** des ressources MCP (contexte), **When** l'analyse démarre, **Then** le contexte MCP est inclus dans les prompts
4. **Given** aucun serveur MCP configuré, **When** Aetheris démarre, **Then** il fonctionne normalement sans MCP

---

### User Story 6 - Skill Registry & Discovery (Priority: P3)

En tant que développeur, je veux pouvoir enregistrer de nouveaux skills personnalisés, afin d'étendre les capacités de l'outil selon mes besoins.

**Why this priority**: Extensibilité avancée - permet la personnalisation pour des cas d'usage spécifiques.

**Independent Test**: Créer un skill personnalisé et vérifier qu'il est disponible pour les AI.

**Acceptance Scenarios**:

1. **Given** un fichier de définition de skill valide, **When** Aetheris charge les skills, **Then** le skill personnalisé est disponible
2. **Given** un skill avec des permissions requises, **When** il est invoqué, **Then** les permissions sont vérifiées
3. **Given** un skill mal formé, **When** Aetheris tente de le charger, **Then** une erreur explicite est affichée

---

### Edge Cases

- Que se passe-t-il si un provider est indisponible temporairement pendant une session?
- Comment gérer les différences de capacités entre Claude et Gemini (certains skills non supportés)?
- Que se passe-t-il si un skill tente d'accéder à un fichier hors du projet?
- Comment gérer les timeouts sur les appels Function Calling de longue durée?
- Que se passe-t-il si le Conductor détecte une boucle infinie dans le plan?
- Comment gérer les conflits entre skills MCP et skills intégrés du même nom?
- Que se passe-t-il si la connexion MCP est perdue en cours d'exécution?

## Requirements

### Functional Requirements

#### Architecture CLI Wrapper

- **FR-001**: Le système DOIT fournir une interface CLI unifiée abstraisant les appels API directs
- **FR-002**: Le système DOIT supporter les providers Claude et Gemini via le même jeu de commandes
- **FR-003**: Le système DOIT permettre la sélection du provider via `--provider` flag ou configuration
- **FR-004**: Le système DOIT maintenir une parité fonctionnelle maximale entre les providers
- **FR-005**: Le système DOIT gérer gracieusement les fonctionnalités non supportées par un provider

#### Agent Skills - Claude

- **FR-006**: Le système DOIT implémenter un skill de lecture de fichiers pour Claude
- **FR-007**: Le système DOIT implémenter un skill d'écriture de fichiers pour Claude
- **FR-008**: Le système DOIT implémenter un skill d'exécution de commandes shell pour Claude
- **FR-009**: Le système DOIT implémenter un skill de recherche dans les fichiers pour Claude
- **FR-010**: Le système DOIT implémenter un mode "safe" avec confirmation pour les actions destructives

#### Agent Skills - Gemini

- **FR-011**: Le système DOIT mapper les skills Claude vers des Function Calling Gemini équivalents
- **FR-012**: Le système DOIT fournir les mêmes skills de base pour Gemini que pour Claude
- **FR-013**: Le système DOIT gérer les différences de format de réponse entre Claude Tool Use et Gemini Function Calling

#### Gemini Conductor

- **FR-014**: Le système DOIT fournir un module Conductor pour décomposer les requêtes complexes
- **FR-015**: Le système DOIT permettre au Conductor de créer un plan d'exécution en étapes
- **FR-016**: Le système DOIT permettre au Conductor de déléguer les étapes aux skills appropriés
- **FR-017**: Le système DOIT permettre au Conductor de gérer les erreurs et re-planifier si nécessaire
- **FR-018**: Le système DOIT afficher la progression du Conductor en mode verbose

#### Intégration MCP

- **FR-019**: Le système DOIT supporter la connexion à des serveurs MCP locaux
- **FR-020**: Le système DOIT découvrir automatiquement les ressources et outils MCP disponibles
- **FR-021**: Le système DOIT intégrer les outils MCP comme skills disponibles pour les AI
- **FR-022**: Le système DOIT intégrer les ressources MCP comme contexte pour les analyses
- **FR-023**: Le système DOIT fonctionner normalement en l'absence de serveur MCP

#### Skill Registry

- **FR-024**: Le système DOIT maintenir un registre des skills disponibles
- **FR-025**: Le système DOIT permettre l'enregistrement de skills personnalisés via fichiers de configuration
- **FR-026**: Le système DOIT valider les définitions de skills au chargement
- **FR-027**: Le système DOIT documenter chaque skill avec nom, description, et paramètres

### Non-Functional Requirements

- **NFR-001**: Le temps de réponse de la CLI ne doit pas être impacté de plus de 10% par le wrapper
- **NFR-002**: Les skills doivent s'exécuter avec les mêmes permissions que l'utilisateur lancant Aetheris
- **NFR-003**: Le Conductor ne doit pas créer de plans avec plus de 20 étapes pour éviter les boucles

### Key Entities

- **CLIWrapper**: Abstraction unifiant les appels aux différents providers AI
- **Skill**: Capacité d'action atomique (lecture, écriture, exécution) disponible pour les AI
- **SkillRegistry**: Registre central des skills disponibles par provider
- **Conductor**: Module d'orchestration décomposant les tâches complexes en plans
- **ExecutionPlan**: Séquence d'étapes planifiées par le Conductor
- **MCPClient**: Client pour la connexion aux serveurs Model Context Protocol
- **MCPResource**: Ressource de contexte découverte via MCP
- **MCPTool**: Outil découvert via MCP, mappé comme skill

## Success Criteria

### Measurable Outcomes

- **SC-001**: Les utilisateurs peuvent exécuter 100% des commandes existantes avec les deux providers sans modifier leur syntaxe
- **SC-002**: Le taux de succès des auto-fix est identique (±5%) entre Claude et Gemini sur le même jeu de tests
- **SC-003**: Les tâches complexes décomposées par le Conductor ont un taux de réussite supérieur à 80%
- **SC-004**: La connexion MCP est établie en moins de 2 secondes au démarrage
- **SC-005**: Les skills personnalisés peuvent être ajoutés sans modification du code source
- **SC-006**: 100% des skills de base sont disponibles pour les deux providers (Claude et Gemini)

## Assumptions

- Les utilisateurs ont déjà configuré leurs clés API pour au moins un provider
- L'environnement d'exécution permet les appels réseau vers les APIs AI
- Les serveurs MCP, s'ils sont utilisés, suivent la spécification MCP standard
- Gemini Function Calling et Claude Tool Use ont des capacités suffisamment similaires pour une abstraction commune
- Les utilisateurs acceptent les risques liés à l'exécution automatique de commandes (mode unsafe)

## Out of Scope

- Support d'autres providers AI au-delà de Claude et Gemini (OpenAI déjà existant reste inchangé)
- Interface graphique pour la gestion des skills
- Création de serveurs MCP (uniquement client)
- Marketplace ou partage de skills personnalisés
- Mode multi-provider simultané (un seul provider actif par session)

## Dependencies

- **v2.6.1**: Architecture de base des providers (existante)
- **v3.0** (optionnel): Persistent Config pour stocker les préférences MCP

## Config Integration (v3.0+)

À partir de v3.0, les options seront configurables via `config.json`:

```json
{
  "cli": {
    "default_provider": "gemini",
    "enable_conductor": true,
    "conductor_max_steps": 20
  },
  "skills": {
    "safe_mode": true,
    "custom_skills_path": "./aetheris-skills/",
    "enabled_skills": ["read_file", "write_file", "execute_command", "search_files"]
  },
  "mcp": {
    "enabled": false,
    "servers": [
      {
        "name": "local-tools",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem"]
      }
    ]
  }
}
```
