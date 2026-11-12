---
id: differential-review
title: Differential security review
agents: [security]
task: analyze
languages: []
when: Use when reviewing a PR, commit, or diff for security vulnerabilities, or checking whether a change re-introduces a previously fixed bug.
source: https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/differential-review/skills/differential-review/SKILL.md
source_commit: e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff
author: Omar Inuwa
license: CC-BY-SA-4.0
license_url: https://creativecommons.org/licenses/by-sa/4.0/
changes: Condensed SKILL.md with references/methodology.md and adversarial.md; removed the subagent, audit-context-building, issue-writer and the report file; one manual pass with Read, Grep and git instead.
---

## Principles

1. Risk-first: focus on auth, crypto, value transfer, external calls.
2. Evidence-based: every finding backed by git history, line numbers, attack scenarios.
3. Adaptive: scale to codebase size.
4. Honest: explicitly state coverage limits and confidence level.

Classify by risk, not size: Heartbleed was 2 lines. Analyze a "just a refactor" change as HIGH until proven LOW; refactors break invariants.

## Steps

1. **Intake and triage.** List the changes (`git diff <base>..<head> --stat`, `git log <base>..<head> --oneline`, `git diff <base>..<head> --name-only`). Pick the depth from the codebase size:
   - SMALL (<20 files): deep, read all deps, full git blame.
   - MEDIUM (20-200): focused, 1-hop deps, priority files.
   - LARGE (200+): surgical, critical paths only.

   Risk score each file:
   - HIGH: auth, crypto, external calls, value transfer, validation removal.
   - MEDIUM: business logic, state changes, new public APIs.
   - LOW: comments, tests, UI, logging.

2. **Changed code analysis.** For each changed file, read both versions (baseline and changed). For each diff region, note BEFORE, AFTER, CHANGE (behavioral impact) and SECURITY (implications).
   - Git blame removed code: `git log -S "removed_code" --all --oneline`. Removed code from "fix", "security", "CVE" commits is CRITICAL; recently added (<1 month) then removed is HIGH.
   - Check for regressions: `git log -S "added_code" --all -p`. Code added, removed for security, re-added now is a REGRESSION.
   - Ask: what attack did removed code prevent? What new surface does new code expose? Can modified logic be bypassed? Are checks weaker? Edge cases covered?

3. **Test coverage.** Separate production changes from test changes (`git diff <range> --name-only | grep -v "test"`), then search for tests of each changed function. Risk elevation rules:
   - NEW function + NO tests: elevate risk MEDIUM to HIGH.
   - MODIFIED validation + UNCHANGED tests: HIGH RISK.
   - Complex logic (>20 lines) + NO tests: HIGH RISK.

4. **Blast radius.** Count callers for each modified function (`grep -r "functionName(" . | wc -l`): 1-5 LOW, 6-20 MEDIUM, 21-50 HIGH, 50+ CRITICAL.

   | Change risk | Blast radius | Priority | Depth |
   |---|---|---|---|
   | HIGH | CRITICAL | P0 | Deep + all deps |
   | HIGH | HIGH/MEDIUM | P1 | Deep |
   | HIGH | LOW | P2 | Standard |
   | MEDIUM | CRITICAL/HIGH | P1 | Standard + callers |

5. **Deep context on HIGH RISK functions.** Manually perform the line-by-line analysis using Read, Grep, and code tracing:
   - Map the function flow: entry conditions, state reads, state writes, external calls, return values and side effects.
   - Trace internal calls and external calls; identify trust boundaries crossed and check for reentrancy risks.
   - Identify invariants: what must ALWAYS be true, what must NEVER happen, are they maintained after the change?
   - Five whys: why was this code changed, why did the original code exist, why might this break?
   - Find repeated validation patterns with grep and check whether the diff removes any. Flag if removal breaks defense-in-depth.

6. **Adversarial analysis on HIGH RISK changes.**
   - Attacker model: WHO (unauthenticated user, authenticated user, malicious administrator, compromised service), WHAT access they have, WHERE they interact (endpoints, functions, RPC, external APIs).
   - Attack vector: the exact entry point, the attack sequence, and proof of accessibility (the function is public, the attacker has the required permissions).
   - Exploitability: EASY (public APIs, no special privileges, single call), MEDIUM (specific conditions or elevated but obtainable privileges), HARD (admin privileges, rare edge cases, significant resources).
   - Concrete impact: specific, measurable harm, not "could cause issues".
   - Cross-reference the baseline: does this violate a system-wide invariant, break a trust boundary, bypass a validation pattern, or regress a previous fix?

## Red flags (stop and investigate)

- Removed code from "security", "CVE", or "fix" commits.
- Access control modifiers removed (internal to external).
- Validation removed without replacement.
- External calls added without checks.
- High blast radius (50+ callers) + HIGH risk change.

These patterns require adversarial analysis even in quick triage.

## Before delivering

- All changed files analyzed; git blame on removed security code; blast radius calculated for HIGH risk.
- Attack scenarios are concrete, not generic; findings reference specific line numbers and commits.
- Do not claim full analysis when time-limited.

When not to use: greenfield code (no baseline to compare), documentation-only changes, formatting or linting changes.
