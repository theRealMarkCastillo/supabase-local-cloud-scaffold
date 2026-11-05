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
