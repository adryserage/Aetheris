# Feature Specification: Multi-Modèles & Analysis Skills

**Feature Branch**: `015-gemini-cli-skills`
**Created**: 2026-01-09
**Status**: Draft
**Target Version**: v4.0
**Depends On**: v3.0 (Persistent Config with Security Profiles), v3.1 (Headless Architecture)

## Overview

Transitionner vers une architecture multi-modèles unifiée supportant Gemini, Claude et OpenRouter. Cette version introduit des **Analysis Skills** - des outils d'analyse enrichie (pas d'exécution autonome) - pour améliorer la qualité et la profondeur des analyses de code.

**IMPORTANT**: Les Skills sont des outils d'**analyse enrichie uniquement**. Ils ne modifient PAS le code et n'exécutent PAS de commandes. Ils fournissent du contexte supplémentaire pour améliorer l'analyse.

### Analysis Skills v4.1

| Skill | Description | Valeur |
|-------|-------------|--------|
| `security-context` | Enrichit l'analyse avec CVE database et contexte de sécurité | Détection vulnérabilités connues |
| `complexity-hotspots` | Identifie les fichiers/fonctions les plus complexes | Ciblage refactoring |
| `dependency-graph` | Visualise les dépendances entre modules | Compréhension architecture |

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

### User Story 2 - OpenRouter Integration (Priority: P1)

En tant qu'utilisateur d'Aetheris, je veux pouvoir utiliser OpenRouter comme provider pour accéder à une variété de modèles (Llama, Mistral, etc.) via une API unifiée.

**Why this priority**: Flexibilité - OpenRouter permet d'accéder à des modèles open-source et de réduire les coûts.

**Independent Test**: Configurer `--provider openrouter --model meta-llama/llama-3-70b` et lancer une analyse.

**Acceptance Scenarios**:

1. **Given** un utilisateur configure `--provider openrouter`, **When** il lance une commande, **Then** l'API OpenRouter est utilisée
2. **Given** un modèle spécifique via `--model`, **When** la commande s'exécute, **Then** ce modèle est utilisé
3. **Given** une clé API OpenRouter dans `.env`, **When** Aetheris démarre, **Then** le provider est disponible

---

### User Story 3 - Security Context Skill (Priority: P1)

En tant qu'utilisateur d'Aetheris, je veux que l'analyse de sécurité soit enrichie avec des données de CVE et des patterns de vulnérabilités connus, afin de détecter des problèmes que l'AI seule pourrait manquer.

**Why this priority**: Amélioration qualité analyse - combine AI + base de données de vulnérabilités.

**Independent Test**: Lancer `aetheris analysis --skills security-context` et vérifier que le rapport inclut des références CVE.

**Acceptance Scenarios**:

1. **Given** le skill security-context activé, **When** une dépendance vulnérable est détectée, **Then** les CVE correspondantes sont incluses dans le rapport
2. **Given** un pattern de code vulnérable connu, **When** l'analyse s'exécute, **Then** le pattern est identifié avec référence OWASP/CWE
3. **Given** aucune vulnérabilité connue, **When** l'analyse se termine, **Then** le skill n'ajoute pas de bruit au rapport

---

### User Story 4 - Complexity Hotspots Skill (Priority: P1)

En tant qu'utilisateur d'Aetheris, je veux identifier automatiquement les fichiers et fonctions les plus complexes du codebase, afin de prioriser mes efforts de refactoring.

**Why this priority**: Ciblage précis - permet de focaliser l'attention sur le code le plus problématique.

**Independent Test**: Lancer `aetheris analysis --skills complexity-hotspots` et obtenir un classement des fichiers par complexité.

**Acceptance Scenarios**:

1. **Given** le skill complexity-hotspots activé, **When** l'analyse se termine, **Then** un classement des fichiers par complexité est inclus
2. **Given** des métriques de complexité (cyclomatic, cognitive), **When** le rapport est généré, **Then** les scores sont affichés par fichier/fonction
3. **Given** un seuil de complexité configurable, **When** un fichier dépasse le seuil, **Then** il est marqué comme "hotspot" prioritaire

---

### User Story 5 - Dependency Graph Skill (Priority: P2)

En tant qu'utilisateur d'Aetheris, je veux visualiser les dépendances entre modules de mon codebase, afin de comprendre l'architecture et identifier les couplages problématiques.

**Why this priority**: Compréhension architecture - aide à planifier les refactorings et comprendre l'impact des changements.

**Independent Test**: Lancer `aetheris analysis --skills dependency-graph` et obtenir une visualisation des dépendances.

**Acceptance Scenarios**:

