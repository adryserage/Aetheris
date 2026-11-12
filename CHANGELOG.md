# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

### ✨ Nouvelles fonctionnalités

- Serveur MCP en stdio, lancé par `uvx adryserage-aetheris` ou `python -m aetheris`. Il expose cinq outils qui forment le déroulé de revue : `list_agents`, `plan_review`, `get_rules`, `run_checks` et `synthesize_report`.
- 10 agents portant 152 règles de revue, rangées en fichiers YAML dans `aetheris/rules/` : sécurité, architecture, qualité du code, métriques, dépendances, synthèse QA, typage, performance, contrat d'API, données personnelles.
- Vérifications sans IA : secrets masqués, vulnérabilités connues par OSV, métriques par fonction, imports circulaires, motifs de sécurité, de typage, de performance, d'API et de données personnelles (cartes validées par Luhn), points d'arrivée d'API orphelins.
- Lecture limitée au dossier du projet (`AETHERIS_ROOT` ou dossier courant). Le seul appel réseau va à OSV.
- Les règles ont été relues par un relecteur indépendant, avec les références vérifiées sur les sources officielles (MITRE CWE, OWASP, RGPD, RFC). 41 corrections : références mal appariées, affirmations techniques fausses, gravités alignées, méthode de synthèse QA cohérente avec le score. Les références OWASP Top 10 2025 sont ajoutées à côté des 2021. Ajout de 10 règles : vérification de signature ou de JWT absente, dépôt de fichier non contrôlé, opérations mémoire dangereuses (C, C++, Rust), pollution de prototype, limite d'essais sur l'authentification, comparaison de secret en temps non constant, injection d'en-tête ou de journal, entrée non fiable qui pilote un LLM avec outils, écriture destructrice sans garde-fou, action CI ou image non épinglée.
- Chaque résultat d'une vérification porte l'identifiant de sa règle (`rule_id`, par exemple SEC-001). La requête SQL construite par concaténation, `%`, `.format()`, f-string ou gabarit JavaScript est détectée.
- Commande `aetheris install` : ajoute le serveur MCP à Claude Code, Cursor et Claude Desktop, sans toucher aux autres serveurs déjà configurés. `aetheris uninstall` le retire, `aetheris serve` lance le serveur.

### 💥 Changements incompatibles

- Début de la v4 : Aetheris devient un serveur MCP et n'appelle plus aucune API d'IA. Les anciennes commandes (`aetheris analysis`, `fix`, `pr`, `issues`, `stats`, `run`…) affichent ce qui a changé et sortent avec le code 2. Retrait des commandes d'analyse de la CLI, de `main.py`, du mode interactif, des fournisseurs Gemini, OpenAI et Claude, de l'orchestrateur, du mode sans interface (`aetheris run`), de l'intégration Claude Code, des commandes GitHub (issues, PR, correctifs), des statistiques, de la traduction de la CLI, du client MCP, des skills, du worker Railway et de l'analyse des user stories. Pour garder la CLI : `pip install "adryserage-aetheris==3.0.0"`.
- Le paquet d'import `src` devient `aetheris`, publié en wheel pur Python. Fin de la compilation Cython. Le sdist contient de nouveau le code source.
- Dépendances réduites à `mcp`, `pydantic`, `pathspec`, `requests` et `pyyaml`. Python 3.10 ou plus.

### 🔒 Sécurité

- Retrait du code malveillant injecté dans `main.py` en mars 2026, y compris de l'historique git. Le paquet PyPI 3.0.0, publié avant l'attaque, ne le contient pas.
- Retrait des secrets `GEMINI_API_KEY` et `PYPI_API_TOKEN` du dépôt GitHub. La publication sur PyPI passe par Trusted Publishing, sans jeton.

### 🔧 Modifications

