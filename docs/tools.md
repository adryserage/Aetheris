# Tools

The server exposes six tools over stdio. Every tool returns one JSON object as text. A tool that fails raises an MCP tool error with a message, described under each tool below.

| Tool | Purpose |
| --- | --- |
| [`list_agents`](#list_agents) | List the agents and the presets |
| [`plan_review`](#plan_review) | Choose the files and the agents for a review |
| [`get_rules`](#get_rules) | Rules and playbooks of one agent |
| [`get_playbook`](#get_playbook) | Steps of one playbook with its attribution |
| [`run_checks`](#run_checks) | Run the deterministic checks of one agent |
| [`synthesize_report`](#synthesize_report) | Merge findings into one scored report |

## Finding

Checks, rules and the assistant share one finding shape. `get_rules` returns its JSON schema.

| Field | Type | Notes |
| --- | --- | --- |
| `agent` | agent id | Required |
| `severity` | `critical`, `high`, `medium`, `low` or `info` | Required |
| `message` | string | Required. Checks prefix it with the check name, such as `weak_crypto: ...` |
| `rule_id` | string or null | The rule the finding applies to, such as `SEC-006` |
| `file`, `line` | string, integer or null | Location, relative to the project root |
| `evidence` | string or null | The offending line. Secrets are masked |
| `source` | `check` or `assistant` | Default `check`. Findings the assistant writes use `assistant` |

Agent ids: `security`, `architecture`, `code_quality`, `metrics`, `dependency`, `qa_synthesis`, `type_safety`, `performance`, `api_contract`, `data_privacy`.

## list_agents

No arguments. Returns:

- `agents`: for each agent, `id`, `name`, `summary`, `rule_count`, `checks` (names) and `playbook_count`.
- `presets`: for each preset, a `description` and its `agents`.

The presets are `full`, `core`, `security-audit`, `performance-review`, `quick-scan`, `compliance-gdpr`, `compliance-hipaa`, `compliance-pci`, `type-safety` and `api-review`.

## plan_review

| Argument | Type | Default | Notes |
| --- | --- | --- | --- |
| `scope` | `diff`, `paths` or `repo` | `diff` | `diff`: files changed against `base` plus untracked files. `paths`: the given paths. `repo`: every source file |
| `paths` | list of strings | none | Required and non-empty when `scope` is `paths`. Files or directories inside the project root |
| `base` | string | `HEAD` | Git revision for the diff. Only used when `scope` is `diff` |
| `preset` | string | none | Name of a preset. Chooses the agents |
| `agents` | list of agent ids | none | Chooses the agents. Takes priority over `preset` |

Returns `root`, `scope`, `base` (null unless the scope is `diff`), `files`, `file_count`, `truncated`, `max_files`, `languages` (file count per language), `agents` and `next_steps`. Each entry of `agents` has an `id`, a `reason` and the `playbooks` that apply (each with `id`, `task` and `reason`).

Files are sorted with code files first, then dependency manifests, then other files. Without `agents` or `preset`, the agents come from the files:

- Any code file selects `security`, `code_quality`, `metrics`, `architecture`, `data_privacy` and `performance`.
- A manifest (`package.json`, `pubspec.yaml`, `requirements.txt` or `pyproject.toml`) adds `dependency`.
- TypeScript, Python or Java files add `type_safety`.
- A path containing `api`, `route`, `controller`, `endpoint` or `handler` adds `api_contract`.
- With no match, only `security` runs. `qa_synthesis` is always added last.

Limits and errors:

- At most 500 files (`max_files`). Past that, `truncated` is `true`.
- Files over 1 MiB, binary files, lock files, minified files and files excluded by `.gitignore` or by the default exclusions (such as `node_modules`, `.git`, `dist`, `build`, `vendor`) are skipped.
- A path outside the project root is refused.
- An unknown `preset`, `scope` `paths` without `paths`, a revision git rejects or a directory that is not a git repository raises an error.

## get_rules

| Argument | Type | Default | Notes |
| --- | --- | --- | --- |
| `agent` | agent id | required | |
| `language` | string | none | Lower-cased. Keeps rules and playbooks that name this language, plus those that apply to all languages |

Returns `agent`, `name`, `summary`, `language`, `rules`, `playbooks` and `finding_schema`. A rule has `id`, `title`, `severity`, `check` (what to look for) and, when set, `languages` and `references`. A playbook entry has `id`, `title`, `task`, `when`. An unknown agent raises an error.

## get_playbook

| Argument | Type | Notes |
| --- | --- | --- |
| `id` | string | A playbook id from `get_rules` or `plan_review` |

Returns `id`, `task`, `agents`, `steps` and `attribution` (`title`, `author`, `source`, `license`, `license_url`, `changes`). Any text you reproduce from `steps` must keep the attribution. An unknown id raises an error that lists the known ids.

## run_checks

| Argument | Type | Default | Notes |
| --- | --- | --- | --- |
| `agent` | agent id | required | |
| `paths` | list of strings | the whole repository | Files or directories inside the project root |

Returns `agent`, `checks` (names), `checked_files`, `findings`, `finding_count`, `errors` and `truncated`. For `qa_synthesis`, which has no checks, it also returns a `note`.

- `findings` is sorted by severity, then file, then line, and capped at 200. `finding_count` is the full count.
- `truncated` is `true` when more than 500 files were in scope or the findings were capped.
- A check that raises an error does not stop the others. Its message goes into `errors`. The `dependency` agent also reports there when the OSV service cannot be reached.
- `dependency` sends package names, ecosystems and versions to the OSV API. It looks up at most 500 packages, with a 15 second timeout per request. See [Security](security.md).

The checks of each agent are listed in [Agents](agents.md).

## synthesize_report

| Argument | Type | Notes |
| --- | --- | --- |
| `findings` | list of findings | All findings, from checks and from the assistant |

Returns:

- `total`: findings kept after deduplication.
- `duplicates_removed`: findings merged into another one. Two findings are the same when they share a file, a line and a rule (or, without a rule id, an agent and a message). The most severe one is kept.
- `score`: 100 minus 15 per critical, 8 per high, 3 per medium and 1 per low finding, never below 0. Info findings cost nothing.
- `by_severity`, `by_agent`: counts.
- `top_findings`: the 20 most severe findings.

The score only summarizes the findings you pass in.
