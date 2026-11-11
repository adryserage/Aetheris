# Feature Specification: Advanced Statistics Command

**Feature Branch**: `003-advanced-stats`
**Created**: 2025-01-07
**Status**: Draft
**Target Version**: v2.6.5

## Overview

Fournir à l'utilisateur une vision claire de la valeur ajoutée par l'outil via une commande dédiée (`stats`) affichant des métriques de performance et de ROI (Retour sur Investissement).

## User Scenarios & Testing

### User Story 1 - View Project Metrics (Priority: P1)

En tant qu'utilisateur, je veux voir les métriques de contexte de mon projet (fichiers analysés, lignes de code) pour comprendre la couverture de l'analyse.

**Why this priority**: Fournit le contexte de base nécessaire pour interpréter toutes les autres métriques.

**Independent Test**: Exécuter `aetheris stats` et vérifier que le nombre de fichiers et de lignes de code s'affiche correctement.

**Acceptance Scenarios**:

1. **Given** un projet avec des analyses effectuées, **When** l'utilisateur exécute `aetheris stats`, **Then** un tableau affiche le nombre total de fichiers analysés
2. **Given** un projet avec des analyses effectuées, **When** l'utilisateur exécute `aetheris stats`, **Then** un tableau affiche le nombre total de lignes de code traitées
3. **Given** un projet sans analyses, **When** l'utilisateur exécute `aetheris stats`, **Then** un message indique qu'aucune analyse n'a été effectuée

---

### User Story 2 - View Performance Metrics (Priority: P1)

En tant qu'utilisateur, je veux voir les métriques de performance (bugs détectés, bugs résolus, temps passé) pour évaluer l'efficacité de l'outil.

**Why this priority**: Permet aux utilisateurs de comprendre l'activité et les résultats de l'outil.

**Independent Test**: Exécuter `aetheris stats` et vérifier que les compteurs de bugs et les temps s'affichent.

**Acceptance Scenarios**:

1. **Given** un projet avec des bugs détectés, **When** l'utilisateur exécute `aetheris stats`, **Then** le tableau affiche le nombre de bugs détectés
2. **Given** un projet avec des bugs résolus, **When** l'utilisateur exécute `aetheris stats`, **Then** le tableau affiche le nombre de bugs résolus avec succès
3. **Given** un projet avec des analyses, **When** l'utilisateur exécute `aetheris stats`, **Then** le tableau affiche le temps total passé à analyser les fichiers
4. **Given** un projet avec des correctifs générés, **When** l'utilisateur exécute `aetheris stats`, **Then** le tableau affiche le temps total passé à générer des correctifs

---

### User Story 3 - View ROI Metrics (Priority: P2)

En tant qu'utilisateur, je veux voir les métriques de ROI (temps économisé, argent économisé) pour justifier l'investissement dans l'outil.

**Why this priority**: Valeur ajoutée importante pour les décideurs, mais non essentielle pour l'utilisation quotidienne.

**Independent Test**: Exécuter `aetheris stats` et vérifier que les estimations de ROI s'affichent.

**Acceptance Scenarios**:

1. **Given** un projet avec des bugs résolus, **When** l'utilisateur exécute `aetheris stats`, **Then** le tableau affiche le temps humain estimé économisé
2. **Given** un taux horaire configuré, **When** l'utilisateur exécute `aetheris stats`, **Then** le tableau affiche l'argent économisé basé sur le temps × taux
3. **Given** aucun taux horaire configuré, **When** l'utilisateur exécute `aetheris stats`, **Then** le système utilise le taux régional par défaut basé sur la locale système (85€/h Europe, 120$CAD/h Canada, 95$USD/h USA)

---

### User Story 4 - Regenerate Statistics (Priority: P3)

En tant qu'utilisateur, je veux pouvoir régénérer les statistiques de ROI si les heuristiques ont changé.

**Why this priority**: Fonctionnalité de maintenance, rarement utilisée.

**Independent Test**: Exécuter `aetheris stats --regenerate` et vérifier que les statistiques sont recalculées.

**Acceptance Scenarios**:

1. **Given** des statistiques existantes, **When** l'utilisateur exécute `aetheris stats --regenerate`, **Then** les statistiques de ROI sont recalculées
2. **Given** des statistiques régénérées, **When** l'utilisateur consulte les stats, **Then** les nouvelles valeurs sont affichées

---

### Edge Cases

- Que se passe-t-il si le projet n'a jamais été analysé?
- Que se passe-t-il si les fichiers de statistiques sont corrompus?
- Comment gérer les analyses partielles (interrompues)?
- Que se passe-t-il si le taux horaire est négatif ou invalide?

## Requirements

### Functional Requirements