- Licence : Aetheris passe sous licence Apache 2.0, avec un fichier `NOTICE`. Elle remplace la licence propriétaire.
- Les specs des versions 2.5 à 3.0.0 sont archivées dans `docs/archive/specs/`, hors du site de documentation.
- Retrait de l'outillage inutilisé : `.serena/`, `.specify/` et les commandes SpecKit, `docs-dev/`, `generate_bugs_cache.py`, `scripts/analyze_changes.py` et `scripts/create_missing_releases.py`.
- Les releases ne partent plus toutes seules. `promote.yml` ne fusionne plus `develop` dans `main`, et `release.yml` ne publie que sur une étiquette `vX.Y.Z` ou un lancement manuel, plus à chaque push sur `main`.
- GitHub Actions remis à niveau. Un seul `ci.yml` (lint, mypy, tests de Python 3.10 à 3.13, build, test d'installation du wheel) remplace `ci.yml` et `promote.yml`. `release.yml` refuse une étiquette qui ne correspond pas à la version du paquet, et les notes de release avertissent les utilisateurs de la 3.x. Les actions sont épinglées par SHA, avec des permissions minimales, et Dependabot vise `develop`. Retrait du graphique des téléchargements, qui échouait chaque jour.
- `scheduled.yml` ne commite plus les rapports générés, qui restent disponibles comme artefacts des exécutions. Git ignore désormais `docs/analyses/` et `docs/metrics/`.

### 📝 Documentation

- README réécrit pour la v4 (serveur MCP), en anglais, avec une traduction française dans `README.fr.md`. Retrait du sondage, des prix et des chiffres sans source. Les descriptions du paquet, du site de doc et du dépôt GitHub sont alignées sur la v4.
- `CLAUDE.md` réécrit en français, réduit à l'état actuel du dépôt.

## [3.0.0] - 2026-01-12

### ✨ Nouvelles fonctionnalités

- **Interactive CLI Mode** : Interface REPL avec `aetheris --cli` ou `aetheris -c`
  - Prompt interactif avec indication du provider courant `aetheris[gemini]>`
  - Commandes intégrées : `/analysis`, `/fix`, `/pr`, `/issues`, `/stats`, `/help`, `/exit`
  - Commandes spécifiques par provider (Claude: `/commit`, `/review` ; Gemini: `/chat`, `/code`)
  - Historique des commandes persistant entre sessions
  - Support Ctrl+C pour interruption gracieuse

- **Command Autocomplete** : Autocomplétion intelligente des commandes
  - Tab completion pour commandes et arguments
  - Suggestions basées sur la distance de Levenshtein pour commandes inconnues
  - Filtrage par provider courant
  - Complétion des chemins de fichiers

- **Skills System** : Système de compétences pour agents AI
  - 4 skills built-in : `read_file`, `write_file`, `search_files`, `execute_command`
  - Validation sandbox pour sécurité des fichiers (restriction au répertoire projet)
  - Confirmation utilisateur pour opérations dangereuses
  - Support async pour exécution non-bloquante

- **Provider Adapters** : Adaptateurs multi-providers
  - `ClaudeAdapter` : Format Claude Tool Use (`tool_use` / `tool_result`)
  - `GeminiAdapter` : Format Gemini Function Calling (`function_call` / `function_response`)
  - Interface commune `SkillAdapter` pour extensibilité

- **Conductor System** : Orchestration de tâches multi-étapes
  - `Planner` : Création de plans d'exécution via AI
  - `Executor` : Exécution de plans avec suivi de progression Rich
  - `CycleDetector` : Détection de boucles infinies via hash d'état
  - Support de dépendances entre étapes
  - Maximum 20 étapes par plan

- **MCP Integration** : Support du Model Context Protocol
  - `MCPClient` : Connexion JSON-RPC aux serveurs MCP
  - `MCPDiscovery` : Découverte automatique d'outils et ressources
  - `MCPToolBridge` : Conversion MCP tools → Aetheris Skills
  - Reconnexion automatique avec exponential backoff
  - Gestion des conflits avec skills built-in

- **Custom Skills** : Skills personnalisés via YAML
  - Définition de skills via fichiers YAML dans `aetheris-skills/`
  - Template de commande avec substitution de paramètres `{param}`
  - Support des types : string, integer, number, boolean, array
  - Validation des paramètres requis et valeurs enum

### 🔧 Modifications

- Nouvelle structure de modules :
  - `src/cli_interactive/` : Mode interactif CLI
  - `src/skills/` : Système de compétences
  - `src/skills/adapters/` : Adaptateurs multi-providers
  - `src/conductor/` : Orchestration multi-étapes
  - `src/mcp/` : Intégration MCP

- Nouveau fichier `src/cli_interactive/interactive.py` avec classe `InteractiveSession`
- Nouveau fichier `src/cli_interactive/command_registry.py` avec `CommandRegistry`
- Nouveau fichier `src/cli_interactive/autocomplete.py` avec `CommandCompleter`
- Nouveau fichier `src/skills/base_skill.py` avec `Skill`, `SkillParameter`, `SkillResult`
- Nouveau fichier `src/skills/file_skills.py` avec `ReadFileSkill`, `WriteFileSkill`, `SearchFilesSkill`
- Nouveau fichier `src/skills/shell_skill.py` avec `ExecuteCommandSkill`
- Nouveau fichier `src/skills/registry.py` avec `SkillRegistry`
- Nouveau fichier `src/skills/adapters/claude_adapter.py` avec `ClaudeAdapter`
- Nouveau fichier `src/skills/adapters/gemini_adapter.py` avec `GeminiAdapter`
- Nouveau fichier `src/conductor/planner.py` avec `Planner`, `ExecutionPlan`, `PlanStep`
- Nouveau fichier `src/conductor/executor.py` avec `Executor`, `ExecutionResult`
- Nouveau fichier `src/conductor/cycle_detector.py` avec `CycleDetector`
- Nouveau fichier `src/mcp/client.py` avec `MCPClient`
- Nouveau fichier `src/mcp/discovery.py` avec `MCPDiscovery`, `MCPTool`, `MCPResource`
- Nouveau fichier `src/mcp/skill_bridge.py` avec `MCPToolBridge`, `MCPSkill`

### 📝 Documentation

- Nouveau fichier `docs/cli-interactive.md` : Guide du mode interactif
- Nouveau fichier `docs/skills/README.md` : Vue d'ensemble du système de skills
- Nouveau fichier `docs/skills/builtin-skills.md` : Documentation des skills intégrés
- Nouveau fichier `docs/skills/custom-skills.md` : Guide de création de skills personnalisés
- Nouveau fichier `docs/mcp-integration.md` : Guide d'intégration MCP
- Mise à jour `README.md` avec fonctionnalités v3.0

### 📦 Dépendances

- Ajout `prompt_toolkit>=3.0.0` pour interface interactive CLI

## [2.13.0] - 2026-01-12

### ✨ Nouvelles fonctionnalités

- **GitHub Actions Integration** : Template workflow complet pour CI/CD
  - Déclenchement automatique sur push vers main/develop
  - Déclenchement sur pull requests (opened, synchronized, reopened)
  - Déclenchement manuel avec options (mode, timeout, full_scan)
  - Détection automatique des fichiers modifiés pour analyse efficace
  - Commentaire automatique sur les PR avec résumé d'analyse
  - Upload des artefacts avec rétention de 30 jours

- **Scripts de Setup Local** : Scripts multiplateforme pour installation locale
  - `scripts/setup-local.sh` : Script Bash pour Linux/macOS
  - `scripts/setup-local.ps1` : Script PowerShell pour Windows
  - Vérification de Python 3.9+, installation Aetheris, check API key
  - Détection des résultats d'analyse existants

- **Documentation CI/CD** : Guide complet pour l'intégration GitHub Actions
  - Quick start en 3 étapes
  - Configuration des triggers et concurrency
  - Customisation des providers AI
  - Profiles de sécurité pour CI
  - Troubleshooting des erreurs courantes
  - Best practices pour différentes tailles de projets

### 🔧 Modifications

- Nouveau fichier `.github/workflows/aetheris-analysis.yml` avec workflow complet
- Nouveau fichier `scripts/setup-local.sh` pour setup Linux/macOS
- Nouveau fichier `scripts/setup-local.ps1` pour setup Windows
- Mise à jour de `docs/github-actions.md` avec documentation exhaustive
- Sécurisation des inputs workflow via variables d'environnement (anti-injection)

### 📝 Documentation

- Mise à jour du README.md avec section CI/CD Integration
- Mise à jour du roadmap (v2.13 marqué comme complété)

## [2.12.0] - 2026-01-12

### ✨ Nouvelles fonctionnalités

- **Safety Profiles System** : Trois profils de sécurité pour contrôler les limites d'exécution
  - `--profile safe` (défaut) : Réseau AI uniquement, limite de 500 lignes, 3 boucles de réparation max
  - `--profile ci` : Mode CI/CD avec fail-fast, audit logging, pas de prompts interactifs
  - `--profile yolo` : Accès réseau complet, limites étendues, nécessite confirmation explicite
  - `--yes` / `-y` : Ignorer la confirmation yolo

- **Command Allowlist** : Système de liste blanche pour le mode safe
  - Patterns glob pour correspondance flexible des commandes
  - Fichier `config/default_allowlist.json` avec commandes pré-approuvées
  - Support pour additions utilisateur via config.json
  - Blocage des commandes dangereuses (rm -rf, sudo, curl, etc.)

- **Network Guard** : Contrôle d'accès réseau pour le mode safe
  - Blocage des appels réseau auxiliaires (web search, etc.)
  - Autorisation des connexions AI providers (Gemini, OpenAI, Claude)
  - Autorisation des services essentiels (OSV, PyPI, npm)
  - Contexte manager pour activation/désactivation propre

- **Audit Logging** : Journalisation structurée pour le mode CI
  - Format JSON Lines (`aetheris-audit.jsonl`)
  - Événements: analysis_started, profile_applied, file_analyzed, etc.
  - Session ID unique pour chaque exécution
  - Détails des contraintes appliquées

- **Profile Constraints** : Limites d'exécution par profil
  - Limite de diff (lignes changées)
  - Limite de boucles de réparation
  - Fail-fast en mode CI (exit code non-zero)
  - Tests obligatoires en mode safe

### 🔧 Modifications

- Nouveau module `src/core/profiles.py` avec ProfileType, ProfileConfig, DiffBoundary
- Nouveau module `src/core/allowlist.py` avec AllowlistConfig, AllowlistGuard
- Nouveau module `src/core/audit_log.py` avec AuditLogger, AuditEvent
- Nouveau module `src/services/network_guard.py` avec NetworkGuard
- Nouveau fichier `config/default_allowlist.json` avec patterns autorisés
- Extension de `src/core/orchestrator.py` avec intégration des profils
- Extension de `src/cli.py` avec options --profile et --yes
- Extension de `src/core/__init__.py` avec exports des profils

### 📝 Documentation

- Section Safety Profiles ajoutée au README.md
- Mise à jour du roadmap (v2.9-v2.12 marqués comme complétés)

## [2.11.0] - 2026-01-12

### ✨ Nouvelles fonctionnalités

- **Agent Selection System** : Système complet de sélection d'agents pour analyses personnalisées
  - `--preset <name>` : Utilisation de presets prédéfinis (full, core, security-audit, etc.)
  - `--interactive` / `-i` : Mode interactif avec Rich UI pour sélection visuelle
  - `--category <name>` : Filtrage par catégorie de correctifs
  - `--list-presets` : Affichage de tous les presets disponibles

- **Presets System** : 10 presets d'analyse prédéfinis
  - `full` : Analyse complète avec les 10 agents
  - `core` : 6 agents principaux uniquement
  - `security-audit` : Focus sécurité (security, data_privacy, vulnerability)
  - `performance-review` : Focus performance (performance, metrics, architecture)
  - `quick-scan` : Analyse rapide (code_analysis, security)
  - `compliance-gdpr/hipaa/pci` : Presets de conformité
  - `type-safety` : Analyse de typage (type_safety, code_analysis)
  - `api-review` : Revue d'API (api_contract, security)

- **Interactive Agent Selection** : Interface Rich pour sélection interactive
  - Tableau des presets disponibles avec descriptions
  - Sélection manuelle agent par agent
  - Sélection des frameworks de conformité
  - Confirmation avant lancement de l'analyse

- **Fix Categories** : Catégories de correctifs pour ciblage
  - Filtrage des issues par catégorie
  - Suivi de progression par catégorie
  - Mapping agents → catégories

### 🔧 Modifications

- Nouveau module `src/core/presets.py` avec AgentPreset et système de presets
- Nouveau module `src/core/fix_categories.py` avec CategoryFilter et CategoryProgress
- Nouveau module `src/core/agent_selector.py` avec AgentSelector et validation
- Nouveau module `src/core/interactive_select.py` avec InteractiveAgentSelector
- Nouveau fichier `config/presets.json` avec définitions des presets
- Extension de `src/core/__init__.py` avec exports des nouveaux modules
- Extension de `src/cli.py` avec options --preset, --interactive, --category, --list-presets

### 📝 Documentation

- Documentation des presets dans CLI help
- Guide d'utilisation interactive intégré à l'interface Rich

## [2.10.0] - 2026-01-12

### ✨ Nouvelles fonctionnalités

- **Extended Agents** : 4 nouveaux agents d'analyse spécialisés
  - **TypeSafetyAgent** : Détection de `any`, casts unsafe, `type: ignore`, null safety
  - **PerformanceAnalysisAgent** : Détection O(n²), N+1 queries, memory leaks, blocking async
  - **APIContractAgent** : Violations REST, breaking changes, endpoints non documentés
  - **DataPrivacyAgent** : PII logging, chiffrement manquant, conformité GDPR/HIPAA/PCI-DSS/CCPA

- **Agent Selection CLI** : Nouvelles options de sélection d'agents
  - `--agents` : Liste des agents à exécuter (ex: `--agents security,performance`)
  - `--skip-agents` : Liste des agents à ignorer (ex: `--skip-agents privacy`)
  - `--compliance` : Frameworks de conformité pour analyse privacy (ex: `--compliance gdpr,hipaa`)

- **Configuration Extended Agents** : Nouveaux champs dans config.json
  - `analysis.compliance_agents` : Frameworks de conformité par défaut
  - `analysis.enabled_agents` : Agents activés par défaut
  - `analysis.skip_agents` : Agents désactivés par défaut

### 🔧 Modifications

- Nouveau module `src/agents/type_safety_agent.py`
- Nouveau module `src/agents/performance_analysis_agent.py`
- Nouveau module `src/agents/api_contract_agent.py`
- Nouveau module `src/agents/data_privacy_agent.py`
- Extension de `src/agents/__init__.py` avec exports des nouveaux agents
- Extension de `src/models/data_models.py` avec 4 nouveaux dataclasses:
  - `PerformanceIssue`, `APIContractViolation`, `TypeSafetyIssue`, `PrivacyViolation`
- Extension de `src/core/orchestrator.py` avec 4 nouvelles WorkflowStages
- Extension de `src/core/config.py` avec options pour extended agents
- Extension de `src/core/config_schema.py` avec `compliance_agents`
- Extension de `src/cli.py` avec options `--agents`, `--skip-agents`, `--compliance`

### 📝 Documentation

- Nouveaux agents documentés dans `src/agents/__init__.py`
- Options CLI documentées dans aide intégrée

## [2.9.0] - 2026-01-12

### ✨ Nouvelles fonctionnalités

- **Configuration Persistante** : Système de configuration hiérarchique complet
  - Nouveau fichier `config.json` pour configuration projet et globale
  - Hiérarchie de priorité : CLI > local > global > env > defaults
  - Nouvelle commande `aetheris init` pour initialiser config.json
  - Nouvelle commande `aetheris settings` pour UI interactive de configuration
  - Nouvelle commande `aetheris migrate-env` pour migrer .env vers config.json
  - Support des presets d'analyse personnalisés
  - Détection automatique des secrets dans config.json (avertissement)
  - Avertissement sur les clés de config inconnues (typos)

### 🔧 Modifications

- Nouveau module `src/core/config_schema.py` avec schéma de configuration
- Nouveau module `src/core/config_file.py` avec ConfigFile et ConfigHierarchy
- Nouveau module `src/core/settings_ui.py` avec interface Rich interactive
- Nouveau fichier `config/default.json` avec valeurs par défaut
- Extension de `src/core/__init__.py` pour exporter les nouveaux modules

### 📝 Documentation

- Schéma de configuration documenté dans config/default.json
- Aide CLI mise à jour avec nouvelles commandes

### 🔒 Sécurité

- Séparation stricte secrets (.env) vs config (config.json)
- Validation des clés secrètes avec avertissement si trouvées dans config.json

## [2.8.0] - 2026-01-11

### ✨ Nouvelles fonctionnalités

- **Mode Headless Déterministe** : Exécution non-interactive pour CI/CD
  - Nouvelle commande `aetheris run <task-file>` pour exécuter des tâches depuis JSON/YAML
  - Sortie JSON structurée avec schéma défini pour parsing automatisé
  - Profils de sécurité : safe, ci, dev, unrestricted
  - Support des signaux SIGINT/SIGTERM pour arrêt gracieux
  - Mode `--dry-run` pour validation sans exécution
  - Seed aléatoire (`--seed`) pour reproductibilité déterministe
  - Option `--no-timestamps` pour output comparables entre runs
  - Timeout configurable (`--timeout 30m`, `--timeout 2h`, `--timeout 0`)

### 🔧 Modifications

- Nouveau module `src/runner/` avec TaskRunner, TaskFileParser, OutputFormatter
- Nouveau module `src/schemas/` avec schémas JSON pour validation
- Exemples de fichiers de tâches dans `examples/tasks/`
- Intégration CLI avec `aetheris run` command

### 📝 Documentation

- Nouvelle documentation `docs/headless.md` avec guide complet
- Exemples d'intégration GitHub Actions et GitLab CI
- Schémas de fichiers de tâches et sorties documentés

### 📦 Dépendances

- Ajout de `jsonschema>=4.0` pour validation des fichiers de tâches

## [2.7.0] - 2026-01-10

### ✨ Nouvelles fonctionnalités

- **Internationalization (i18n)** : Support multilingue pour la CLI
  - Anglais (en) comme langue par défaut
  - Français (fr) entièrement traduit
  - Détection automatique de la langue du système (LANG, LC_ALL, LC_MESSAGES)
  - Variable d'environnement `AETHERIS_LANG` pour forcer la langue
  - Flag CLI `--lang` pour sélectionner la langue (ex: `aetheris --lang fr analysis`)
  - Flag CLI `--list-languages` pour afficher les langues disponibles
  - Traductions stockées dans `src/locales/*.json`
  - API développeur pour ajouter de nouvelles langues

### 🔧 Modifications

- Nouveau module `src/i18n/` avec support de traduction
- Fichiers de traduction JSON dans `src/locales/`
- Messages CLI (startup, analysis, errors) traduits en français
- Fallback automatique vers l'anglais si clé manquante

### 📝 Documentation

- Mise à jour README.md avec la fonctionnalité multi-langue
- Documentation de la configuration de langue dans docs/commands/README.md
- Ajout v2.7 dans la feuille de route

## [2.6.5] - 2026-01-09

### ✨ Nouvelles fonctionnalités

- **Commande `aetheris stats`** : Tableau de bord des statistiques d'analyse
  - Affichage des métriques agrégées (analyses, fichiers, issues)
  - Filtrage par période : `--period week|month|all`
  - Dashboard Rich avec tables et panneaux colorés

- **Calcul ROI automatique** : Estimation de l'impact business
  - Heures développeur économisées basées sur la sévérité des issues
  - Coût évité avec taux horaire configurable (défaut: $75/h)
  - Incidents de production évités (défaut: $5,000/incident)
  - Paramètres configurables via statistiques

- **Export multi-formats** : Génération de rapports
  - JSON : Export complet avec tous les détails
  - CSV : Données tabulaires pour spreadsheets
  - Markdown : Rapports lisibles pour documentation
  - Flag `--export json|csv|md` avec `--output` personnalisable

- **Statistiques par catégorie** : Breakdown détaillé
  - Issues par sévérité (critical, high, medium, low)
  - Issues par catégorie (security, performance, quality, debt)
  - Indicateurs de tendance (amélioration/régression)

- **Enregistrement automatique** : Suivi historique
  - Chaque analyse est automatiquement enregistrée
  - Stockage local JSON par projet (aetheris-stats.json)
  - Support du stockage global (~/.aetheris/statistics.json)

### 🔧 Modifications

- Nouveau module `src/models/stats_models.py` avec dataclasses de statistiques
- Nouveau service `src/services/statistics_service.py` avec logique ROI
- Configuration ROI dans `src/config/stats_config.py`
- Intégration CodeAnalyzer pour enregistrement automatique après analyse

## [2.6.2] - 2025-01-09

### ✨ Nouvelles fonctionnalités

- **Commande `aetheris cleanup`** : Nettoyage des artefacts de développement avant packaging
  - Mode `--dry-run` pour prévisualiser les fichiers à supprimer
  - Mode `--deep` pour inclure les répertoires de build (dist/, build/, *.egg-info/)
  - Patterns personnalisés via `--patterns`
  - Catégories nettoyées : sécurité (.env, *.pem), OS (.DS_Store), dev tooling (mypy.ini), tests

- **Commande `aetheris validate-package`** : Validation de sécurité pré-publication
  - Détection des fichiers exclus (secrets, configs dev, tests)
  - Scanner de secrets avec niveaux de confiance (HIGH/MEDIUM/LOW)
  - Validation de la taille du package
  - Mode `--fix` pour corriger automatiquement les problèmes
  - Support `.secretsignore` pour les faux positifs

- **Secret Scanner** : Détection multi-patterns des credentials exposés
  - AWS Access Keys et Secret Keys
  - GitHub Personal Access Tokens et OAuth tokens
  - Anthropic, OpenAI API keys
  - Stripe Live/Test keys
  - GCP, Azure credentials
  - Patterns génériques (api_key=, password=, secret=)
  - Scan parallèle avec ThreadPoolExecutor

- **Minification Python optionnelle** : Réduction de taille des fichiers Python
  - Suppression des commentaires
  - Suppression des docstrings
  - Preview de la réduction de taille

### 📦 Nouveaux modules

- `src/config/exclusion_patterns.py` : Patterns d'exclusion par catégorie
- `src/config/secret_patterns.py` : Patterns de détection de secrets
- `src/models/cleanup_models.py` : Dataclasses pour les opérations de cleanup
- `src/services/cleanup_service.py` : Service de nettoyage de fichiers
- `src/services/secret_scanner.py` : Scanner de secrets multi-patterns
- `src/services/package_validator.py` : Validateur de package pré-publication
- `src/services/minifier.py` : Minification optionnelle de code Python

### 🔧 Modifications

- **CLI** : Ajout des sous-commandes `cleanup` et `validate-package` (alias `validate`)
- **MANIFEST.in** : Mise à jour avec exclusions de sécurité complètes
- **GitHub Actions** : Correction du warning `python-version` dans dependency-submission

### 📝 Documentation

- Documentation complète de `aetheris cleanup` dans `docs/commands/cleanup.md`
- Documentation complète de `aetheris validate-package` dans `docs/commands/validate-package.md`
- Mise à jour de `docs/features.md` avec la section Package Security
- Mise à jour du README avec les nouvelles commandes et le roadmap
- Ajout de `.secretsignore.example` comme template

## [2.6.1] - 2025-01-08

### ✨ Nouvelles fonctionnalités

- **Gestion flexible du timeout** : Contrôle de la durée maximale d'analyse
  - Nouveau paramètre CLI `--timeout` / `-t`
  - Formats supportés : secondes (3600), minutes (30m), heures (2h), illimité (0)
  - Timeout par défaut : 60 minutes
  - Gestion gracieuse avec tentative de sauvegarde du contexte

- **Heartbeat Monitor** : Indicateur de progression pour analyses longues
  - Feedback périodique toutes les 10 minutes
  - Affiche le nombre de fichiers analysés et le temps écoulé
  - Empêche les timeouts silencieux sur les grandes bases de code

- **Flag `--reanalyze` / `-r`** : Analyse incrémentale des fichiers modifiés
  - Détecte les fichiers modifiés depuis la dernière analyse
  - Utilise git diff ou timestamps (fallback)
  - Détection automatique des fichiers supprimés
  - Compatible avec `--changed-files-only` et `--timeout`

### 📦 Nouveaux modules

- `src/core/heartbeat.py` : HeartbeatMonitor pour le feedback périodique
- `src/core/change_detector.py` : ChangeDetector pour la détection des modifications

### 🔧 Modifications

- **CLI** : Ajout des paramètres `--timeout`, `-t`, `--reanalyze`, `-r`
- **Orchestrateur** : Application du timeout global sur l'ensemble du workflow
- **Configuration** : Nouveau champ `timeout_seconds` dans AnalysisConfig

### 📝 Documentation

- Mise à jour du README avec documentation de l'analyse incrémentale
- Exemples d'utilisation du timeout et de la réanalyse

## [2.5.8] - 2025-01-07

> **Note** : Cette version consolide plusieurs améliorations mineures (v2.5.1-v2.5.7) publiées le même jour pour réduire la "release fatigue".

### 🔒 Sécurité

- **CRITIQUE : Désactivation du mode `--auto` par défaut** (CVE potentiel, CWE-94)
  - Le flag `--auto` de `aetheris fix` est maintenant désactivé par défaut
  - **Risque identifié** : Injection de prompt permettant l'exécution de code malveillant
  - **Vecteur d'attaque** : Code analysé contenant des instructions malveillantes pour l'agent IA
  - **Impact** : Exécution de code arbitraire, exfiltration de données sur la machine du développeur
  - **Mitigation** :
    - Validation humaine obligatoire pour toute modification générée par l'IA
    - Mode `--auto` requiert désormais le flag explicite `--i-accept-security-risks`
    - Documentation des risques ajoutée dans le CHANGELOG et la documentation
  - **Recommandation** : N'utilisez `--auto` que dans des environnements sandboxés (CI, containers éphémères)

- **Protection contre l'injection de prompt indirecte via Google Search** (BUG-7A1985E1, CWE-74)
  - **Risque identifié** : La fonctionnalité `enable_google_search` (v2.2.0) exposait l'application à des attaques par injection de prompt indirecte
  - **Vecteur d'attaque** : Contenu web malveillant ingéré lors des recherches Google pouvait manipuler le comportement de l'IA
  - **Impact** : Rapports d'analyse faussés, suggestions de code vulnérable, exfiltration potentielle de données
  - **Mitigation implémentée** :
    - Nouvelle méthode `_sanitize_web_content()` pour assainir tout contenu web récupéré
    - Filtrage des patterns d'injection de prompt courants ("ignore previous instructions", "system:", etc.)
    - Délimiteurs stricts (`<<<EXTERNAL_WEB_CONTENT_START>>>` / `<<<EXTERNAL_WEB_CONTENT_END>>>`) pour isoler les données externes
    - Instruction système de sécurité automatique dans `_build_config()` lorsque Google Search est activé
    - Limitation de la taille du contenu externe à 50KB (protection DoS)
  - **Fichiers modifiés** : `src/core/ai_providers.py`

### ✨ Nouvelles fonctionnalités

- **Sondage communautaire** : Ajout d'un sondage "Should Aetheris become Open Source?"
  - Badges SVG dynamiques dans le README avec vote en un clic
  - Page de sondage dédiée sur adryanserage.ca/poll/aetheris
  - Lien "Vote: Open Source?" ajouté sur la page PyPI

### 📦 Package

- **Métadonnées PyPI améliorées** : Sidebar PyPI enrichie
  - Ajout email auteur/mainteneur pour vérification
  - Ajout classifiers : License OSI MIT, OS, Topics AI/Security, Framework Pydantic
  - Ajout keywords : ai, llm, devops, ci-cd, vulnerability-scanner
  - Support langues : Anglais, Français

### 📝 Documentation

- **README amélioré** : Section Commands étendue avec tous les arguments CLI
  - Chaque commande inclut maintenant des exemples d'utilisation
  - Tables complètes de toutes les options disponibles
  - Liens vers la documentation détaillée de chaque commande
- **Statistiques de téléchargements** : Ajout de badges dans le README (pepy.tech)
- **Badges README** : Ajout de badges compatibles (PyPI status, black, mypy, platform)
- **Configuration recommandée** : Gemini pour l'analyse, Claude Code pour la correction
- **Correction du badge GitHub Actions** : URL corrigée vers le bon repository

## [2.5.0] - 2025-01-06

### ✨ Nouvelles fonctionnalités

- **Commande `aetheris issues`** : Création d'issues GitHub depuis les rapports d'analyse
  - Parse les rapports d'analyse dans `docs/analyses/`
  - Extrait les bugs et crée des issues GitHub pour chacun
  - Format de titre : `[BugType] in filename - description`
  - Sections dans le body : File, Bug Description, Issue Details, Recommended Solution, Code Context
  - Labels automatiques : `bug`, `aetheris-analysis`, niveau de sévérité
  - Options : `--dry-run`, `--labels`, `--assignee`, `--repo`, `--from-report`
  - Déduplication automatique par titre

- **Commande `aetheris pr-gen`** : Génération de PRs avec corrections AI
  - Génère des Pull Requests avec des corrections générées par AI pour chaque bug
  - Workflow : 1 bug = 1 PR avec fix AI
  - Création automatique de branches `fix/<file>-<bug-type>-<id>`
  - Linking automatique aux issues GitHub (`--link-issues`)
  - Options : `--dry-run`, `--base-branch`, `--from-report`, `--bug-index`, `--issue-number`
  - Corps de PR détaillé avec résumé, détails du bug, changements appliqués

> **⚠️ AVERTISSEMENT DE SÉCURITÉ - Supply Chain Risk**
>
> La commande `pr-gen` génère automatiquement des Pull Requests avec du code produit par IA. **Risques identifiés** :
>
> - **Supply Chain Attack** : Une analyse corrompue ou manipulée pourrait générer des PRs contenant du code malveillant
> - **Spam de repository** : Sans contrôle, la commande pourrait créer un grand nombre de PRs indésirables
> - **Injection de code vulnérable** : L'IA pourrait introduire des vulnérabilités non intentionnelles
>
> **Mitigations OBLIGATOIRES** :
>
> 1. **Permissions restrictives** : Le `GITHUB_TOKEN` utilisé doit avoir les permissions minimales (lecture seule par défaut)
> 2. **Approbation humaine requise** : Les PRs générées automatiquement **DOIVENT** nécessiter une revue et approbation explicite d'un mainteneur humain avant tout merge
> 3. **Protection de branche** : Activer les règles de protection sur les branches principales (require reviews, require status checks)
> 4. **Mode `--dry-run`** : Toujours utiliser `--dry-run` en premier pour prévisualiser les PRs avant création
> 5. **CI restreinte** : Ne pas exécuter de workflows CI avec permissions d'écriture sur les PRs automatiques non validées
>
> - **CWE-94** : Improper Control of Generation of Code ('Code Injection')
> - **OWASP** : LLM01:2023 - Prompt Injection, A08:2021 - Software and Data Integrity Failures

### 📝 Documentation

- **Restructuration complète de la documentation**
  - README condensé (~170 lignes vs ~1195) avec liens vers sous-documents
  - Nouvelle structure `docs/commands/` avec documentation individuelle par commande
  - `docs/installation.md` : Guide d'installation
  - `docs/configuration.md` : Référence des variables d'environnement
  - `docs/ai-providers.md` : Configuration des providers AI et pricing
  - `docs/agents.md` : Vue d'ensemble des agents d'analyse
  - `docs/features.md` : Documentation des fonctionnalités
  - `docs/github-actions.md` : Intégration CI/CD
  - `docs/troubleshooting.md` : Dépannage et erreurs courantes
  - Documentation des nouvelles commandes `issues` et `pr-gen`

### 📦 Nouveaux modules

- `src/services/issue_creator.py` : Service de création d'issues GitHub
  - `IssueCreator` : Classe principale pour créer des issues
  - `IssueOptions` : Dataclass pour les options de configuration
  - Parsing des rapports d'analyse markdown
  - Gestion du rate limiting GitHub

- `src/services/pr_generator.py` : Service de génération de PRs
  - `PRGenerator` : Classe principale pour générer des PRs avec fixes
  - `PROptions` : Dataclass pour les options de configuration
  - Génération de fixes AI via les providers configurés
  - Gestion des branches et commits automatiques

### 🔧 Modifications

- **CLI** : Ajout des sous-commandes `issues` et `pr-gen` (alias `generate-prs`)
- **Workflow** : Intégration complète avec GitHub CLI (`gh`)

## [2.4.0] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Commande `aetheris pr`** : Revue de Pull Requests GitHub avec AI
  - Support URL (`--url https://github.com/owner/repo/pull/123`)
  - Support repo + numéro (`--repo owner/repo --pr 123`)
  - Intégration complète avec GitHub CLI (`gh`)

- **Multi-Provider avec Consensus** : Analyse avec plusieurs providers AI
  - Support simultané de Gemini, Claude et OpenAI (`--providers gemini,claude,openai`)
  - Mode consensus (par défaut) : ne reporte que les issues trouvées par TOUS les providers
  - Matching intelligent des issues par fichier, type et proximité de ligne (±3 lignes)
  - Option `--no-consensus` pour reporter toutes les issues

- **Commentaires GitHub** : Publication directe sur les PRs
  - Commentaires inline sur les lignes spécifiques du diff
  - Commentaire résumé avec tableau des issues, score de risque et recommandation
  - Mode `--dry-run` pour prévisualiser sans poster
  - Option `--no-inline` pour résumé uniquement

- **Détection de propriété de PR** : Détection automatique si la PR vous appartient
  - Comparaison de l'email git local avec l'auteur de la PR
  - Comparaison du login GitHub authentifié
  - Option `--auto-fix` pour corriger avec Claude Code si c'est votre PR

- **Filtrage avancé** :
  - Filtrage par sévérité (`--severity critical|high|medium|low|info`)
  - Export du rapport en markdown (`--output report.md`)

- **Mode parallèle pour `aetheris fix`** : Correction de bugs en batch
  - Option `--batch-size` / `-b` pour définir le nombre de corrections simultanées
  - Pool de workers avec remplacement dynamique (quand un termine, le suivant démarre)
  - Option `--timeout` pour définir le timeout par bug
  - Gain de performance ~5x avec `--batch-size 10`
  - Barre de progression en temps réel pour toutes les corrections
  - **Détection de rate limit** : Arrêt automatique si limite Claude Code atteinte
    - Détection intelligente des messages de rate limit
    - Extraction du temps d'attente (heures/minutes)
    - Affichage du nombre de bugs corrigés et restants
    - Message clair pour reprendre plus tard

### 📦 Nouveaux modules

- `src/models/pr_models.py` : Modèles de données pour PR review
  - `PRInfo`, `PRFile`, `PRIssue`, `PRComment`, `PRReviewResult`
  - Enums `PRIssueSeverity`, `PRIssueType`, `PRFileStatus`

- `src/models/pr_schemas.py` : Schémas Pydantic pour Structured Outputs
  - `PRIssueSchema`, `PRAnalysisResultSchema`
  - Validation automatique des réponses AI

- `src/services/github_service.py` : Service GitHub via `gh` CLI
  - `parse_pr_url()` : Extraction repo/numéro depuis URL
  - `fetch_pr_info()` : Récupération métadonnées PR
  - `fetch_pr_diff()` : Récupération du diff
  - `fetch_pr_files()` : Liste des fichiers modifiés
  - `post_review_comment()` : Publication commentaire résumé
  - `post_inline_comment()` : Publication commentaire inline
  - `is_own_pr()` : Détection propriété PR

- `src/agents/pr_review_agent.py` : Agent de revue de PR
  - Support multi-provider avec analyse parallèle
  - Algorithme de consensus pour matching d'issues
  - Génération de commentaires inline et résumé
  - Intégration Claude Code pour auto-fix

### 🔧 Modifications

- **Configuration** : Nouvelles options PR dans `AnalysisConfig`
  - `pr_providers` : Liste des providers AI pour PR review
  - `pr_consensus_mode` : Activer le mode consensus
  - `pr_min_severity` : Sévérité minimale des issues
  - `pr_post_inline_comments` : Poster commentaires inline
  - `pr_auto_fix_own_pr` : Auto-fix si PR propre
  - `pr_dry_run` : Mode dry-run

- **CLI** : Ajout de la sous-commande `pr` (alias `review-pr`)
  - Arguments mutuellement exclusifs pour source PR
  - Validation des clés API selon providers sélectionnés

- **ClaudeCodeIntegration** : Nouvelles méthodes pour le mode parallèle
  - `_fix_bug_async()` : Correction asynchrone d'un bug
  - `run_fix_session_parallel()` : Session de correction avec pool de workers

- **CLI fix** : Nouveaux arguments
  - `--batch-size` / `-b` : Nombre de corrections parallèles
  - `--timeout` : Timeout par bug en secondes

### 📝 Documentation

- Mise à jour du README avec documentation complète de `aetheris pr`
- Description PyPI améliorée avec mots-clés PR review
- Statut de développement passé à "Production/Stable"

## [2.3.4] - 2025-01-05

### 🧹 Qualité de code

- **Lint & Formatting** : Nettoyage complet du codebase
  - Formatage Black appliqué sur tous les fichiers
  - Imports triés avec isort
  - Suppression des imports inutilisés (autoflake)
  - Correction des `bare except` → `except Exception`
  - Variables inutilisées supprimées
  - Renommage des variables ambiguës (`l` → `line`)

## [2.3.3] - 2025-01-05

### 🐛 Corrections

- **User Story Agent** : Corrige `AttributeError: 'ProgressManager' object has no attribute 'update_current_file'`
  - Remplace l'appel à `update_current_file` par `print` existant

## [2.3.2] - 2025-01-05

### 🐛 Corrections

- **Impact Analyzer** : Les champs `fixed`, `fixed_at`, `fix_summary` sont maintenant inclus dans le cache initial
  - Corrige l'incohérence entre le cache initial et le cache mis à jour après correction

## [2.3.1] - 2025-01-05

### ✨ Améliorations

- **Suivi des bugs corrigés** : Les bugs corrigés sont maintenant marqués dans le cache
  - Nouveau champ `fixed: boolean` dans `BugIdentifier`
  - Champ `fixed_at` avec timestamp de la correction
  - Champ `fix_summary` avec résumé de la correction appliquée
  - Les bugs déjà corrigés sont automatiquement ignorés lors des prochaines sessions
  - Le cache `.bugs_cache.json` est mis à jour après chaque correction réussie
  - Message d'info indiquant le nombre de bugs déjà corrigés

## [2.3.0] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **User Story Analysis** : Nouvelle commande `aetheris user-story` pour analyser les flux utilisateur
  - Trace les appels frontend ↔ backend bidirectionnels
  - Détecte les endpoints orphelins (définis mais jamais appelés)
  - Détecte les appels API sans handler correspondant
  - Analyse les incohérences logiques et les problèmes potentiels
  - Génère des diagrammes Mermaid et PlantUML
  - Supporte plusieurs modes d'entrée :
    - `--text "description"` : Depuis une description textuelle
    - `--file user-stories.md` : Depuis un fichier markdown
    - `--entry LoginButton.tsx` : Depuis un point d'entrée code
    - `--auto` : Auto-détection de tous les flux
  - Sortie en markdown, JSON ou les deux

- **Nouveaux modèles et services** :
  - `FlowTracer` : Détection agnostique des appels API (JS/TS, Dart, Python)
  - `UserStoryParser` : Parsing de user stories depuis texte, markdown, Gherkin
  - `UserStoryAnalysisAgent` : Agent IA pour l'analyse des flux
  - `DiagramGenerator` : Génération de diagrammes de séquence et flowcharts

- **Détection multi-framework** :
  - Frontend : fetch, axios, dio, requests, httpx, aiohttp
  - Backend : Express, Next.js, FastAPI, Flask, Django, NestJS

- **Types de problèmes détectés** :
  - `orphan_endpoint` : Endpoint défini mais jamais appelé
  - `missing_handler` : Appel API sans endpoint correspondant
  - `missing_error_handling` : Appel API sans gestion d'erreur
  - `race_condition` : Appels concurrents sur même state
  - `missing_auth` : Endpoint sensible sans authentification
  - `dead_code` : Code jamais exécuté dans le flux

## [2.2.8] - 2025-01-05

### 🐛 Corrections

- **Correction du mode direct Claude Code** : Ajout des flags manquants pour le mode non-interactif
  - Ajout de `--print` pour le mode non-interactif
  - Ajout de `--output-format text` pour la sortie texte
  - Ajout de `--no-session-persistence` pour éviter les problèmes de session
  - Résout le timeout de 300s qui se produisait en mode arrière-plan

- **Nouvelle méthode `test_claude_code_execution()`** : Test complet de l'exécution
  - Teste que Claude Code peut réellement exécuter des prompts
  - Utilisé par `aetheris fix --test`

## [2.2.7] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Flag `--version`** : Affichage de la version avec `aetheris --version` ou `aetheris -v`

- **Mode direct pour Claude Code** : Exécution en arrière-plan (sans fenêtre terminal)
  - Nouvelle méthode `run_claude_direct()` pour exécution directe
  - Nouvelle méthode `test_claude_code()` pour vérifier la connexion
  - Nouvelle méthode `fix_bug_direct()` pour correction sans fenêtre
  - Mode direct par défaut (plus fiable que le mode terminal)
  - **⚠️ AVERTISSEMENT SÉCURITÉ CRITIQUE** : Ce mode exécute des commandes sans supervision visuelle, amplifiant le risque d'injection de prompt lorsque combiné avec `--auto`. **Le mode `--auto` est DÉSACTIVÉ par défaut depuis v2.5.8.** Voir l'avertissement complet dans v2.1.0 et la mitigation dans v2.5.8 (CWE-94, OWASP LLM01:2023).

- **Flag `--test` pour Claude Code** : Test de connexion avant correction
  - `aetheris fix --test` vérifie si Claude Code fonctionne
  - Affiche la version et effectue un test de communication

- **Flag `--terminal` pour Claude Code** : Mode fenêtre terminal optionnel
  - `aetheris fix --terminal` ouvre Claude Code dans une nouvelle fenêtre
  - Utile pour le débogage interactif

### 🐛 Corrections

- **Correction du terminal vide sur Windows** : Le mode direct évite les problèmes d'échappement

## [2.2.6] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Mode direct pour Claude Code (initial)** : Première implémentation du mode arrière-plan
- **Workflow publish avec workflow_dispatch** : Permet le déclenchement manuel de la publication

## [2.2.5] - 2025-01-05

### 🐛 Corrections

- **Correction severity 'info' dans impact analyzer** : Ajout de la clé 'info' manquante
  - Résout l'erreur `KeyError: 'info'` dans l'analyse d'impact
  - Les issues de sécurité de niveau 'info' sont maintenant correctement traitées

## [2.2.4] - 2025-01-05

### 🐛 Corrections

- **Correction du parser .env** : Les commentaires inline sont maintenant ignorés
  - `API_KEY=abc123  # commentaire` fonctionne correctement
  - Résout l'erreur "API key not valid" causée par les commentaires

- **Validation de la clé API au démarrage** : Test automatique de la clé
  - Affichage de la clé masquée pour debug
  - Message d'erreur clair si la clé est invalide
  - Arrêt immédiat au lieu de continuer avec des erreurs

## [2.2.3] - 2025-01-05

### 🔧 Modifications

- **Modèle Gemini par défaut** : Confirmation de `gemini-3-pro-preview` comme modèle par défaut
  - Validation que le modèle est bien disponible et fonctionnel
  - Alignement avec la documentation officielle Gemini

## [2.2.1] - 2025-01-05

### 🐛 Corrections

- **Correction du SDK google-genai** : Mise à jour des imports dans CLI et main.py
  - Changement de `import google.generativeai` vers `from google import genai`
  - Alignement avec le nouveau SDK google-genai>=1.0.0

- **Options de configuration v2.2.0** : Les nouvelles options Gemini sont maintenant passées à AnalysisConfig
  - `ENABLE_STRUCTURED_OUTPUTS`, `ENABLE_THINKING`, `ENABLE_CODE_EXECUTION`, etc.
  - Documentation des incompatibilités dans `.env.example`

- **Exclusion des fichiers cachés** : Les fichiers commençant par `.` sont maintenant exclus de l'analyse
  - Respect des règles `.gitignore`
  - Meilleure performance et pertinence des analyses

### 📚 Documentation

- Mise à jour de `.env.example` avec les incompatibilités entre fonctionnalités Gemini
- Ajout de `ENABLE_GOOGLE_SEARCH` comme option de configuration

## [2.2.0] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Migration vers le nouveau SDK google-genai** : Passage de `google-generativeai` à `google-genai>=1.0.0`
  - Nouvelle architecture client-based (`genai.Client`)
  - API plus moderne et performante
  - Support des dernières fonctionnalités Gemini

- **Modèle par défaut Gemini 3 Pro Preview** : `gemini-3-pro-preview`
  - Input: 1,048,576 tokens
  - Output: 65,536 tokens
  - Support de toutes les fonctionnalités avancées

- **Structured Outputs (Sorties structurées)** : Réponses JSON garanties via schémas Pydantic
  - Nouvelle méthode `generate_structured()` dans GeminiProvider
  - Nouvelle méthode `_call_ai_structured()` dans BaseAgent
  - Schémas Pydantic dans `src/models/analysis_schemas.py`
  - Validation automatique des réponses

- **Code Execution (Exécution de code)** : Le modèle peut exécuter du Python en sandbox
  - Nouvelle méthode `generate_with_code_execution()`
  - Nouvelle méthode `_call_ai_with_code_execution()` dans BaseAgent
  - Analyse dynamique avec parsing AST, calcul de métriques, etc.

> **⚠️ AVERTISSEMENT DE SÉCURITÉ — Code Execution** (BUG-4BFA242A)
>
> L'exécution de code est **strictement confinée côté serveur** dans le sandbox de l'API Google Gemini.
>
> **Garanties de sécurité** :
> - ❌ **Aucune exécution locale** : Aetheris n'exécute JAMAIS de code Python généré par le modèle sur la machine locale
> - ✅ **Sandbox distant uniquement** : Tout code est exécuté dans l'environnement isolé de Google
> - ✅ **Résultats informatifs uniquement** : Les résultats d'exécution sont utilisés exclusivement pour enrichir les rapports d'analyse
> - ❌ **Aucune action automatique** : Les résultats ne déclenchent aucune modification de fichier, exécution de commande ou décision logique automatisée dans l'application locale
>
> **Risques résiduels** :
> - Si le sandbox de Google Gemini était compromis (hors de notre contrôle), des résultats malveillants pourraient être inclus dans les rapports
> - **Mitigation** : Les rapports générés doivent être revus par un humain avant toute action basée sur leur contenu
>
> **CWE-94** : Improper Control of Generation of Code ('Code Injection') — Risque mitigé par confinement serveur

- **Thinking/Reasoning (Raisonnement)** : Affichage du processus de raisonnement du modèle
  - Nouvelle méthode `generate_with_thinking()`
  - Nouvelle méthode `_call_ai_with_thinking()` dans BaseAgent
  - Budget de tokens configurable (`thinking_budget`)

- **Context Caching (Cache de contexte)** : Réduction des coûts API (~50%)
  - Nouvelle méthode `create_cache()` pour créer des caches
  - Nouvelle méthode `generate_with_cache()` pour utiliser les caches
  - TTL configurable (`cache_ttl_seconds`)

- **Batch API (API Batch)** : Traitement en lot à coût réduit (-50%)
  - Nouvelle méthode `create_batch_job()` pour créer des jobs batch
  - Mode batch activable via configuration

- **Function Calling (Appel de fonction)** : Appel automatique de fonctions Python
  - Nouvelle méthode `generate_with_tools()` avec fonctions Python
  - Support des outils personnalisés

- **Google Search (Recherche web intégrée)** : Grounding avec recherche web
  - Nouvelle méthode `generate_with_search()` pour recherche en temps réel

### 🔧 Modifications

- **Configuration** : Nouvelles options dans `AnalysisConfig`
  - `enable_code_execution` : Activer l'exécution de code
  - `enable_structured_outputs` : Activer les sorties structurées (défaut: true)
  - `enable_function_calling` : Activer l'appel de fonctions
  - `enable_thinking` : Activer le mode thinking
  - `thinking_budget` : Budget de tokens pour le raisonnement
  - `enable_context_caching` : Activer le cache de contexte
  - `cache_ttl_seconds` : Durée de vie du cache API
  - `enable_batch_mode` : Activer le mode batch
  - `enable_google_search` : Activer la recherche Google intégrée

- **BaseAgent** : Nouvelles méthodes pour les fonctionnalités avancées
  - `_call_ai_structured()` pour les sorties structurées
  - `_call_ai_with_thinking()` pour le raisonnement visible
  - `_call_ai_with_code_execution()` pour l'exécution de code

- **SecurityAnalysisAgent** : Utilisation des Structured Outputs
  - Analyse de sécurité avec schémas Pydantic validés
  - Champs CWE et OWASP enrichis

- **CodeAnalysisExpert** : Nouvelles méthodes avancées
  - `analyze_file_structured()` avec Structured Outputs
  - `analyze_with_code_execution()` pour analyses dynamiques

- **SecurityIssue (data_models)** : Nouveaux champs
  - `cwe_id` : Identifiant CWE (ex: CWE-79)
  - `owasp_category` : Catégorie OWASP (ex: A01:2021)

### 📦 Nouveaux modules

- `src/core/gemini_config.py` : Configuration des fonctionnalités avancées Gemini
  - `GeminiFeatureConfig` : Configuration par requête
  - `CodeExecutionResult` : Résultat d'exécution de code
  - `ThinkingResult` : Résultat avec raisonnement
  - `CacheConfig` : Configuration du cache
  - `BatchRequest/BatchJobInfo` : Gestion des jobs batch
  - Helpers : `supports_code_execution()`, `supports_thinking()`, etc.

- `src/models/analysis_schemas.py` : Schémas Pydantic pour Structured Outputs
  - `Severity`, `IssueCategory` : Enums pour les issues
  - `SecurityIssue`, `SecurityAnalysisResult` : Analyse de sécurité
  - `CodeMetrics`, `CodeIssue`, `Dependency` : Métriques et issues
  - `FileAnalysisResult` : Résultat complet d'analyse
  - `ArchitecturePattern`, `LayerAnalysis`, `ArchitectureAnalysisResult` : Architecture
  - `QualityDimension`, `QualityAssuranceResult` : Qualité
  - `VulnerabilityInfo`, `DependencyVulnerabilityResult` : Vulnérabilités

### 📦 Dépendances

- `google-genai>=1.0.0` remplace `google-generativeai>=0.8.5`
- `pydantic>=2.0.0` pour les schémas structurés

### 📝 Documentation

- Mise à jour du README avec les nouvelles fonctionnalités Gemini
- Exemples d'utilisation des Structured Outputs
- Documentation des méthodes avancées

## [2.1.0] - 2025-01-05

### ✨ Nouvelles fonctionnalités

- **Commande `aetheris fix`** : Nouvelle commande CLI pour corriger les bugs détectés avec Claude Code
  - Lance Claude Code dans une fenêtre séparée pour chaque bug
  - Correction séquentielle avec confirmation utilisateur
  - Filtrage par sévérité (`--severity critical|high|medium|low`)
  - ~~Mode automatique (`--auto`) sans confirmations entre les bugs~~ **⚠️ DÉSACTIVÉ (voir avertissement sécurité ci-dessous)**
  - Détection automatique et support multi-plateforme (Windows, macOS, Linux)

> **⚠️ AVERTISSEMENT DE SÉCURITÉ CRITIQUE**
>
> Le mode `--auto` est **DÉSACTIVÉ par défaut** depuis v2.5.8 en raison d'un risque de sécurité critique :
>
> - **Risque** : Injection de prompt (Prompt Injection) - Un attaquant peut insérer des instructions malveillantes dans le code analysé pour forcer l'agent IA à générer et exécuter du code destructeur ou exfiltrer des données.
> - **Vecteur** : Combinaison du mode `--auto` avec l'exécution en arrière-plan de Claude Code (v2.2.7).
> - **Mitigation** :
>   - Le mode `--auto` requiert maintenant le flag explicite `--i-accept-security-risks`
>   - Validation humaine obligatoire par défaut pour toute modification de fichier
>   - Utilisez `--auto` uniquement dans des environnements sandboxés/éphémères (CI, containers)
> - **CWE-94** : Improper Control of Generation of Code ('Code Injection')
> - **OWASP** : LLM01:2023 - Prompt Injection

- **Extraction des exports** : Analyse des exports de chaque fichier pour comprendre les relations
  - Support TypeScript/JavaScript (export default, export {}, export function/class)
  - Support Python (__all__, fonctions/classes publiques)
  - Support Dart (export, classes/fonctions publiques)

- **Graphe de dépendances inverse** : Savoir "qui dépend de ce fichier"
  - Construction automatique du graphe inverse
  - Méthode `get_dependents()` pour trouver les fichiers impactés
  - Profondeur configurable

- **Analyse d'impact des bugs** : Calcul automatique des fichiers impactés par chaque bug
  - IDs de bugs uniques au format `BUG-XXXXXXXX`
  - Extraction des bugs depuis les analyses (sécurité, risques, incohérences)
  - Cache des bugs dans `.bugs_cache.json`

### 🔧 Modifications

- **Orchestrateur** : Ajout de 3 nouveaux stages de workflow
  - `EXPORT_ANALYSIS` : Extraction des exports
  - `REVERSE_DEPENDENCY` : Construction du graphe inverse
  - `IMPACT_ANALYSIS` : Analyse d'impact des bugs

- **Configuration** : Nouvelles options
  - `enable_export_analysis` : Activer l'extraction des exports
  - `enable_reverse_dependency` : Activer le graphe de dépendances inverses
  - `enable_impact_analysis` : Activer l'analyse d'impact
  - `max_impact_depth` : Profondeur maximale pour l'analyse d'impact
  - `enable_claude_code_fix` : Activer l'intégration Claude Code
  - `fix_severity_threshold` : Seuil de sévérité minimale pour les corrections

### 📦 Nouveaux modules

- `src/services/export_analyzer.py` : Extraction des exports multi-langage
- `src/services/impact_analyzer.py` : Analyse d'impact des bugs
- `src/services/claude_code_integration.py` : Intégration avec Claude Code CLI

### 📝 Documentation

- Mise à jour du README avec documentation complète de `aetheris fix`
- Mise à jour de `docs/PLUGINS.md` avec les nouveaux hooks
- Exemples d'utilisation des nouveaux stages

## [2.0.1] - 2025-01-04

### 🔧 Corrections

- **Migration de dépendance** : Remplacement de `duckduckgo-search` par `ddgs` (package renommé)
- **Correction modèle Gemini** : Changement du modèle par défaut de `gemini-1.5-flash` vers `gemini-1.5-pro` pour compatibilité avec l'API v1beta
- **Mise à jour dépendances** : `google-generativeai>=0.8.5` pour meilleur support des modèles récents

### 📦 Dépendances

- `ddgs>=1.0.0` remplace `duckduckgo-search>=6.0.0`
- `google-generativeai>=0.8.5` (au lieu de >=0.8.0)

## [2.0.0] - 2025-01-04

### ✨ Nouvelles fonctionnalités

- **Orchestrateur dédié** : Système d'orchestration séparé pour une meilleure maintenabilité et testabilité
- **Système de cache** : Cache basé sur git SHA + timestamp pour réduire les coûts API de 60-80%
- **Parallélisation intelligente** : Analyse des fichiers indépendants en parallèle basée sur le graphe de dépendances
- **Système de priorités** : Priorisation automatique des fichiers modifiés dans les PR (HIGH) et leurs dépendances (MEDIUM)
- **Métriques et monitoring** : Collecte complète de métriques de performance avec export JSON
- **Analyse incrémentale améliorée** : Détection automatique des fichiers dépendants avec profondeur configurable
- **Gestion d'erreurs améliorée** : Circuit breaker et backoff exponentiel pour une meilleure résilience

### 🔧 Modifications

- **Architecture** : Refactorisation de `CodeAnalyzer` pour utiliser un orchestrateur interne
- **Workflow** : Système de workflow avec étapes, dépendances et hooks
- **Configuration** : Nouvelles options (`enable_cache`, `cache_ttl_days`, `analyze_dependent_files`, `max_dependency_depth`, `enable_metrics`, `enable_priority_analysis`)
- **BaseAgent** : Intégration du circuit breaker pour éviter les appels répétés en cas d'erreur
- **Orchestrateur** : Support des hooks pour extensibilité et collecte de métriques

### 📦 Nouveaux modules

- `src/core/orchestrator.py` : Orchestrateur principal avec système de workflow
- `src/core/cache.py` : Système de cache avec stockage disque
- `src/core/error_handler.py` : Gestion d'erreurs avec circuit breaker
- `src/core/parallel_analyzer.py` : Parallélisation intelligente basée sur dépendances
- `src/core/priority_manager.py` : Gestionnaire de priorités pour PR reviews
- `src/core/metrics.py` : Collecteur de métriques de performance

### 📝 Documentation

- Documentation complète du système de plugins/hooks dans `docs/PLUGINS.md`
- Exemples d'utilisation et guide pour créer des plugins personnalisés

### 🔄 Compatibilité

- **Backward compatible** : L'API publique de `CodeAnalyzer` reste inchangée
- Les nouvelles fonctionnalités sont activées par défaut mais peuvent être désactivées via configuration

## [1.1.0] - 2025-01-03

### ✨ Nouvelles fonctionnalités

- **Affichage du reasoning** : Possibilité d'afficher le processus de raisonnement des modèles AI (si disponible)
- **Support OpenAI o1** : Support du reasoning pour les modèles o1-preview et o1-mini d'OpenAI
- **Panneau de reasoning** : Affichage du reasoning dans un panneau Rich dédié avec syntax highlighting

### 🔧 Modifications

- **AIProvider** : Ajout de la méthode `generate_content_with_reasoning()` pour récupérer le reasoning
- **BaseAgent** : Ajout de `_call_ai_with_reasoning()` pour utiliser le reasoning si activé
- **Configuration** : Ajout de l'option `show_reasoning` dans `AnalysisConfig`
- **Agents** : Passage de `progress_manager` aux agents pour afficher le reasoning

### 📝 Documentation

- Mise à jour du README avec explication du reasoning
- Ajout de la variable d'environnement `SHOW_REASONING` dans la documentation

## [1.0.9] - 2025-01-02

### ✨ Nouvelles fonctionnalités

- **Barre de progression moderne** : Ajout d'une barre de progression interactive avec Rich pour un suivi visuel clair de l'analyse
- **Affichage en temps réel** : Progression détaillée pour chaque étape (scan, analyse, rapports)
- **Statistiques visuelles** : Affichage du temps écoulé, temps restant et pourcentage de progression

### 🔧 Modifications

- **CodeAnalyzer** : Intégration de `ProgressManager` pour remplacer les logs simples par des barres de progression
- **Points d'entrée** : `main.py` et `src/cli.py` créent automatiquement un `ProgressManager` si le terminal le supporte
- **Fallback automatique** : Si Rich n'est pas disponible ou si on n'est pas dans un terminal interactif, le système utilise les logs simples

### 📦 Dépendances

- Ajout de `rich>=13.0.0` pour les barres de progression modernes

### 📝 Documentation

- Mise à jour du README avec description de la barre de progression

## [1.0.8] - 2025-01-01

### ✨ Nouvelles fonctionnalités

- **Support multi-fournisseurs AI** : Ajout du support pour OpenAI, Claude (Anthropic) et Gemini
- **Choix du modèle** : Possibilité de choisir le modèle AI selon le fournisseur sélectionné
- **Abstraction des providers** : Architecture modulaire permettant d'ajouter facilement de nouveaux fournisseurs AI
- **Documentation des coûts** : Ajout d'un tableau détaillé des coûts d'analyse dans le README
- **Modèles à jour** : Mise à jour avec les derniers modèles disponibles (Gemini 2.5 Pro, GPT-4o, Claude 3.5 Sonnet)

### 🔧 Modifications

- **Configuration** : Remplacement de `gemini_api_key` et `gemini_model` par `ai_api_key` et `ai_model` génériques
- **Variables d'environnement** : Ajout de `AI_PROVIDER` pour choisir le fournisseur (gemini, openai, claude)
- **BaseAgent** : Refactorisation pour utiliser l'abstraction `AIProvider` au lieu de Gemini directement
- **CodeGenerator** : Adaptation pour utiliser l'abstraction `AIProvider`

### 📦 Dépendances

- Ajout de `openai>=1.0.0` pour le support OpenAI
- Ajout de `anthropic>=0.25.0` pour le support Claude

### 📝 Documentation

- Ajout de la section "Choix du fournisseur AI" dans le README
- Ajout du tableau des modèles supportés par fournisseur
- Ajout de la section "Coûts d'analyse" avec estimations pour différents scénarios
- Mise à jour des instructions de configuration pour les différents fournisseurs

### 🔄 Compatibilité

- **Breaking change** : Les variables `GEMINI_API_KEY` et `GEMINI_MODEL` sont remplacées par `AI_PROVIDER`, `AI_API_KEY` (selon provider) et `AI_MODEL`
- Pour la rétrocompatibilité, si `AI_PROVIDER` n'est pas défini, le système utilise Gemini par défaut

## [1.0.7] - 2024-11-21

### 🔧 Corrections et améliorations

- **Dépendance obligatoire** : `ddgs` (anciennement `duckduckgo-search`) est maintenant une dépendance obligatoire au lieu d'optionnelle
- **Simplification du code** : Suppression des vérifications conditionnelles pour `ddgs` dans tout le codebase
- **Amélioration des imports** : Simplification des imports dans `main.py` et `src/cli.py` avec gestion d'erreur unifiée
- **Suppression des avertissements inutiles** : L'avertissement pour `ddgs` ne s'affiche plus si la recherche web est désactivée dans la configuration

### 📦 Dépendances

- `ddgs>=1.0.0` (anciennement `duckduckgo-search>=6.0.0`) déplacé des dépendances optionnelles vers les dépendances principales dans `pyproject.toml` et `requirements.txt`

### 📝 Documentation

- Mise à jour du README pour indiquer que `ddgs` est une dépendance obligatoire

## [1.0.6] - 2024-11-21

### 🔧 Corrections et améliorations

- **Workflows manuels uniquement** : Les workflows `code-review.yml` et `run-aetheris.yml` ne s'exécutent maintenant que manuellement
- **Installation PyPI** : Le workflow `run-aetheris.yml` utilise maintenant PyPI au lieu de GitHub Packages
- **Documentation** : Mise à jour complète de README, CHANGELOG, .gitignore, .gitattributes et scripts
- **Correction URLs** : Correction des URLs du repository dans pyproject.toml
- **Amélioration .gitignore** : Ajout des fichiers de packaging Python (build/, dist/, \*.egg-info, etc.)
- **Amélioration .gitattributes** : Ajout des règles de fin de ligne pour différents types de fichiers

### 📝 Documentation

- Mise à jour du README avec les liens PyPI et repository GitHub
- Documentation améliorée des scripts utilitaires
- CHANGELOG mis à jour avec toutes les versions

## [1.0.5] - 2024-11-21

### 🚀 Publication sur PyPI

- **Publication sur PyPI** : Le package est maintenant disponible sur PyPI (Python Package Index)
- **Installation simplifiée** : Plus besoin de `--extra-index-url`, installez simplement avec `pip install adryserage-aetheris`
- Correction du workflow de publication (suppression de GitHub Packages avec URL incorrecte)
- Workflow GitHub Actions mis à jour pour publier uniquement sur PyPI

### 📦 Package

- Nom du package : `adryserage-aetheris`
- Commande CLI : `aetheris` (inchangée)
- Installation : `pip install adryserage-aetheris` (depuis PyPI)

## [1.0.4] - 2024-11-21

### 🔧 Corrections

- Ajout du support PyPI dans le workflow de publication
- Configuration du token PyPI comme secret GitHub
- Mise à jour des workflows avec les dernières versions des actions GitHub (checkout@v4, setup-python@v5)

## [1.0.3] - 2024-11-21

### 🚀 Publication

- Renommage du package Python en `adryserage-aetheris` pour publication
- Configuration complète du package avec `pyproject.toml`
- Ajout de la commande CLI `aetheris` avec sous-commandes (`aetheris analysis`)
- Workflow GitHub Actions pour publication automatique lors des tags de version
- Documentation mise à jour avec instructions d'installation

## [1.0.2] - 2024-11-21

### 🔧 Corrections

- Correction de la commande `gh pr diff` qui utilisait des flags invalides (`--json` et `--jq` non supportés)
- Remplacement par `gh pr view` avec filtrage approprié pour exclure les fichiers supprimés
- Alignement du comportement entre les modes PR et commit pour exclure les fichiers supprimés (cohérence avec `git diff --diff-filter=ACMR`)

## [1.0.1] - 2024-11-21

### 🔧 Corrections

- Correction du workflow GitHub Actions pour utiliser `gh pr view` au lieu de `gh pr diff` pour récupérer les fichiers modifiés dans les pull requests

## [1.0.0] - 2024-11-21

### ✨ Fonctionnalités

- Ajout du support pour analyser uniquement les fichiers modifiés dans le Code Analyzer
- Support des analyses ciblées pour les Pull Requests et commits
- Mode `--changed-files-only` avec support des fichiers spécifiés via arguments ou variables d'environnement
- Support du numéro de PR pour enrichir les rapports d'analyse

### 📚 Documentation

- Documentation complète du système dans le README.md
- Instructions d'installation et de configuration détaillées
- Guide d'utilisation avec exemples
- Documentation des agents d'analyse et de leurs fonctionnalités

### 🏗️ Infrastructure

- Workflow GitHub Actions pour l'analyse automatique de code
- Support des analyses complètes et ciblées
- Génération automatique de rapports en tant qu'artifacts GitHub

### 🎉 Version initiale

- Système d'analyse de code multi-agents avec 6 agents spécialisés :
  - Code Analysis Expert (CAE)
  - Architect Analysis Agent (AAA)
  - Security Analysis Agent (SSA)
  - Code Metrics Agent (CMA)
  - Dependency Vulnerability Agent (DVA)
  - Quality Assurance Agent (QAA)
- Support de multiples langages de programmation
- Analyse des vulnérabilités via l'API OSV
- Génération de rapports détaillés en Markdown
- Configuration flexible via variables d'environnement

[Unreleased]: https://github.com/adryserage/aetheris/compare/v2.12.0...HEAD
[2.12.0]: https://github.com/adryserage/aetheris/compare/v2.11.0...v2.12.0
[2.11.0]: https://github.com/adryserage/aetheris/compare/v2.10.0...v2.11.0
[2.10.0]: https://github.com/adryserage/aetheris/compare/v2.9.0...v2.10.0
[2.9.0]: https://github.com/adryserage/aetheris/compare/v2.8.0...v2.9.0
[2.8.0]: https://github.com/adryserage/aetheris/compare/v2.7.0...v2.8.0
[2.7.0]: https://github.com/adryserage/aetheris/compare/v2.6.5...v2.7.0
[2.6.5]: https://github.com/adryserage/aetheris/compare/v2.6.2...v2.6.5
[2.6.2]: https://github.com/adryserage/aetheris/compare/v2.6.1...v2.6.2
[2.6.1]: https://github.com/adryserage/aetheris/compare/v2.5.8...v2.6.1
[2.5.8]: https://github.com/adryserage/aetheris/compare/v2.5.0...v2.5.8
[2.5.0]: https://github.com/adryserage/aetheris/compare/v2.4.0...v2.5.0
[2.4.0]: https://github.com/adryserage/aetheris/compare/v2.3.4...v2.4.0
[2.3.4]: https://github.com/adryserage/aetheris/compare/v2.3.3...v2.3.4
[2.3.3]: https://github.com/adryserage/aetheris/compare/v2.3.2...v2.3.3
[2.3.2]: https://github.com/adryserage/aetheris/compare/v2.3.1...v2.3.2
[2.3.1]: https://github.com/adryserage/aetheris/compare/v2.3.0...v2.3.1
[2.3.0]: https://github.com/adryserage/aetheris/compare/v2.2.8...v2.3.0
[2.2.8]: https://github.com/adryserage/aetheris/compare/v2.2.7...v2.2.8
[2.2.7]: https://github.com/adryserage/aetheris/compare/v2.2.6...v2.2.7
[2.2.6]: https://github.com/adryserage/aetheris/compare/v2.2.5...v2.2.6
[2.2.5]: https://github.com/adryserage/aetheris/compare/v2.2.4...v2.2.5
[2.2.4]: https://github.com/adryserage/aetheris/compare/v2.2.3...v2.2.4
[2.2.3]: https://github.com/adryserage/aetheris/compare/v2.2.1...v2.2.3
[2.2.1]: https://github.com/adryserage/aetheris/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/adryserage/aetheris/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/adryserage/aetheris/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/adryserage/aetheris/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/adryserage/aetheris/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/adryserage/aetheris/compare/v1.0.9...v1.1.0
[1.0.9]: https://github.com/adryserage/aetheris/compare/v1.0.8...v1.0.9
[1.0.8]: https://github.com/adryserage/aetheris/compare/v1.0.7...v1.0.8
[1.0.7]: https://github.com/adryserage/aetheris/compare/v1.0.6...v1.0.7
[1.0.6]: https://github.com/adryserage/aetheris/compare/v1.0.5...v1.0.6
[1.0.5]: https://github.com/adryserage/aetheris/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/adryserage/aetheris/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/adryserage/aetheris/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/adryserage/aetheris/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/adryserage/aetheris/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/adryserage/aetheris/releases/tag/v1.0.0
