---
id: fp-check
title: False positive check
agents: [qa_synthesis, security]
task: triage
languages: []
when: Use to verify whether a specific suspected security finding is real, exploitable, or a false positive before it is reported, not to hunt for new bugs.
source: https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/fp-check/skills/fp-check/SKILL.md
source_commit: e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff
author: Maciej Domanski
license: CC-BY-SA-4.0
license_url: https://creativecommons.org/licenses/by-sa/4.0/
changes: Condensed SKILL.md with references/standard-verification.md and gate-reviews.md; kept the standard path only, removed the deep path (task tracking and analysis agents) and names when it would be needed.
---

Produce a TRUE POSITIVE or FALSE POSITIVE verdict with documented evidence for each suspected bug. Every bug gets full verification.

## Rationalizations to reject

- "This pattern looks dangerous, so it's a vulnerability." Pattern recognition is not analysis: complete data flow tracing before any conclusion.
- "The code looks unsafe, reporting without tracing data flow." Unsafe-looking code may have upstream validation: trace the complete path from source to sink.
- "Similar code was vulnerable elsewhere." Each context has different validation, callers, and protections: verify this specific instance independently.
- "This is clearly critical." LLMs are biased toward seeing bugs and overrating severity: complete the devil's advocate review.

## Step 0: Understand the claim and context

Restate the bug in your own words. Half of false positives collapse at this step: the claim doesn't make coherent sense when restated precisely. Document the exact vulnerability claim, the alleged root cause, the supposed trigger, the claimed impact, the threat model (privilege level, sandbox, what the attacker can already do), the bug class, the execution context, the callers and the input constraints they impose, and whether this is part of a larger system with multiple protection layers.

## Route

Use this standard path when ALL of these hold: a clear, specific claim; a single component; a well-understood bug class (buffer overflow, SQL injection, XSS, integer overflow); no concurrency or async in the trigger; straightforward data flow from source to sink.

**Deep verification is not part of this adaptation.** It is needed when ANY of these hold: an ambiguous claim, a cross-component bug path (data flows through 3+ modules or services), race conditions, TOCTOU or concurrency in the trigger, logic bugs without a clear spec, an inconclusive standard check, or an explicit request for full verification. When a bug needs it, say so in the verdict instead of concluding.

## Standard verification

1. **Data flow.** Trace data from source to the alleged sink. Map trust boundaries crossed. Identify all validation and sanitization between source and sink. Check API contracts: many APIs have built-in bounds protection. Check for environmental protections (compiler, runtime, OS, framework) that prevent exploitation entirely. Key pitfall: analyzing the vulnerable code in isolation; conditional logic upstream may make it mathematically unreachable. **Escalation check:** 3+ trust boundaries, callbacks or async control flow, or an ambiguous validation chain means deep verification would be needed.
2. **Exploitability.** Prove the attacker controls data reaching the vulnerable operation; internal storage set by trusted components is not attacker-controlled. For integer or bounds issues, write an explicit algebraic proof: IF validation_check_passes THEN bounds_guarantee_holds. For race conditions, prove concurrent access is actually possible.
3. **Impact.** Distinguish real security impact (RCE, privesc, info disclosure) from operational robustness issues (crash recovery, cleanup failure). Failure of a defense-in-depth measure is not a vulnerability if primary protections remain intact.
4. **PoC sketch.** Write pseudocode showing the attack path: `[Source] → [Validation?] → [Transform?] → [Vulnerable Op] → [Impact]`, what the attacker controls, and the trigger.
5. **Devil's advocate.** Against the vulnerability: Am I seeing it because the pattern "looks dangerous"? Am I assuming attacker control over trusted data? Have I proven the mathematical condition can occur? Am I confusing defense-in-depth failure with a primary vulnerability? Am I hallucinating it? For the vulnerability: Am I dismissing a real one because the exploit seems complex or unlikely? Am I inventing mitigations I haven't verified in the source? Re-read the code after reaching a conclusion. **Escalation check:** genuine uncertainty you cannot resolve means deep verification would be needed.
6. **Gate review.** All six gates must pass before reporting any bug as a vulnerability:

   | Gate | Pass | Fail |
   |---|---|---|
   | 1. Process | Evidence exists for every step | Steps lack concrete evidence |
   | 2. Reachability | Attacker-controlled path shown + PoC confirms | Cannot demonstrate attacker control or reachability |
   | 3. Real impact | Direct RCE, privesc, or info disclosure with concrete scenarios | Only an operational robustness issue |
   | 4. PoC validation | Shows attacker control, trigger, and impact | Fails to show attack path or impact |
   | 5. Math bounds | Algebraic proof shows the condition is possible | Math proves validation prevents it |
   | 6. Environment | Protections do not eliminate the vulnerability | Environmental protections block it entirely |

## Verdict

- All gates pass: `BUG #N TRUE POSITIVE — [brief vulnerability description]`.
- Any gate fails: `BUG #N FALSE POSITIVE — [brief reason for rejection]`, naming the failed gate and its evidence. Continue all remaining steps before issuing it.

For several bugs: run Step 0 for all of them first, then verify each, then check for exploit chains (findings that individually failed may combine to form a viable attack). Finish with the counts of true and false positives and a one-line reason for each.