1. **Given** le skill dependency-graph activé, **When** l'analyse se termine, **Then** un graphe des dépendances est généré
2. **Given** des imports circulaires détectés, **When** le rapport est généré, **Then** les cycles sont mis en évidence
3. **Given** l'option `--output-format mermaid`, **When** le skill s'exécute, **Then** le graphe est exporté en format Mermaid
4. **Given** un module avec beaucoup de dépendants, **When** le rapport est généré, **Then** il est identifié comme "high-impact"

---

### User Story 6 - MCP Integration for Context (Priority: P2)

En tant qu'utilisateur d'Aetheris, je veux que l'outil supporte le Model Context Protocol (MCP) pour enrichir l'analyse avec des sources de contexte externes.

**Why this priority**: Extensibilité - MCP permet d'intégrer des sources de documentation et de contexte projet.

**Independent Test**: Configurer un serveur MCP local et vérifier qu'Aetheris utilise le contexte MCP dans l'analyse.

**Acceptance Scenarios**:

1. **Given** un serveur MCP configuré, **When** Aetheris démarre, **Then** il se connecte et découvre les ressources de contexte
2. **Given** des ressources MCP (documentation, specs), **When** l'analyse démarre, **Then** le contexte MCP enrichit les prompts
3. **Given** aucun serveur MCP configuré, **When** Aetheris démarre, **Then** il fonctionne normalement sans MCP

---

### User Story 7 - Skills Configuration (Priority: P3)

En tant qu'utilisateur, je veux pouvoir configurer quels skills sont actifs par défaut et leurs paramètres, via config.json.

**Why this priority**: Personnalisation - permet d'adapter les skills aux besoins du projet.

**Independent Test**: Configurer `analysis.default_skills: ["security-context", "complexity-hotspots"]` et vérifier qu'ils sont utilisés par défaut.

**Acceptance Scenarios**:

1. **Given** des skills configurés dans config.json, **When** l'analyse démarre sans `--skills`, **Then** les skills configurés sont utilisés
2. **Given** `--skills none` sur la CLI, **When** l'analyse s'exécute, **Then** aucun skill n'est utilisé
3. **Given** un skill inconnu configuré, **When** Aetheris charge la config, **Then** un warning est affiché

---

### Edge Cases & Solutions

#### Multi-Provider

| Edge Case | Solution |
|-----------|----------|
| Provider indisponible temporairement | Circuit breaker avec 3 tentatives. Fallback sur cache local si disponible. Message d'erreur explicite |
| Différences de capacités entre providers | Maintenir une matrice de compatibilité. Afficher warning si feature non supportée |
| Clé API manquante pour provider | Message d'erreur explicite indiquant quelle variable d'environnement configurer |
| Provider OpenRouter avec modèle invalide | Valider le modèle via API OpenRouter. Lister les modèles disponibles sur erreur |

#### Analysis Skills

| Edge Case | Solution |
|-----------|----------|
| Skill security-context sans connexion OSV | Mode dégradé: utiliser cache local des CVE. Warning dans le rapport |
| Skill complexity-hotspots sur très gros projet | Limite configurable de fichiers analysés. Progress bar pour long processing |
| Skill dependency-graph avec imports dynamiques | Documenter les limitations. Marquer les imports non résolus dans le graphe |
| Skill retourne données incomplètes | Continuer l'analyse. Inclure warning dans le rapport. Ne pas bloquer |

#### MCP Integration

| Edge Case | Solution |
|-----------|----------|
| Connexion MCP perdue | Retry automatique (3x avec backoff). Continuer sans MCP si échec. Log warning |
| Ressource MCP trop volumineuse | Limite de taille configurable. Tronquer avec warning si dépassée |

## Requirements

### Functional Requirements

#### Multi-Provider Architecture

- **FR-001**: Le système DOIT fournir une interface CLI unifiée abstraisant les appels API directs
- **FR-002**: Le système DOIT supporter les providers Gemini, Claude et OpenRouter
- **FR-003**: Le système DOIT permettre la sélection du provider via `--provider` flag ou configuration
- **FR-004**: Le système DOIT maintenir une parité fonctionnelle maximale entre les providers
- **FR-005**: Le système DOIT gérer gracieusement les fonctionnalités non supportées par un provider
- **FR-006**: Le système DOIT supporter la sélection de modèle via `--model` flag

#### Analysis Skills

- **FR-007**: Le système DOIT fournir un skill `security-context` enrichissant l'analyse avec CVE/OWASP data
- **FR-008**: Le système DOIT fournir un skill `complexity-hotspots` identifiant les fichiers/fonctions complexes
- **FR-009**: Le système DOIT fournir un skill `dependency-graph` visualisant les dépendances entre modules
- **FR-010**: Le système DOIT permettre l'activation des skills via `--skills skill1,skill2`
- **FR-011**: Le système DOIT permettre de désactiver tous les skills via `--skills none`
- **FR-012**: Les skills NE DOIVENT PAS modifier le code ni exécuter de commandes (lecture seule)
- **FR-013**: Les skills DOIVENT enrichir le rapport d'analyse avec leurs données

