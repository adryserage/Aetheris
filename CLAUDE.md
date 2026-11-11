# Aetheris

## Projet

Serveur MCP open source (Apache 2.0) qui donne à l'assistant de code IA les règles de revue de 10 agents et des vérifications sans IA. Paquet PyPI `adryserage-aetheris`, projet Plane `AETHERIS`. La v4 est sur `develop` (AETHERIS-7) et n'est pas encore publiée. La dernière version sur PyPI est la 3.0.0, l'ancienne CLI.

## Commandes

- Installer : `pip install -e . pytest pytest-cov` (Python 3.10 ou plus)
- Lancer le serveur MCP (stdio) : `adryserage-aetheris` ou `python -m aetheris`, depuis le dossier du projet à relire, ou avec `AETHERIS_ROOT=<dossier>`. Depuis le dépôt sans installer : `uvx --from . adryserage-aetheris`.
- Tester : `pytest tests -q` (tests hors ligne, OSV simulé)
- Lint, comme la CI : `black --check --line-length 100 aetheris tests`, `isort --check-only --profile black aetheris tests`, `flake8 aetheris tests --max-line-length=100 --extend-ignore=E203,W503,E501,E402,F401`
- Types : `mypy aetheris --ignore-missing-imports`
- Construire : `python -m build` (wheel en pur Python)
- Doc : `mkdocs build --strict`

## Structure

- `aetheris/server.py` : le serveur MCP et ses cinq outils (`list_agents`, `plan_review`, `get_rules`, `run_checks`, `synthesize_report`).
- `aetheris/domain.py` : les types `Rule`, `Agent` et `Finding`, et les identifiants des 10 agents.
- `aetheris/rules/<agent>.yaml` : les règles de revue de chaque agent. `aetheris/registry.py` les charge, les valide et définit les préréglages.
- `aetheris/checks/` : les vérifications sans IA, un module par famille. `CHECK_NAMES` dans `checks/__init__.py` dit quel agent lance quoi.
- `aetheris/files.py` et `aetheris/changes.py` : choix des fichiers (`.gitignore`, exclusions, limite au dossier du projet) et diff git.
- `aetheris/synthesis.py` : la synthèse QA (dédoublonnage, tri, score).
- `tests/` : tests pytest du comportement de chaque outil.
- `docs/` : doc publiée sur GitHub Pages, encore celle de la 3.x (AETHERIS-14). `docs/archive/specs/` garde les specs des versions 2.5 à 3.0.0, hors du site.
- `.agents/product-marketing.md` : positionnement du produit.

## Services et déploiement

- Push sur `develop` : `promote.yml` lance le lint, les types et le build. Il ne fusionne rien.
- Étiquette `vX.Y.Z` poussée, ou lancement manuel : `release.yml` construit le sdist et le wheel, les publie sur PyPI par Trusted Publishing (sans jeton), crée la release GitHub et déploie la doc sur GitHub Pages. Un push sur `main` ne publie rien.
- `ci.yml` : lint, tests et types à chaque push ou PR qui touche `aetheris/`, `tests/` ou `pyproject.toml`.
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
