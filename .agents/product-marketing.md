# Contexte marketing du produit

**Version du document :** v1
**Dernière mise à jour :** 2026-11-11

## Produit

**En une ligne :** des règles de revue de code et des vérifications fiables pour l'assistant de code IA, servies par un serveur MCP, sans clé d'API ni coût d'IA.
**Ce qu'il fait :** Aetheris est un serveur MCP open source. L'assistant (Claude Code, Cursor ou tout client MCP) l'appelle pour obtenir les règles d'une analyse (sécurité, performance, architecture, revue de PR, etc.) avec le format de sortie attendu, et pour lancer des vérifications qui ne dépendent pas de l'IA : secrets, vulnérabilités connues des dépendances (OSV), métriques, graphe de dépendances, flux d'API. C'est l'assistant qui choisit les outils et qui raisonne.
**Catégorie :** serveur MCP de revue de code et d'analyse statique.
**Type :** bibliothèque open source (Apache 2.0) publiée sur PyPI (`adryserage-aetheris`), lancée en local en stdio. Une instance hébergée tourne dans le MCP Hub d'Allowebs.
**Modèle :** gratuit et open source. Aucun service payant.

## Public visé

**Utilisateurs :** développeurs qui travaillent déjà avec un assistant de code IA et veulent des revues plus complètes et plus régulières.
**Cas d'usage principal :** faire relire un changement, une PR ou un dépôt par son assistant avec une grille de revue complète, au lieu d'un « relis mon code » improvisé.
**Tâches confiées :**
- Relire une PR avant de la fusionner, avec un avis clair et des problèmes classés par gravité.
- Faire un audit de sécurité : secrets exposés, dépendances vulnérables, failles OWASP.
- Repérer la dette technique d'un dépôt hérité (complexité, dépendances circulaires, code mort).

## Problème

**Problème central :** demandée sans cadre, une revue faite par un assistant dépend de la formulation du jour. Elle oublie des catégories entières (données personnelles, contrat d'API), ne vérifie pas les dépendances et rend un format différent à chaque fois.
**Limites des solutions actuelles :**
- Les services de revue par IA facturent l'usage ou le siège, et le code part chez un tiers.
- Les outils d'analyse statique produisent beaucoup d'alertes, que l'assistant ne sait pas trier.
- Aetheris 3.x envoyait le code à une API d'IA payante, avec une clé à gérer.

## Concurrence

**Directe :** les serveurs MCP d'outils d'analyse statique (Semgrep, SonarQube). Ils fournissent des résultats de règles, sans grille de revue pour l'assistant.
**Secondaire :** les services de revue de PR par IA (CodeRabbit et autres). Payants, et le code passe par leur modèle.
**Indirecte :** les commandes de revue intégrées aux assistants, ou un prompt écrit à la main. Le résultat varie, et rien ne vérifie les dépendances ni les secrets.

## Différence

- Aucune clé d'API et aucun coût d'IA : l'assistant de l'utilisateur fait le raisonnement.
- En local, le code ne quitte pas la machine. Seuls les noms et les versions de paquets partent vers OSV.
- Les règles et les vérifications sont réunies au même endroit, avec un format de sortie fixe d'une revue à l'autre.
- Open source : on peut lire, corriger et enrichir les règles par une PR.

## Objections

| Objection | Réponse |
|-----------|---------|
| « Mon assistant sait déjà faire une revue. » | Il la fait mieux avec une grille complète et des vérifications réelles (CVE, secrets), au lieu de ce qu'il devine. |
| « Encore un outil à installer. » | Une ligne de configuration MCP, lancée par `uvx`, sans compte ni clé. |
| « Les règles sont-elles fiables ? » | Elles sont publiques et versionnées, et chacun peut les corriger par une PR. |

**Hors cible :** les équipes qui veulent un service hébergé et clés en main, sans assistant IA dans leur flux de travail.

## Langage

**Mots à utiliser :** règles de revue, vérifications, serveur MCP, assistant, sans clé d'API, open source.
**Mots à éviter :** « qui marche vraiment », « l'IA qui voit ce que les humains ratent », « comme un développeur senior », tout chiffre de gain ou de coût sans source.
**Glossaire :**
| Terme | Sens |
|-------|------|
| Catégorie de règles | Un domaine de revue : sécurité, performance, typage, données personnelles, contrat d'API, revue de code, architecture, QA, revue de PR, parcours utilisateur |
| Vérification | Un outil qui ne dépend pas de l'IA et rend un résultat reproductible |

## Ton

| Attribut | Veut dire | Ne veut pas dire |
|----------|-----------|------------------|
| Sobre | Dire ce que fait l'outil, avec des exemples réels | Slogans, promesses de gain |
| Précis | Noms d'outils, commandes exactes, limites dites | Jargon pour faire sérieux |
| Ouvert | Inviter à contribuer, dire ce qui manque | Faux enthousiasme communautaire |

## Preuves

**Chiffres :** aucun pour l'instant. Le README 3.x citait des réductions de coût et des résultats de démo sans source : ne pas les reprendre.
**Historique :** 46 versions publiées sur PyPI, de 1.0.0 à 3.0.0 (54 étiquettes git, chacune avec sa release GitHub).

## Objectifs

**Objectif :** que des développeurs installent Aetheris dans leur assistant et contribuent aux règles.
**Action visée :** ajouter le serveur à son client MCP (`uvx adryserage-aetheris`).

## Apprentissages

*Décisions et leçons testées, la plus récente en premier.*
| Date | Apprentissage | Preuve | S'applique à | Statut |
|------|---------------|--------|--------------|--------|
| 2026-11-11 | Passage de CLI à API d'IA payante vers serveur MCP open source sans clé | Décision du propriétaire (AETHERIS-7) | Tous les textes | actif |

## Journal

*Le plus récent en premier.*
- v1 (2026-11-11) : contexte initial, écrit pour la v4 (serveur MCP open source).
