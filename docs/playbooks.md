# Playbooks

A playbook is a review method your assistant follows step by step, such as a differential review of a diff. Aetheris has 7. They are adapted from [Trail of Bits Skills](https://github.com/trailofbits/skills) and served by the `get_playbook` tool.

`get_rules` lists the playbooks of an agent. `plan_review` lists the ones that fit the review in front of it. The assistant then calls `get_playbook` with the id and reads the steps before judging the code.

| Id | Title | Task | Agents | When to use it |
| --- | --- | --- | --- | --- |
| `differential-review` | Differential security review | analyze | `security` | Reviewing a PR, commit or diff for security vulnerabilities, or checking whether a change re-introduces a fixed bug |
| `agentic-actions-auditor` | Agentic actions audit | analyze | `security` | GitHub Actions workflow files in `.github/workflows/` are in scope and may invoke AI coding agents |
| `insecure-defaults` | Insecure defaults audit | analyze | `security`, `data_privacy` | Auditing a file, directory or repository for insecure default configuration: fallback secrets, default credentials, fail-open switches, weak crypto, permissive access, debug leakage |
| `sharp-edges` | Sharp edges analysis | analyze | `security`, `api_contract` | Reviewing API designs, configuration schemas or cryptographic library ergonomics for error-prone APIs and dangerous configurations |
| `fp-check` | False positive check | triage | `qa_synthesis`, `security` | Verifying whether a suspected security finding is real, exploitable or a false positive, before reporting it |
| `variant-analysis` | Variant analysis | triage | `security` | Right after a bug or bad pattern is confirmed in one file, to find other instances of the same root cause |
| `vulnerability-triage-brocards` | Vulnerability triage brocards | triage | `qa_synthesis`, `dependency` | Deciding whether a vulnerability report, CVE, advisory or raw automated finding deserves investigation |

The task is `analyze` for a method that looks for problems, and `triage` for a method that judges findings already made.

## Attribution

The playbooks are adapted from [Trail of Bits Skills](https://github.com/trailofbits/skills) and stay under the [Creative Commons Attribution-ShareAlike 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/) (CC BY-SA 4.0). The rest of Aetheris is under the Apache License 2.0.

Each playbook names its author, its source and what was changed. `get_playbook` returns the same information in the `attribution` block, and any reproduction of a playbook must keep it. The sources below are pinned to the commit the adaptation was made from.

| Playbook | Author | Source |
| --- | --- | --- |
| `differential-review` | Omar Inuwa | [SKILL.md](https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/differential-review/skills/differential-review/SKILL.md) |
| `agentic-actions-auditor` | Emilio López, Will Vandevanter | [SKILL.md](https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/agentic-actions-auditor/skills/agentic-actions-auditor/SKILL.md) |
| `insecure-defaults` | Trail of Bits | [README.md](https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/insecure-defaults/README.md) |
| `sharp-edges` | Trail of Bits | [SKILL.md](https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/sharp-edges/skills/sharp-edges/SKILL.md) |
| `fp-check` | Maciej Domanski | [SKILL.md](https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/fp-check/skills/fp-check/SKILL.md) |
| `variant-analysis` | Axel Mierczuk | [SKILL.md](https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/variant-analysis/skills/variant-analysis/SKILL.md) |
| `vulnerability-triage-brocards` | Alexis Challande, adapted from William Woodruff | [SKILL.md](https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/vulnerability-triage-brocards/skills/vulnerability-triage-brocards/SKILL.md) |

The adapted files live in [`aetheris/playbooks/trailofbits/`](https://github.com/adryserage/aetheris/tree/main/aetheris/playbooks/trailofbits), next to the license text. The `changes` field of each file says what was condensed or removed.
