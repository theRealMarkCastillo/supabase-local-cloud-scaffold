# Validation and current limits

This is a new-project starter, independent of the existing application/migration
repositories. The official Docker vendor distribution is retained unmodified at its
pinned version; own adaptations are in scripts and Compose. Sources and upstream
requirements were checked on 2026-11-05.

## Completed

- Source-only creation copied no existing environment, user data, volumes or runtime
  configuration. Fresh init generates independent project identity, localhost ports
  8094/19804/18029 and private credentials/runtime files.
- Local Compose configuration and all optional profiles validate.
- Linux ARM64 Docker build, Node/TanStack compilation/type checks and backend startup
  passed. Schema migrated successfully into this instance's own database.
- Synthetic smoke passed signup/captured email/confirmation, password login, anonymous
  denial, two-user read/write RLS, private upload/download isolation, authenticated
  Edge Function/anon identity denial, logout refresh revocation, rendered HTML,
  per-response CSP nonces, no-store caching and absence of privileged values in HTML.

## Boundaries

The frontend manages sessions in the browser and renders a signed-out SSR shell.
Authenticated SSR, external OAuth/Keycloak, real SMTP, workers/queues, backups/restore
operations, cloud deployment and provider-specific secrets are not validated by the
default demo. Self-hosted managed-platform features are not implied. The pinned key
path remains legacy HS256; asymmetric/new API keys and rotation need a tested upgrade.
Local keys are newly generated but are not production credentials.

No existing stacks were stopped, reset or modified. No cloud services were deployed.

## Additional executed checks

- Six offline tests passed for fresh secrets/private files, environment overwrite
  refusal, migration naming/ordering, duplicate versions, symlinked SQL, transaction
  control, import-map escape and independent per-function authentication policies.
- A disposable database verified repeat application, edited migration refusal,
  anonymous RLS denial, failure rollback and incremental standard history. It was
  removed after the checks; application data was not reset.
- The generated hello-user function ran with a valid user's token and rejected an
  anon API JWT as an identity. This is included in the repeatable smoke command.
- Chrome checks passed login, notes, two-tab Realtime, Edge Function, private file
  upload/download, logout, signup/PKCE confirmation, mobile width, initial server
  HTML, CSP nonces/hydration, server-backend connection and real 404/admin denial.
  Exercised browser requests stayed local. This new instance's mobile screenshot was inspected after rendering settled.
- Fly app templates passed CLI validation; Render templates passed Blueprint schema
  validation. No provider deployment or hosted backend runtime was exercised.

Source-check CI is included for pushes/PRs. It does not deploy or claim full runtime
validation. Optional Vite runtime and Linux AMD64 were not exercised for this new
instance; the default TanStack image was built and run on local Linux ARM64.

## Review fixes — 2026-11-05

The review findings and implementation plan are resolved locally; see
[REVIEW.md](REVIEW.md) for exact fixes, commands, test counts and runtime evidence.
Application and documentation changes include the review fixes described above. No
cloud resource or production data was changed. Earlier publication statements refer
to the historical baseline; use Git history for subsequent fixes.

### Running the added checks

Make bootstraps `.venv-tools` using Python 3.11+ and installs pinned `pglast==8.7`
from `requirements-tools.txt` ([parser documentation](https://pglast.readthedocs.io/en/latest/parser.html)). First setup needs package-download access. The parser
is developer tooling, excluded from app images; `make tools` also enables direct
`python3 scripts/...` commands via a subprocess fallback. Its PostgreSQL 18 grammar
does not prove compatibility with the pinned backend's PostgreSQL version. SQL is
still executed transactionally on that backend; unsupported operations fail there.

Run Python tests and `make frontend-test` (Node 22+) without a browser. With the local
app running, the optional browser regression requires Playwright and Chrome:

```sh
npm install --prefix .runtime/browser-tools --no-save playwright@1.62.1
make browser-test
```

Alternatively set `SCAFFOLD_PLAYWRIGHT_PATH` to an installed `playwright/index.mjs`.
The default uses installed Chrome. To use Playwright's Chromium, install that
browser explicitly and set `SCAFFOLD_BROWSER_CHANNEL=chromium`. The test reads this
project's local `.env`, creates synthetic accounts/notes/files, and refuses nonlocal
origins. Keep its captured confirmation messages private. Extra local CA trust may
be needed for OrbStack; do not disable certificate verification. The regression
uses bounded waits and leaves its synthetic records for inspection.

## URL and callback follow-up — 2026-11-05

Added the cross-environment [URL/callback contract](URLS_AND_CALLBACKS.md), including
external registrations, internal endpoints, cloud differences and imported-app limits.
`make tunnel` now reads the configured local web port; the Supabase repos also provide
`make tunnel-set` as an alias for their origin action. Dry-run checks covered the
project port, a custom port and invalid-port refusal without launching ngrok. No
running origin, external registration or cloud deployment was changed. Public-tunnel
and social-provider runtime validation remain pending.

## Shared email commands — 2026-11-05

Added `make email-config`, `make email-test` and `make email-smoke`, matching the
cloud scaffold's command names with Supabase-native Auth behavior. See
[EMAIL.md](EMAIL.md) for configuration names, SMTP/cloud boundaries and recovery UI
limitations. Mailpit is aligned to v1.32.0 with a health check, project-scoped
persistent inbox and a 500-message cap. Upgrading replaced the old in-memory inbox;
existing Auth/database data and the configured public origin were preserved.

`make check email-config email-test email-smoke` passed on this local instance:
synthetic signup capture, confirmation, password login, recovery email/action,
backend password change, login with the new password and old-password rejection.
This is API-level recovery coverage; no password-reset UI was implemented or claimed.
Synthetic users/messages remain local. No real email was delivered externally.

`make test frontend-test up smoke` also passed: 12 Python tests,
3 frontend identity tests, healthy local stack and existing full Auth/RLS/private
storage/function/logout/SSR checks. Syntax, diff and documentation-link checks pass.
These email changes are recorded in the source accompanying this report. No cloud
deployment, external SMTP registration or public tunnel was performed. Real-provider delivery remains pending.
