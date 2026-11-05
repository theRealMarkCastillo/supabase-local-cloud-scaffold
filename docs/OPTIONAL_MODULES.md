# Optional dependencies

Start with the default backend and add a module when application behavior needs it.
The template does not provision these modules or claim their runtime validation.

| Need | Candidate pattern | Application work |
| --- | --- | --- |
| Social sign-in | Supabase Auth Google/Apple providers | Separate client registrations, callback URLs, secrets, linking/logout tests |
| Shared enterprise identity | Keycloak as an upstream Supabase Auth provider | Stable issuer reachable by browser/Auth, per-app clients; keep Supabase session/RLS boundary |
| Background jobs | Dedicated worker using a durable queue | Idempotency, retries, leases, shutdown and ownership; choose Postgres-backed queue or Redis explicitly |
| Scheduled tasks | Reviewed database schedule or scheduler container | Single active schedule, destination credentials, run history and duplicate prevention |
| Cache/rate limiting | Redis when justified | Correctness without cached data, TTLs, persistence/eviction and outage handling |
| External file storage | Supported S3-compatible backend | Bucket credentials, endpoint/TLS, backup, private downloads and ownership checks |
| Observability | Structured logs plus chosen metrics/tracing/error service | Redact secrets/tokens, retention, resource limits and actionable health checks |
| AI/payment/email providers | Server-side adapter with scoped credentials | Explicit real-provider opt-in, fake/synthetic fixtures and webhook verification |

Supabase Storage already serves the demo's files; a separate MinIO container is not
required for the local file-backed configuration. Supabase Auth already provides
identity. The Edge Runtime is useful for request handlers; long-running or durable
work should use a suitable worker/queue design rather than assuming a request lives
forever. SMTP capture is local-only; it is not delivery infrastructure for real users.

The optional Studio/meta profile is available through make admin. The upstream-derived
pooler profile is configuration-validated, but its use from this app is not exercised.
GraphQL and additional upstream storage/analytics variants are not app-tested here.

References:
[Supabase Keycloak](https://supabase.com/docs/guides/auth/social-sign-in/auth-keycloak),
[self-hosted OAuth](https://supabase.com/docs/guides/self-hosting/self-hosted-oauth),
[Supabase queues](https://supabase.com/docs/guides/queues),
[Supabase cron](https://supabase.com/docs/guides/cron).