- **FR-001**: Le système DOIT fournir une commande `aetheris stats` pour afficher les statistiques
- **FR-002**: Le système DOIT afficher les métriques dans un tableau formaté (ASCII/Unicode)
- **FR-003**: Le système DOIT afficher le nombre total de fichiers analysés
- **FR-004**: Le système DOIT afficher le nombre total de lignes de code traitées
- **FR-005**: Le système DOIT afficher le nombre de bugs détectés
- **FR-006**: Le système DOIT afficher le nombre de bugs résolus avec succès
- **FR-007**: Le système DOIT afficher le temps total passé à analyser
- **FR-008**: Le système DOIT afficher le temps total passé à générer des correctifs
- **FR-009**: Le système DOIT calculer et afficher le temps humain estimé économisé
- **FR-010**: Le système DOIT calculer et afficher l'argent économisé (temps × taux horaire)
- **FR-011**: Le système DOIT permettre de configurer le taux horaire (avec des valeurs par défaut régionales: 85€/h Europe, 120$CAD/h Canada, 95$USD/h USA)
- **FR-012**: Le système DOIT supporter l'option `--regenerate` pour recalculer les statistiques
- **FR-013**: Le système DOIT collecter les statistiques automatiquement lors de chaque analyse

### Key Entities

- **ProjectStats**: Statistiques globales du projet (fichiers, LOC)
- **PerformanceMetrics**: Compteurs de bugs détectés/résolus et temps passés
- **ROIMetrics**: Calculs de temps économisé et valeur monétaire
- **HeuristicConfig**: Configuration des heuristiques de calcul (temps par type de bug)

## Success Criteria

### Measurable Outcomes

- **SC-001**: Les utilisateurs peuvent consulter les statistiques en moins de 2 secondes
- **SC-002**: 100% des analyses contribuent aux statistiques cumulées
- **SC-003**: Les métriques de ROI aident à justifier l'outil (90% des utilisateurs comprennent la valeur)
- **SC-004**: Le tableau des statistiques est lisible et formaté correctement dans tous les terminaux standards
- **SC-005**: Les calculs de ROI sont basés sur des heuristiques documentées et reproductibles

## Heuristiques de calcul du temps humain (DEV + QA)

Les estimations suivantes reflètent le **cycle complet de traitement d'un bug**, incluant l'analyse, la correction, les tests, l'assurance qualité et la validation minimale en environnement contrôlé.

### Catégories de bugs

#### Bug simple
- Portée : correction évidente, typo, ajustement mineur sans impact systémique
- Temps humain estimé : **30 à 45 minutes**

#### Bug modéré
- Portée : logique métier, edge case, correction localisée avec validation fonctionnelle
- Temps humain estimé : **1,25 à 1,75 heures**

#### Bug complexe
- Portée : effets de bord, dette technique, refactor partiel ou impact transversal
- Temps humain estimé : **3 à 5 heures**

> Ces durées représentent des moyennes observées. Un bug inférieur à 30 minutes constitue une exception opérationnelle, non une catégorie.

### Taux horaires de référence (marché mondial)

Les taux ci-dessous correspondent à un **coût horaire moyen pondéré**, intégrant développement logiciel et assurance qualité, conformément aux pratiques du marché B2B international (SaaS, systèmes en production).

| Région | Taux horaire |
|--------|--------------|
| **Europe (EUR)** | 85 € / heure |
| **Canada (CAD)** | 120 $ CAD / heure |
| **États-Unis (USD)** | 95 $ USD / heure |

> Les montants sont volontairement alignés sur les standards régionaux de facturation, et non sur une simple conversion de devises.

### Logique de calcul du coût

```text
coût = temps_humain × taux_horaire_régional
```

## Assumptions

- Les valeurs par défaut pour les calculs de temps sont les moyennes des plages définies:
  - Bug simple: 37.5 minutes (moyenne de 30-45)
  - Bug modéré: 90 minutes (moyenne de 75-105)
  - Bug complexe: 240 minutes (moyenne de 180-300)
- Le taux horaire par défaut dépend de la région détectée via la locale système:
  - Europe: 85 € / heure
  - Canada: 120 $ CAD / heure
  - États-Unis: 95 $ USD / heure
  - Autre: 85 € / heure (défaut)
- Les statistiques sont persistées localement dans un fichier de cache

## Out of Scope

- Export des statistiques vers des formats externes (CSV, JSON)
- Statistiques par période (semaine, mois)
- Comparaison avec des projets précédents
- Dashboard web ou interface graphique
- Intégration avec des outils de reporting externes
- Stockage de la configuration → **Voir 006-persistent-config** (section `stats.*`)

## Config Integration (v3.0+)

À partir de v3.0, les options de stats seront configurables via `config.json`:

```json
{
  "stats": {
    "hourly_rate": null,
    "region": "auto",
    "currency": "auto",
    "heuristics": {
      "bug_simple_minutes": 37.5,
      "bug_moderate_minutes": 90,
      "bug_complex_minutes": 240
    }
  }
}
```

La hiérarchie: config.json local > config.json global > détaut régional
