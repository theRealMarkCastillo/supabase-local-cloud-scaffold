# Common additions: start with Supabase

Use the existing Supabase capability first. Add another process or service when a
specific workload, integration or operational requirement justifies it. Adding a
feature often means SQL, provider configuration or application code, not another
container. This guide describes options; it does not enable or provision them.

## What is ready versus available to add

- **Implemented and exercised:** email/password Auth with local confirmation mail,
  Postgres/REST, note RLS, private Storage, Realtime, Edge Functions and app health
  checks. These are the default scaffold's tested paths.
- **Supabase/Postgres capabilities requiring setup:** social login, Keycloak
  federation, Postgres queues, cron, additional extensions, external storage and real
  SMTP. Availability in Supabase documentation is not proof that the pinned local
  configuration has enabled or tested them.
- **Additional services/processes:** a worker, Redis, Keycloak, search engine,
  monitoring service or secret manager when the chosen design requires one.

Studio/meta is available through `make admin`. The upstream pooler profile validates
as configuration; this application's use of it is not runtime-tested. GraphQL and
other upstream storage/analytics variants are not exercised by the default demo.

## Choose an addition by use case

| Need | Start with the existing stack | Add something when… | Example addition and extra work |
| --- | --- | --- | --- |
| Login and social sign-in | Supabase Auth; configure Google/Apple providers | An organization already has a central IdP or needs shared enterprise identity | Keycloak as an upstream Auth provider; maintain realm/issuer, per-app clients, callbacks, linking and logout tests |
| Application authorization | Postgres grants, RLS and explicit application permissions | A separate policy system is justified by a concrete cross-service requirement | Policy service; define enforcement points and failure behavior while retaining database boundaries |
| File uploads and downloads | Supabase Storage, private buckets and ownership policies | Files need a different durable storage backend or operational arrangement | Supported S3-compatible backend; configure endpoints, credentials, metadata, backups and private access tests. MinIO is not needed for this demo's file-backed storage |
| Small API handlers and webhooks | Edge Functions or the app's server routes | Work needs a persistent process, specialized runtime or resources outside request execution constraints | API/worker container; define authentication, health, timeouts and deployment lifecycle |
| Durable background jobs | Consider a Postgres-backed queue, including Supabase Queues/pgmq after setup | Jobs need long-running execution, heavy processing or independent concurrency/scaling | Worker process consuming the Postgres queue. Redis is a separate choice if the selected queue library/workload requires it |
| Scheduled tasks | Consider pg_cron after setup, invoking SQL or enqueueing work | Schedules must coordinate across services, or database scheduling is unsuitable | Scheduler/cron container or hosted scheduler; ensure one active schedule, credentials, run history and duplicate prevention |
| Caching | Query/index improvements and ordinary application/HTTP caching where appropriate | Measurements show a shared, low-latency cache would help multiple app instances | Redis; define TTLs, invalidation, eviction and correctness during cache failure |
| Rate limiting | Supabase Auth's own endpoint limits; explicit application limits for business APIs | Shared counters or broader traffic controls need a dedicated implementation | Redis-backed limiter or gateway; define atomic updates, scope and outage behavior. Auth limits do not cover every application endpoint |
| Search | Postgres indexes/full-text search; pgvector when the use case needs it and the extension is configured | Ranking, faceting, scale or operational needs exceed the Postgres design | Dedicated search engine; maintain authorization filters, synchronization and rebuild procedures |
| Real email delivery | Mailpit captures local messages; configure Auth SMTP for real delivery | The app must send notifications or transactional messages beyond Auth flows | SMTP/email provider adapter; delivery/bounce handling, retries and scoped credentials |
| Observability | Health checks and container logs | You need aggregated errors, metrics, traces, retention or alerts | Chosen error/metrics/tracing service; redact tokens, bound retention/resources and define actionable alerts |
| AI, payments and other APIs | Server-side adapters in functions/app code | A product feature requires an external provider | Provider credentials and client code; synthetic fixtures, webhook verification, retries and explicit real-provider tests |
| Secret management | Ignored private local env files; provider runtime settings when hosted | Rotation, audit, access policy or workload identity requires a dedicated system | Managed secret store; map each secret to consuming services and avoid privileged browser/build values |

