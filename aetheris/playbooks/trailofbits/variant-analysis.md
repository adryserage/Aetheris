---
id: variant-analysis
title: Variant analysis
agents: [security]
task: triage
languages: []
when: Use right after a vulnerability, logic bug, or bad pattern is confirmed in one file, to find the other instances of the same root cause across the codebase.
source: https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/variant-analysis/skills/variant-analysis/SKILL.md
source_commit: e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff
author: Axel Mierczuk
license: CC-BY-SA-4.0
license_url: https://creativecommons.org/licenses/by-sa/4.0/
changes: Condensed SKILL.md with references/root-cause.md, searching.md and triage.md; removed the parallel workflow, CodeQL/Semgrep resources and the report template; the ladder runs with grep only.
---

Find the other instances of a bug you have already found. One root cause usually has several manifestations, and they are rarely in the module where you found the first one. Not for initial discovery with no bug in hand.

**Coverage limit.** This adaptation searches with grep (ripgrep) only. Grep does not follow values across functions: data flow tracking needs Semgrep taint or CodeQL, and cross-function analysis needs CodeQL. Say so when a variant depends on inter-function flow.

## Steps

1. **Understand the original issue.** Ask four questions: what operation is dangerous, what data makes it dangerous, what's missing, what context enables it? Then write the statement "This vulnerability exists because [UNTRUSTED DATA] reaches [DANGEROUS OPERATION] without [REQUIRED PROTECTION]." For logic bugs with no data flow, state the violated invariant instead. That statement is the search pattern. Enumerate every manifestation before searching:
   - Semantically related identifiers: `isAuthenticated` also means `isActive`, `isAdmin`, `isVerified`. Grep for the names before claiming them; identifiers that don't exist waste a search axis.
   - Other boolean-logic errors: inverted conditions, a wrong default return (`return True` on the fall-through path), `or` where `and` was meant.
   - Data-type edge cases: null comparisons where both sides can be null, empty string vs null, zero vs null, empty collections.
   - Documentation/code mismatches: functions named with `deny`, `restrict`, `block`, `check`, `validate` whose return value does not mean what the name says.

   Understanding why a variant exists predicts where to find it. A copy-paste bug clusters in sibling files; an API misuse bug clusters at every call site of that API.

2. **Create an exact match.** Write a pattern matching ONLY the known instance and confirm it hits. A pattern that matches nothing means you have misunderstood the bug, and every search built on it is calibrated against the wrong code.

3. **Generalize one element at a time.** Climb from the exact match toward the pattern family: first replace variable names, then generalize the surrounding structure. Each step: make ONE change, run it, read ALL new matches, decide whether the false-positive rate is still acceptable, then continue or revert. Abstract a variable name only if different names could carry the same bug; abstract a literal only if any value triggers the bug. Stop when more than roughly half the matches are noise: revert and take a different abstraction rather than pushing further up the same one.
   - Run every search against the entire codebase root, not the directory the original bug lived in. Narrow scope is the single most common reason a hunt finds nothing.
   - Filter test trees (`rg "pattern" --glob '!**/test*' --glob '!**/*_test.*'`), already-sanitized forms, and literal values that are not attacker-controlled.
   - Analyze false positives as you go: they tell you which abstraction was too aggressive.

4. **Triage.** The snippet alone is never enough. Read the surrounding function, the callers, and the type of every value involved, then look for what makes it safe: a guard earlier in the function or in a decorator/middleware, a sanitizer or parameterized API between source and sink, a type constraint that makes the dangerous value unreachable, a caller set that never supplies attacker-controlled input. A candidate survives only if you looked for these and did not find them.
   - Establish reachable, controllable, unprotected. Reachable and controllable with a different protection in place is a false positive worth recording. Unreachable today but unprotected is a real finding at lower severity: say so and say what would make it reachable. Having no callers is not a reason to refute.
   - Test null equality bypasses (`None == None` passes an ownership check), documentation/code mismatches (every caller of such a function is a potential finding), unauthenticated callers, and boundary values.
   - Attach a severity to every verdict, and keep severity (impact if real) separate from confidence (how sure you are). Do not suppress findings you judge minor.
   - When a candidate is ruled out, record why it was safe.

5. **Write it up**, including the patterns that failed and a CI rule to prevent regression.

## What makes hunts fail

1. Narrow scope: searching only the module the original bug was in.
2. Pattern too specific: searching one attribute and missing the family around it.
3. One vulnerability class: chasing a single manifestation of the root cause.
4. Happy-path testing: never trying the null, empty, and boundary cases.
5. Generalizing too fast: abstracting several elements at once, so noise cannot be attributed to any one of them.
