# Hosting the application and Supabase backend

No deployment or paid provisioning happens automatically. Local verification proves
only the exercised local behavior, not cloud operations.

## App on Fly/Render with managed Supabase

Use cloud/fly.tanstack.toml or cloud/render.tanstack.yaml for the standalone Node app.
The Docker build context is the repository root. Set PUBLIC_URL,
SUPABASE_BROWSER_URL, SUPABASE_BROWSER_KEY and SUPABASE_SERVER_URL for a separate
hosted development Supabase project. Only the explicit public projection is sent to
the browser. The server API URL may be the same HTTPS endpoint or a reachable private
route. Do not give this app image service-role credentials.

The image binds 0.0.0.0 and honors PORT. /health checks the app process; the example
button separately checks backend connectivity. Apply reviewed schema, buckets/policies
and function source to the hosted backend, configure SMTP and auth redirects, and
verify the actual deployment before using real data. Local sample credentials must
never become hosted credentials.

For a local app-only container against a configured external DEVELOPMENT backend:

```sh
# Copy .env.hosted.tanstack.example to ignored .env.hosted.tanstack and set values.
docker compose --env-file .env.hosted.tanstack -f compose.hosted.tanstack.yaml up --build -d
```

That command intentionally contacts the configured external backend. It does not
start a local Supabase instance. Static Vite alternatives use compose.hosted.yaml,
.env.hosted.example, cloud/fly.web.toml and cloud/render.yaml.

This reference loads public config at runtime. An application that embeds VITE_*
values at build time must supply them during build and rebuild after changing them.
Never reference sensitive build arguments; use provider runtime secret settings.

## Entire open-source backend on a persistent VM

Use the pinned official Docker distribution as the foundation. Development Compose
settings need a separate operational deployment configuration: public HTTPS ingress,
restricted admin access, real SMTP/OAuth, persistent database/file volumes, tested
backup/restore procedures, monitoring, upgrades and secret/key rotation.

The full upstream stack lists 4 GB minimum / 8 GB+ recommended RAM. It is a stateful
collection of services, not a single stateless container. Use a VM/VPS sized for it,
or design the services and persistence explicitly on your chosen provider. The app
can still run separately on Fly or Render close to the database.

Self-hosted Supabase does not provide all managed-platform capabilities, including
managed backups/PITR and branching. A CLI development stack is also distinct from
a self-hosted deployment; neither local success nor copying Compose establishes
production readiness.

## Keep local, demo on demand

For intermittent work, run Compose locally. Expose only the web port through a chosen
tunnel, configure the resulting public HTTPS origin, and stop the stack when finished.
Never publish the raw gateway/Studio, database, pooler or captured-email UI.

## Database alternatives

A plain hosted Postgres connection alone does not implement the Auth/Storage/Realtime/
Functions APIs used here. Moving those interfaces requires an explicit migration;
changing DATABASE_URL is insufficient. Keep the full Supabase backend contract when
you want the least application change. Alternative backend adapters are a separate
project decision.

Sources checked 2026-11-05:
[Supabase self-hosting](https://supabase.com/docs/guides/self-hosting),
[Docker requirements](https://supabase.com/docs/guides/self-hosting/docker),
[Fly configuration](https://fly.io/docs/reference/configuration/),
[Render Docker](https://render.com/docs/docker).

Email capture, recovery checks and cloud SMTP configuration: [EMAIL.md](EMAIL.md).