Examples:

- **Generate a PDF after an upload:** keep Supabase Storage and Postgres metadata;
  enqueue a job and add a worker if rendering needs it. A worker does not imply Redis.
- **Sign in with Google:** configure Supabase Auth and a Google development client.
  Keycloak is unnecessary unless there is a separate shared-identity requirement.
- **Send a nightly summary:** configure a reviewed schedule that enqueues work; the
  consumer handles delivery/retries. A separate scheduler is not automatically needed.
- **Speed up a slow dashboard:** measure queries/indexes first. Add Redis only with
  a cache design and evidence that it solves the bottleneck.

## Background work is more than a request

Supabase Queues is built on the Postgres `pgmq` extension; Supabase Cron uses
`pg_cron`. Enabling them locally requires checking the pinned database image,
extensions, schema/API permissions and operational settings. Neither is enabled or
app-tested by this scaffold. Do not assume managed Dashboard setup instructions
apply unchanged to a self-hosted deployment.

A queue stores work; a consumer executes it; a scheduler decides when to enqueue or
invoke it. These are separate responsibilities even when they share Postgres.
Consumers need idempotency, retries/backoff, visibility/lease handling, dead-letter
or failure reporting, shutdown behavior and ownership checks. A queue's delivery
semantics do not guarantee that an external side effect happens exactly once.

Edge Functions can handle appropriate background tasks, but request/worker limits
and restarts still matter. Use durable state for work that must survive termination.
Hosted limits and this pinned self-hosted runtime's settings are distinct; inspect
both rather than copying one set of limits into another environment.

## Preserve the existing boundaries

Keep Supabase Auth issuing the app session when federating to Keycloak, unless a
separate identity migration is explicitly designed. RLS and Storage policies still
need the expected identity claims. Never put privileged keys into frontend config.

Mailpit is an administrative capture tool, not a delivery service. Keep its UI,
Studio, database and raw gateway off public demo tunnels. A new service must not
accidentally expose its own administrative interface through the app ingress.

For every addition, record: the requirement the default cannot satisfy, who calls
it, authentication/authorization, secrets, persistent state, outage behavior, resource
cost, local/hosted configuration and the checks that establish it works. Avoid adding
a service solely because another starter template includes one.

## Operational requirements still apply

Backups/restore verification, patching, monitoring and secret/key rotation are real
requirements for a hosted stateful backend even if they do not need a new container.
Local named volumes persist data; they are not backups. Managed Supabase and a
self-hosted backend provide different operational guarantees. See [hosting](CLOUD.md)
and [security](SECURITY.md) before treating the local demo as a production setup.

## References

Checked 2026-11-05; consult the current provider/version documentation when implementing:

- [Supabase Keycloak](https://supabase.com/docs/guides/auth/social-sign-in/auth-keycloak)
- [Self-hosted OAuth](https://supabase.com/docs/guides/self-hosting/self-hosted-oauth)
- [Supabase Queues](https://supabase.com/docs/guides/queues)
- [Expose queues locally/self-hosted](https://supabase.com/docs/guides/queues/expose-self-hosted-queues)
- [Supabase Cron](https://supabase.com/docs/guides/cron)
- [Hosted Edge Function limits](https://supabase.com/docs/guides/functions/limits)
- [Self-hosted functions](https://supabase.com/docs/guides/self-hosting/self-hosted-functions)
- [Auth rate limits](https://supabase.com/docs/guides/auth/rate-limits)
- [Full-text search](https://supabase.com/docs/guides/database/full-text-search)
- [pgvector](https://supabase.com/docs/guides/database/extensions/pgvector)
