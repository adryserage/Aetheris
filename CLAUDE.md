# Aetheris

## Projet

Outil d'analyse de code par plusieurs agents d'IA (qualité, sécurité, architecture, dette technique), publié sur PyPI sous le nom `adryserage-aetheris`. Projet Plane `AETHERIS`. La v4 (AETHERIS-7) le transforme en serveur MCP open source qui n'appelle plus d'API d'IA.

## Commandes

- Installer : `pip install -e .` (Python 3.9 ou plus)
- Lancer : `aetheris --help`, puis `aetheris analysis`
- Tester : `pytest tests/` (les 3 fichiers couvrent seulement `src/runner/`)
- Lint, comme la CI : `black --check --line-length 100 src/ main.py`, `isort --check-only --profile black src/ main.py`, `flake8 src/ main.py --max-line-length=100 --extend-ignore=E203,W503,E501,E402,F401`
- Types : `mypy src/ --ignore-missing-imports` (lit `mypy.ini`)
- Construire : `python -m build`. `setup.py` compile les modules avec Cython.
- Doc : `mkdocs build --strict`

## Structure

- `src/cli.py` : CLI argparse, point d'entrée `aetheris` (`src.cli:main`).
- `src/agents/` : agents d'analyse, avec leurs prompts et leurs motifs.
- `src/core/` : analyseur, orchestrateur, fournisseurs d'IA, configuration.
- `src/services/` : secrets, dépendances, flux d'API, PR et issues GitHub.
- `src/runner/` : mode sans interface (`aetheris run`).
- `worker/` : webhook appelé par `aetheris-analysis.yml`, construit par `Dockerfile` et `railway.toml`.
- `docs/` : doc publiée sur GitHub Pages. `docs/archive/specs/` garde les specs des versions 2.5 à 3.0.0, hors du site.

## Services et déploiement

- Push sur `develop` : `promote.yml` lance le lint, les types et le build. Il ne fusionne rien.
- Étiquette `vX.Y.Z` poussée, ou lancement manuel : `release.yml` construit le paquet, le publie sur PyPI par Trusted Publishing (sans jeton), crée la release GitHub et déploie la doc sur GitHub Pages. Un push sur `main` ne publie rien.
- `ci.yml` : lint, tests et types à chaque push ou PR qui touche `src/`, `tests/` ou `pyproject.toml`.
- `scheduled.yml` : analyses planifiées. Le dépôt n'a plus de secret `GEMINI_API_KEY`, donc elles échouent tant qu'AETHERIS-5 ou AETHERIS-7 n'est pas livrée.
- Serveurs : voir `~/.claude/FLUX.md`.

## Règles du projet

- Pas de branche de fonctionnalité : le travail se fait sur `develop`, et on peut y pousser du travail en cours.
- Une release se décide : le propriétaire choisit le moment. Elle se fait en fusionnant `develop` dans `main`, puis en poussant l'étiquette `vX.Y.Z`. Rien ne publie tout seul.
- Chaque changement visible pour l'utilisateur ajoute sa ligne dans la section `[Unreleased]` de `CHANGELOG.md`, dans le même commit. `CHANGELOG.md` est l'historique des versions du dépôt (format Keep a Changelog, versionnage sémantique).
- À chaque release, la section `[Unreleased]` prend le numéro et la date de la version, et `pyproject.toml` et la feuille de route du `README.md` sont mis à jour. L'étiquette `vX.Y.Z` et la release GitHub suivent la règle globale. Une commande CLI ajoutée ou modifiée met à jour `docs/commands/`.
- Le dépôt n'a ni SpecKit ni skill propre : le travail suit les règles globales et Plane.
- Exception de langue, décidée par le propriétaire pour ce dépôt public : `README.md` est en anglais et `README.fr.md` en est la traduction. Toute modification de l'un se reporte dans l'autre. Les autres `.md` restent en français.
- `.agents/product-marketing.md` décrit le positionnement du produit. Les textes publics (README, description du paquet et du dépôt) le suivent : aucun chiffre ni promesse sans source.
- Lignes de 100 caractères au plus (black).
