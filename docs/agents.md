# Agents

An agent is a group of review rules with the deterministic checks that go with them. There are 10. `get_rules` returns an agent's rules, `run_checks` runs its checks, and `plan_review` chooses which agents to run. The full rule texts are in the [rules reference](rules/index.md).

A check scans text and reports findings with the id of the rule it applies to. Checks are heuristics: your assistant confirms each match by reading the code. A rule without a check, and an agent without checks, are reviewed by the assistant reading the files.

| Agent | Rules | Checks | Playbooks |
| --- | --- | --- | --- |
| [`security`](rules/security.md) | 28 | `secret_scan`, `security_patterns` | 6 |
| [`architecture`](rules/architecture.md) | 14 | `circular_imports` | 0 |
| [`code_quality`](rules/code_quality.md) | 17 | `metric_thresholds`, `duplicate_blocks` | 0 |
| [`metrics`](rules/metrics.md) | 9 | `file_metrics` | 0 |
| [`dependency`](rules/dependency.md) | 12 | `manifest_parse`, `osv_lookup` | 1 |
| [`qa_synthesis`](rules/qa_synthesis.md) | 14 | none | 2 |
| [`type_safety`](rules/type_safety.md) | 14 | `type_patterns` | 0 |
| [`performance`](rules/performance.md) | 14 | `performance_patterns` | 0 |
| [`api_contract`](rules/api_contract.md) | 15 | `api_patterns`, `orphan_endpoints` | 1 |
| [`data_privacy`](rules/data_privacy.md) | 15 | `pii_patterns` | 1 |

## What each check reports

Each finding message starts with a finding name. When a rule is listed, the finding carries its id.

| Agent and check | Finding names (rule) |
| --- | --- |
| `security` / `secret_scan` | Provider keys and tokens, private key headers and similar secrets (SEC-005). Values are masked in the evidence. High confidence matches are `critical`, the others `medium` |
| `security` / `security_patterns` | `sql_injection` (SEC-001), `xss` (SEC-003), `dynamic_eval` (SEC-004), `weak_crypto` (SEC-006), `insecure_random` (SEC-008) |
| `architecture` / `circular_imports` | `circular_imports` (ARC-001) for Python, JavaScript and TypeScript |
| `code_quality` / `metric_thresholds` | `complexity` (CQ-004, above 15), `nesting` (CQ-005, above 4), `function_length` (CQ-006, above 80 lines) |
| `code_quality` / `duplicate_blocks` | `duplicate_block` (CQ-007), blocks of 5 lines or more repeated in the inspected files |
| `metrics` / `file_metrics` | `file_metrics`: size and complexity numbers per file, severity `info`, no rule id |
| `dependency` / `manifest_parse` | `manifest_parse` (DEP-011): a manifest that could not be parsed |
| `dependency` / `osv_lookup` | `osv_lookup` (DEP-001): a pinned package with known vulnerabilities in [OSV](https://osv.dev) |
| `type_safety` / `type_patterns` | `any_usage` (TYP-001), `unsafe_cast` (TYP-002), `type_ignore` (TYP-003), `non_null_assertion` (TYP-004), `raw_generic` (TYP-013), `null_safety` (no rule id) |
| `performance` / `performance_patterns` | `n_plus_one` (PERF-001), `nested_loops` (PERF-002), `string_concat_in_loop` (PERF-004), `blocking_async` (PERF-005), `sort_in_loop` (PERF-011) |
| `api_contract` / `api_patterns` | `verb_in_url` (API-005) |
| `api_contract` / `orphan_endpoints` | `orphan_endpoint` and `orphan_call` (API-002): a route no inspected file calls, or a call matching no route |
| `data_privacy` / `pii_patterns` | `ssn`, `email_literal` and `credit_card` (PRIV-002), `pii_logging` (PRIV-001), `insecure_storage` (PRIV-005), `tracking_without_consent_check` (PRIV-007), `data_retention` (PRIV-008) |

Some checks only see the files you pass. `circular_imports` and `orphan_endpoints` need the files that import each other or call each other, so run them on a directory or the whole repository, not on one file.

`osv_lookup` needs network access, and only reads versions it can pin exactly, such as `requests==2.19.0` in `requirements.txt`. It reads `package.json`, `pubspec.yaml`, `requirements.txt` and `pyproject.toml`.

## Which playbooks apply

A playbook is a review method an agent can follow. `get_rules` lists the playbooks of an agent. `plan_review` goes further and says which ones fit the review in front of it.

| Agent | Playbooks |
| --- | --- |
| `security` | `agentic-actions-auditor`, `differential-review`, `fp-check`, `insecure-defaults`, `sharp-edges`, `variant-analysis` |
| `qa_synthesis` | `fp-check`, `vulnerability-triage-brocards` |
| `dependency` | `vulnerability-triage-brocards` |
| `api_contract` | `sharp-edges` |
| `data_privacy` | `insecure-defaults` |

`plan_review` points the `security` agent to `differential-review` when the scope is a diff, and to `agentic-actions-auditor` when files under `.github/workflows/` are in scope. It points `qa_synthesis` to `fp-check` and `vulnerability-triage-brocards`. See [Playbooks](playbooks.md).

## Presets

A preset is a named set of agents. Pass its name as `preset` to `plan_review`.

| Preset | Agents |
| --- | --- |
| `full` | All 10 |
| `core` | `code_quality`, `architecture`, `security`, `metrics`, `dependency`, `qa_synthesis` |
| `security-audit` | `security`, `data_privacy`, `dependency`, `qa_synthesis` |
| `performance-review` | `performance`, `metrics`, `architecture`, `qa_synthesis` |
| `quick-scan` | `code_quality`, `security`, `qa_synthesis` |
| `compliance-gdpr`, `compliance-hipaa`, `compliance-pci` | `data_privacy`, `qa_synthesis` |
| `type-safety` | `type_safety`, `code_quality`, `qa_synthesis` |
| `api-review` | `api_contract`, `security`, `qa_synthesis` |

## Languages

Files are matched to a language by extension: Python, TypeScript, JavaScript, Java, Kotlin, Go, Rust, Dart, C#, PHP, Ruby, Swift, C and C++. Some checks only apply to some of them. The type checks, for example, cover TypeScript, Python and Java.
