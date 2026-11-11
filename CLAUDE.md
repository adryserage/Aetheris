# Aetheris

## Projet

Serveur MCP open source (Apache 2.0) qui donne à l'assistant de code IA les règles de revue de 10 agents et des vérifications sans IA. Paquet PyPI `adryserage-aetheris`, projet Plane `AETHERIS`. La v4 est en construction (AETHERIS-7, étapes AETHERIS-9 à AETHERIS-15). La dernière version publiée est la 3.0.0, l'ancienne CLI.

## Commandes

- Installer : `pip install -e .` (Python 3.9 ou plus)
- Lint, comme la CI : `black --check --line-length 100 src/`, `isort --check-only --profile black src/`, `flake8 src/ --max-line-length=100 --extend-ignore=E203,W503,E501,E402,F401`
- Types : `mypy src/ --ignore-missing-imports` (lit `mypy.ini`)
- Construire : `python -m build` (wheel en pur Python)
- Doc : `mkdocs build --strict`

## Structure

- `src/services/` et `src/config/` : la logique sans IA gardée pour la v4 (secrets, dépendances, exports, flux d'API, impact, exclusions).
- `src/core/` : sélection et priorité des fichiers, catégories et préréglages des agents.
- `src/agents/` : le code des 10 agents de la 3.x. Il ne s'importe plus et sert de matière pour les règles (AETHERIS-12) et les vérifications (AETHERIS-13).
- `src/models/` : dataclasses et schémas Pydantic des rapports.
- `config/presets.json` : ensembles d'agents prédéfinis.
- `docs/` : doc publiée sur GitHub Pages, encore celle de la 3.x. `docs/archive/specs/` garde les specs des versions 2.5 à 3.0.0, hors du site.
- `.agents/product-marketing.md` : positionnement du produit.

## Services et déploiement

- Push sur `develop` : `promote.yml` lance le lint, les types et le build. Il ne fusionne rien.
- Étiquette `vX.Y.Z` poussée, ou lancement manuel : `release.yml` construit le sdist et le wheel, les publie sur PyPI par Trusted Publishing (sans jeton), crée la release GitHub et déploie la doc sur GitHub Pages. Un push sur `main` ne publie rien.
- `ci.yml` : lint, tests et types à chaque push ou PR qui touche `src/`, `tests/` ou `pyproject.toml`.
- `scheduled.yml` : graphique des téléchargements PyPI chaque jour (commit sur `main`), scan de sécurité chaque dimanche.
- Serveurs : voir `~/.claude/FLUX.md`.

## Règles du projet

- Pas de branche de fonctionnalité : le travail se fait sur `develop`, et on peut y pousser du travail en cours.
- Une release se décide : le propriétaire choisit le moment. Elle se fait en fusionnant `develop` dans `main`, puis en poussant l'étiquette `vX.Y.Z`. Rien ne publie tout seul.
- Chaque changement visible pour l'utilisateur ajoute sa ligne dans la section `[Unreleased]` de `CHANGELOG.md`, dans le même commit. `CHANGELOG.md` est l'historique des versions du dépôt (format Keep a Changelog, versionnage sémantique).
- À chaque release, la section `[Unreleased]` prend le numéro et la date de la version, et `pyproject.toml` est mis à jour. L'étiquette `vX.Y.Z` et la release GitHub suivent la règle globale.
- Le dépôt n'a ni SpecKit ni skill propre : le travail suit les règles globales et Plane.
- Exception de langue, décidée par le propriétaire pour ce dépôt public : `README.md` est en anglais et `README.fr.md` en est la traduction. Toute modification de l'un se reporte dans l'autre. Les autres `.md` restent en français.
- `.agents/product-marketing.md` décrit le positionnement du produit. Les textes publics (README, description du paquet et du dépôt) le suivent : aucun chiffre ni promesse sans source.
- Aucun appel à une API d'IA. En mode local, le seul appel réseau va à OSV, et le serveur ne lit que les fichiers sous le dossier du projet.
- Lignes de 100 caractères au plus (black).
