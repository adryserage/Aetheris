---
id: insecure-defaults
title: Insecure defaults audit
agents: [security, data_privacy]
task: analyze
languages: []
when: Use to audit a file, directory, or whole repo for insecure default configuration such as fallback secrets, default credentials, fail-open switches, weak crypto, permissive access, and debug leakage.
source: https://github.com/trailofbits/skills/blob/e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff/plugins/insecure-defaults/README.md
source_commit: e4dd0bb5b15535f7c5a0834187dffba6ac37e4ff
author: Trail of Bits
license: CC-BY-SA-4.0
license_url: https://creativecommons.org/licenses/by-sa/4.0/
changes: Condensed README.md with the six references/*.md; removed the Workflow pipeline, parallel sweep and verifier agents and the report; one pass that greps candidates, then traces each one.
---

Whatever you point at is the target, however test-like it looks. Exclusions (fixtures, docs, vendored code) apply only outside the scope you named.

## Categories

| Category | Example | Report when | Skip when |
|---|---|---|---|
| Fallback secrets | `SECRET = env.get('KEY') or 'dev'` | A default supplied when the env var is absent feeds signing, encryption, session, or token machinery. | Defaults generated per-boot at random. Values only used as cache keys or correlation ids. |
| Default credentials | seeded `admin` / `admin123` | A credential literal a running deployment can authenticate with, including seeded accounts created on first boot. | Accounts created disabled or with a forced-reset flag. Credentials in docs, READMEs, and fixture files. |
| Fail-open switches | `getenv('REQUIRE_AUTH', 'false')` | The value taken when configuration is absent disables a security control. | Switches whose unconfigured value is the secure one. Flags read but never consulted at the enforcement point. |
| Weak crypto | `hashlib.md5(password)` | A broken or non-cryptographic primitive stands in for password hashing, token generation, encryption, or signature verification. | Checksums, ETags, cache keys, deduplication hashes, test vectors. |
| Permissive access | `ACL='public-read'`, `0o666`, CORS `*` | Access is granted to a party who should not have it, hardcoded or as the unconfigured fallback. | Deliberate public endpoints with a stated reason. Local-only dev servers. Permissiveness gated by an outer authorization layer at the same trust boundary. |
| Debug leakage | `traceback.format_exc()` in a response | Internal detail reaches a response, a listening port, or a log a lower-privileged party can read, behind a flag that defaults to on or unconditionally. | Log-verbosity-only flags with no user-facing output. Debug servers bound to loopback and off by default. |

Category notes:

- Fallback secrets: the decisive question is whether the app runs with the literal. `env.get(X, Y)` runs; `env[X]` crashes. That difference is the whole finding.
- Default credentials: a credential in prose is a credential nobody can use. A credential in `bootstrap_admin()` is a login.
- Fail-open: read the default, not the flag name. `REQUIRE_AUTH` defaulting to `'false'` requires nothing.
- Weak crypto: the algorithm alone is never the finding. `hashlib.md5` over a cache key is fine; the same call over a password is not. Trace to the use site before filing.
- Permissive access: ask who gains access, not how wide the value looks. `0o644` on a CDN asset is correct; `0o666` on a key file is not.
- Debug leakage: the finding needs both halves, enabled-by-default and an exposure path.

## Two shapes of candidate

- **Configurable**: a lookup with a fallback. Only a bug if the app runs with it. `env.get('K', 'x')` does; `env['K']` crashes instead, so it's fine.
- **Unconditional**: no configuration anywhere, insecure as written. About half of all findings. A missing env var is not grounds to refute one.

## Steps

1. **Profile the stack.** Find the project's own config wrappers, and flag those that can return a default. Seed patterns are a floor, not the search: derive patterns for the detected stack, such as framework keys, language idioms (`ENV.fetch`, `System.getProperty(k, d)`, `${VAR:-default}`) and manifest formats (`default =` in HCL, `ENV` in a Dockerfile). A codebase reading everything through `get_setting("X", "default")` barely matches the generic seeds.
2. **Collect candidates per category.** Grep only, and do not judge yet. Write patterns as POSIX ERE (`[[:space:]]`, `[0-9]`, never `\s`, `\d` or `\b`): some `grep` builds silently fail to match those, and a pattern that matches nothing is indistinguishable from a clean result. Keep one candidate per `category:file:line`; the same line flagged by two categories stays as two candidates.
3. **Verify each candidate.** Start at refuted and stop at the first step that kills it:
   1. Is the file reachable in production?
   2. Is the insecure value the one that runs? Configurable: does it fail-secure instead? Unconditional: this step can't refute it.
   3. Is the value actually insecure?
   4. Does it reach a security decision? Cite the sink.
   5. Does deployment always supply the var? Configurable only, and no answer refutes: every manifest setting it lowers severity, none is the CRITICAL case, and a partial or undetermined answer counts as reachable.

   Incomplete trace = refuted.
4. **Report coverage.** Report seed patterns and derived patterns separately. A category whose derived list is empty only looked for generic idioms; name it as a coverage gap. No candidates is not proof of absence.

When not to use it: a fixed pattern with no reachability question (Semgrep or a linter fits better), or extensive secret detection in committed credentials (use gitleaks/trufflehog).
