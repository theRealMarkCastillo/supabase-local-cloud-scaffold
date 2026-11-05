# New-project development workflow

## Schema and migrations

Write authoritative SQL under supabase/migrations. `make migration NAME=add_projects`
creates a unique UTC timestamped file. Include grants, RLS, ownership checks, indexes,
triggers, storage buckets/policies and required extensions as appropriate.

Run `make migrate` against the project's already running database, or `make up` to
start/rebuild and apply pending files. Each file and its migration-history entries
commit in one transaction under a database advisory lock. Failure rolls back that
file; earlier files remain applied. Logs are private at .runtime/migration.log.

The runner records standard versions in supabase_migrations.schema_migrations and
checksums in a private scaffold_internal ledger. Unchanged applied files are skipped;
edited files or pre-existing external history stop for review. It does not baseline
an existing database automatically. Transaction-incompatible operations, psql commands
and explicit BEGIN/COMMIT need a separately reviewed process. No down/reset command.

This Compose runner is not Supabase CLI's local stack. Do not start a second CLI
stack and assume it is the same database. CLI migration-authoring/promotion tools can
be used deliberately, but inspect the installed CLI version and selected destination.
For managed hosting, promote the reviewed migration files using its normal deployment
process; cloud migration is not authorized by a local make command.

Sources: [Supabase migrations](https://supabase.com/docs/guides/local-development/database-migrations),
[self-hosted Docker](https://supabase.com/docs/guides/self-hosting/docker).

## Functions and shared code

`make function NAME=hello-user` creates supabase/functions/hello-user/index.ts. Its
handler verifies caller identity through Auth; it does not treat a valid anon JWT
as a signed-in user. `make up` loads source changes into a generated runtime mount.

Add shared modules under _shared. Root/per-function deno.json/deno.jsonc maps are
supported. Optional policy lives in supabase/config.toml:

```toml
[functions.hello-user]
verify_jwt = true
# import_map = "./functions/hello-user/deno.json"
```

JWT verification defaults to true. If a webhook must be public, explicitly configure
false and validate the provider signature in its code. Keep authorization and RLS
checks in place. Unsupported custom entrypoints fail for adapter review. Remote
package imports may require internet and a cache; pin them when adding dependencies.

The runtime router is generated from the pinned upstream file, outside vendor. Code
changes create a new runtime generation; the old generation is not edited beneath
a running container. Local .env.functions supports one-line secret values and must
be mode 0600. Core backend/router settings cannot be overridden there. All functions
share this app-level environment; this is not secret isolation between functions.

Source: [Self-hosted functions](https://supabase.com/docs/guides/self-hosting/self-hosted-functions).

## Frontend and server data

The TanStack server loader serializes only explicit public config; the Node process
has no database password or service-role key. A read-only server function probes the
internal database API with the anonymous role. An authorization denial is expected.
Private notes/files are accessed from the browser with the signed-in user's token.

The SSR shell starts signed out. Authenticated server-rendered data requires verified
request-scoped cookies/tokens and authorization. Never share a global user session or
privileged database client between requests. For a new framework, preserve the same
backend contract and add its own adapter rather than shipping secrets in browser code.

## Project identity and origin

Choose name/ports at fresh init. Do not copy .env or rename STACK_NAME as a way to
migrate data: another name selects another set of volumes. Keep PUBLIC_URL aligned
with WEB_PORT or the explicit HTTPS host. Email links already captured before an
origin change retain their old URL; request new messages afterwards.

For demos, expose the app only. Signup is enabled for the local example; decide whether
public signup is appropriate and add abuse controls for a real internet deployment.

## Fixtures and checks

Use synthetic data through a separate script or API workflow. Schema migrations
should not embed customer data or credentials. `make smoke` creates synthetic accounts,
records and files and retains them locally. It is restricted to local/OrbStack hosts.
Check cross-user reads/writes as well as the happy path for every new table/bucket.

Run `make integration` with this project's database running to test rollback and
history in a disposable database. It removes only that database afterwards.