#### Skill: Security Context

- **FR-014**: Le skill DOIT interroger la base OSV pour les CVE des dépendances
- **FR-015**: Le skill DOIT identifier les patterns OWASP/CWE dans le code
- **FR-016**: Le skill DOIT inclure les références CVE dans le rapport de sécurité

#### Skill: Complexity Hotspots

- **FR-017**: Le skill DOIT calculer la complexité cyclomatique par fonction
- **FR-018**: Le skill DOIT calculer la complexité cognitive par fonction
- **FR-019**: Le skill DOIT classer les fichiers par score de complexité
- **FR-020**: Le skill DOIT permettre de configurer un seuil de complexité

#### Skill: Dependency Graph

- **FR-021**: Le skill DOIT analyser les imports/requires du projet
- **FR-022**: Le skill DOIT détecter les dépendances circulaires
- **FR-023**: Le skill DOIT identifier les modules à fort impact (beaucoup de dépendants)
- **FR-024**: Le skill DOIT exporter le graphe en format Mermaid optionnellement

#### MCP Integration

- **FR-025**: Le système DOIT supporter la connexion à des serveurs MCP locaux
- **FR-026**: Le système DOIT intégrer les ressources MCP comme contexte pour les analyses
- **FR-027**: Le système DOIT fonctionner normalement en l'absence de serveur MCP

#### Configuration

- **FR-028**: Le système DOIT supporter `analysis.default_skills` dans config.json
- **FR-029**: Le système DOIT supporter des paramètres par skill dans config.json
- **FR-030**: Le système DOIT valider les noms de skills au chargement

### Non-Functional Requirements

- **NFR-001**: Les skills ne doivent pas augmenter le temps d'analyse de plus de 30%
- **NFR-002**: Les skills doivent fonctionner en mode lecture seule uniquement
- **NFR-003**: Les données des skills doivent être cachables pour les analyses répétées

### Key Entities

- **AIProvider**: Abstraction unifiant les appels aux différents providers (Gemini, Claude, OpenRouter)
- **AnalysisSkill**: Interface pour les skills d'analyse enrichie (read-only)
- **SecurityContextSkill**: Skill enrichissant avec CVE/OWASP data
- **ComplexityHotspotsSkill**: Skill identifiant la complexité du code
- **DependencyGraphSkill**: Skill visualisant les dépendances
- **SkillRegistry**: Registre des skills disponibles et leur configuration
- **MCPClient**: Client pour la connexion aux serveurs Model Context Protocol
- **MCPResource**: Ressource de contexte découverte via MCP

## Success Criteria

### Measurable Outcomes

- **SC-001**: Les utilisateurs peuvent exécuter 100% des commandes existantes avec les trois providers (Gemini, Claude, OpenRouter) sans modifier leur syntaxe
- **SC-002**: Le skill security-context identifie 100% des CVE connues pour les dépendances du projet
- **SC-003**: Le skill complexity-hotspots calcule les métriques de complexité en moins de 5 secondes pour un projet de 1000 fichiers
- **SC-004**: Le skill dependency-graph génère un graphe correct pour 95% des imports analysés
- **SC-005**: La connexion MCP est établie en moins de 2 secondes au démarrage
- **SC-006**: Les skills n'augmentent pas le temps d'analyse de plus de 30%

## Assumptions

- Les utilisateurs ont déjà configuré leurs clés API pour au moins un provider
- L'environnement d'exécution permet les appels réseau vers les APIs AI et OSV
- Les serveurs MCP, s'ils sont utilisés, suivent la spécification MCP standard
- Les skills fonctionnent en mode lecture seule et n'ont pas besoin de permissions d'écriture

## Out of Scope

- Skills qui modifient le code ou exécutent des commandes (hors scope - analyse seulement)
- Interface graphique pour la gestion des skills
- Création de serveurs MCP (uniquement client)
- Mode multi-provider simultané (un seul provider actif par session)
- TUI interactive (utiliser la CLI standard)

## Dependencies

- **v3.0**: Persistent Config pour stocker les préférences de skills et provider
- **v3.1**: Headless Architecture pour l'intégration CI/CD

## Config Integration (v3.0+)

Les options seront configurables via `config.json`:

```json
{
  "ai": {
    "provider": "gemini",
    "model": "default"
  },
  "analysis": {
    "default_skills": ["security-context", "complexity-hotspots"],
    "skills": {
      "security-context": {
        "include_owasp": true,
        "cve_cache_ttl": 86400
      },
      "complexity-hotspots": {
        "threshold": 15,
        "max_files": 100
      },
      "dependency-graph": {
        "output_format": "mermaid",
        "include_external": false
      }
    }
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
