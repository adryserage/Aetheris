# Aetheris

## Projet

Serveur MCP open source (Apache 2.0) qui donne à l'assistant de code IA les règles de revue de 10 agents et des vérifications sans IA. Paquet PyPI `adryserage-aetheris`, projet Plane `AETHERIS`. La version 4.0.0 remplace la CLI de la 3.x.

## Commandes

- Installer : `pip install -e . pytest pytest-cov` (Python 3.10 ou plus)
- Installer le serveur dans les clients : `aetheris install` (Claude Code, Cursor, Claude Desktop ; `--client`, `--project`), `aetheris uninstall` pour le retirer.
- Lancer le mode hébergé (HTTP) : `aetheris serve --http`, avec `AETHERIS_BASE_PUBLIQUE`, `OAUTH_EMETTEUR`, `AETHERIS_HOTES_AUTORISES` et `MCP_TOKEN` (32 caractères au moins), plus `PORT`, `SENTRY_DSN` en option. Image : `docker build -t aetheris-hosted .`. Le client envoie le contenu des fichiers, rien n'est lu sur le disque.
- Lancer le serveur MCP (stdio) : `adryserage-aetheris` ou `python -m aetheris`, depuis le dossier du projet à relire, ou avec `AETHERIS_ROOT=<dossier>`. Depuis le dépôt sans installer : `uvx --from . adryserage-aetheris`.
- Tester : `pytest tests -q` (tests hors ligne, OSV simulé)
- Lint, comme la CI : `black --check --line-length 100 aetheris tests scripts`, `isort --check-only --profile black aetheris tests scripts`, `flake8 aetheris tests scripts --max-line-length=100 --extend-ignore=E203,W503,E501,E402,F401`
- Types : `mypy aetheris --ignore-missing-imports`
- Construire : `python -m build` (wheel en pur Python)
- Doc : `mkdocs build --strict`

## Structure

- `aetheris/server.py` : le serveur MCP et ses six outils (`list_agents`, `plan_review`, `get_rules`, `run_checks`, `get_playbook`, `synthesize_report`).
- `aetheris/playbooks/trailofbits/` : 7 méthodes de revue adaptées des Trail of Bits Skills, sous CC BY-SA 4.0 (licence dans le dossier, mention dans `NOTICE`). Chaque fichier porte en en-tête sa source au SHA près, son auteur et ses modifications. Une adaptation ne reprend que des phrases de la source, et reste sous CC BY-SA.
- `aetheris/hosted.py` : le mode HTTP (configuration, vérification des jetons comme CV Builder du MCP Hub, métadonnées OAuth, `/sante`, garde des hôtes, limite de taille). `aetheris/files.py:check_label` et `CheckContext.from_contents` font tourner les vérifications sur du contenu fourni, sans disque.
- `aetheris/cli.py` : la commande `aetheris` (installation dans les clients, message de migration pour les anciennes commandes 3.x, qui sortent avec le code 2).
- `aetheris/domain.py` : les types `Rule`, `Agent` et `Finding`, et les identifiants des 10 agents.
- `aetheris/rules/<agent>.yaml` : les règles de revue de chaque agent. `aetheris/registry.py` les charge, les valide et définit les préréglages.
- `aetheris/checks/` : les vérifications sans IA, un module par famille. `CHECK_NAMES` dans `checks/__init__.py` dit quel agent lance quoi, et `RULE_IDS` dans `checks/base.py` relie chaque motif à sa règle. Tout résultat passe par `make_finding`.
- `aetheris/files.py` et `aetheris/changes.py` : choix des fichiers (`.gitignore`, exclusions, limite au dossier du projet) et diff git.
- `aetheris/synthesis.py` : la synthèse QA (dédoublonnage, tri, score).
- `tests/` : tests pytest du comportement de chaque outil.
- `docs/` : doc v4 publiée sur GitHub Pages à chaque release (installation, déroulé de revue, outils, agents, playbooks, sécurité, migration). `docs/rules/` est généré à partir des règles par `scripts/gen_rules_docs.py` : après toute modification d'une règle, relancer le script, sinon `tests/test_docs.py` échoue. `docs/assets/diagrams/` contient les schémas du README, produits par `scripts/gen_diagrams.py` (à relancer quand les agents, les règles ou les outils changent). `docs/archive/specs/` garde les specs des versions 2.5 à 3.0.0, hors du site.
- `.agents/product-marketing.md` : positionnement du produit.

## Services et déploiement

- `ci.yml` : à chaque push sur `develop` ou `main`, à chaque PR et au lancement manuel. Lint et mypy en Python 3.10, tests de 3.10 à 3.13, build avec `twine check`, puis installation du wheel dans un venv vide (`aetheris --version`, démarrage du serveur).
- `release.yml` : seulement sur une étiquette `vX.Y.Z` poussée, ou au lancement manuel avec une étiquette. Le job `guard` refuse une étiquette différente de la version de `pyproject.toml`. Ensuite : build, publication sur PyPI par Trusted Publishing (environnement `pypi`, sans jeton), release GitHub avec les notes tirées de `CHANGELOG.md` par `scripts/extract_release_notes.py`, qui échoue si la section manque et ajoute un avertissement quand elle contient « Changements incompatibles », et déploiement de la doc sur GitHub Pages. Un push sur `main` ne publie rien.
- `scheduled.yml` : chaque dimanche, `pip-audit` sur le projet et `bandit` sur `aetheris/`.
- Dependabot vise `develop`, pour `pip` et `github-actions`.
- Les actions sont épinglées par SHA de commit, avec l'étiquette en commentaire. Chaque job a des permissions minimales et `persist-credentials: false`.
- Serveurs : voir `~/.claude/FLUX.md`.

## Règles du projet

- Pas de branche de fonctionnalité : le travail se fait sur `develop`, et on peut y pousser du travail en cours.
- Une release se décide : le propriétaire choisit le moment. Elle se fait en fusionnant `develop` dans `main`, puis en poussant l'étiquette `vX.Y.Z`. Rien ne publie tout seul.
- Chaque changement visible pour l'utilisateur ajoute sa ligne dans la section `[Unreleased]` de `CHANGELOG.md`, dans le même commit. `CHANGELOG.md` est l'historique des versions du dépôt (format Keep a Changelog, versionnage sémantique).
- À chaque release, la section `[Unreleased]` prend le numéro et la date de la version, et `pyproject.toml` est mis à jour. L'étiquette `vX.Y.Z` et la release GitHub suivent la règle globale.
- Le dépôt n'a ni SpecKit ni skill propre : le travail suit les règles globales et Plane.
- Exception de langue, décidée par le propriétaire pour ce dépôt public : les fichiers pour les contributeurs extérieurs sont en anglais (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/`, le site `docs/`). `README.fr.md` est la traduction du README, et toute modification de l'un se reporte dans l'autre. Les autres `.md` restent en français.
- `.agents/product-marketing.md` décrit le positionnement du produit. Les textes publics (README, description du paquet et du dépôt) le suivent : aucun chiffre ni promesse sans source.
- Aucun appel à une API d'IA. En mode local, le seul appel réseau va à OSV, et le serveur ne lit que les fichiers sous le dossier du projet.
- Lignes de 100 caractères au plus (black).
