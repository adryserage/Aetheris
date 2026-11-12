---
id: sharp-edges
title: Sharp edges analysis
agents: [security, api_contract]
task: analyze
languages: []
when: Use when reviewing API designs, configuration schemas, or cryptographic library ergonomics for error-prone APIs, dangerous configurations, and footgun designs.
source: https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/sharp-edges/skills/sharp-edges/SKILL.md
source_commit: e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff
author: Trail of Bits
license: CC-BY-SA-4.0
license_url: https://creativecommons.org/licenses/by-sa/4.0/
changes: Condensed SKILL.md; removed the sharp-edges-analyzer agent and the per-language reference files; the four phases run in one pass.
---

**The pit of success**: secure usage should be the path of least resistance. If developers must understand cryptography, read documentation carefully, or remember special rules to avoid vulnerabilities, the API has failed.

Not for implementation bugs (use standard code review), business logic flaws, or performance.

## Rationalizations to reject

- "It's documented": developers don't read docs under deadline pressure. Make the secure choice the default or only option.
- "Advanced users need flexibility": flexibility creates footguns. Provide safe high-level APIs; hide primitives.
- "Nobody would actually do that": assume maximum developer confusion.
- "It's just a configuration option": config is code; wrong configs ship to production. Validate configs; reject dangerous combinations.
- "We need backwards compatibility": insecure defaults can't be grandfather-claused. Deprecate loudly; force migration.

## Categories

1. **Algorithm/mode selection.** APIs that let developers choose algorithms invite choosing wrong ones. The JWT pattern: the header specifies the algorithm, so an attacker can set `"alg": "none"`, or use an RSA public key as HMAC secret when switching RS256 to HS256. Root cause: letting untrusted input control security-critical decisions. Look for parameters like `algorithm`, `mode`, `cipher`, `hash_type`.
2. **Dangerous defaults.** Defaults that are insecure, or zero/empty values that disable security. Look for timeouts or lifetimes that accept 0, empty strings that bypass checks, null values that skip validation, boolean defaults that disable security features, negative values with undefined semantics. Ask what happens with `timeout=0`, `max_attempts=0`, `key=""`, and whether the default is the most secure option.
3. **Primitive vs. semantic APIs.** APIs that expose raw bytes instead of meaningful types invite type confusion. Look for functions taking `bytes`, `string`, `[]byte` for distinct security concepts, and parameters that could be swapped without type errors. The comparison footgun: `hmac == expected` (timing attack) looks identical to `hmac.Equal(mac, expected)` (constant-time).
4. **Configuration cliffs.** One wrong setting creates catastrophic failure, with no warning. Look for boolean flags that disable security entirely, string configs that aren't validated, combinations of settings that interact dangerously, environment variables that override security settings, and constructor parameters with sensible defaults but no validation (callers can override with insecure values). Examples: `verify_ssl: fasle` silently accepted as truthy; `session_timeout: -1`.
5. **Silent failures.** Errors that don't surface, or success that masks failure. Look for functions returning booleans instead of throwing on security failures, empty catch blocks around security operations, default values substituted on parse errors, verification functions that "succeed" on malformed input (`if not key: return True`), and return values the developer forgets to check.
6. **Stringly-typed security.** Security-critical values as plain strings enable injection and confusion. Look for SQL or commands built from string concatenation, permissions as comma-separated strings (`permissions += ",admin"`), roles or scopes as arbitrary strings instead of enums, URLs constructed by joining strings.

## Steps

1. **Surface identification.** Map security-relevant APIs (authentication, authorization, cryptography, session management, input validation). Identify developer choice points: where can developers select algorithms, configure timeouts, choose modes? Find configuration schemas: environment variables, config files, constructor parameters.
2. **Edge case probing.** For each choice point ask:
   - Zero/empty/null: what happens with `0`, `""`, `null`, `[]`?
   - Negative values: what does `-1` mean? Infinite? Error?
   - Type confusion: can different security concepts be swapped?
   - Default values: is the default secure? Is it documented?
   - Error paths: what happens on invalid input? Silent acceptance?
3. **Threat modeling.** Consider three adversaries:
   - The Scoundrel (malicious developer or attacker controlling config): can they disable security via configuration, downgrade algorithms, inject malicious values?
   - The Lazy Developer (copy-pastes examples, skips documentation): will the first example they find be secure? Is the path of least resistance secure?
   - The Confused Developer (misunderstands the API): can they swap parameters without type errors, use the wrong key/algorithm/mode by accident? Are failure modes obvious or silent?
4. **Validate findings.** For each sharp edge: reproduce the misuse with minimal code, verify the misuse creates a real vulnerability, check whether the danger is documented (documentation doesn't excuse bad design, but affects severity), and test whether the API can be used safely with reasonable effort. If a finding seems questionable, return to step 2 and probe more edge cases.

## Severity

| Severity | Criteria | Example |
|---|---|---|
| Critical | Default or obvious usage is insecure | `verify: false` default; empty password allowed |
| High | Easy misconfiguration breaks security | Algorithm parameter accepts "none" |
| Medium | Unusual but possible misconfiguration | Negative timeout has unexpected meaning |
| Low | Requires deliberate misuse | Obscure parameter combination |

Before concluding: all zero/empty/null edge cases probed, defaults verified secure, all three adversary types considered, error paths verified not to bypass security, constructor params validated (not just defaulted).
