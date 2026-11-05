# Supabase local/cloud starter

Independent new-project scaffold. Local Docker Compose testing is expected. Do not
provision or deploy cloud services without an explicit user request. Never push
without explicit authorization. Keep vendor/supabase unmodified, retain provenance
and licenses, and place adaptations in scripts/compose/application source.

Use versioned SQL migrations with RLS/grants, preserve checksums and migration history,
and verify anonymous/two-user access. No browser service-role keys. Local .env and
.runtime are private, ignored and excluded from Docker context. Function secrets go
in private .env.functions, never source/config examples. JWT verification does not
by itself prove a signed-in user. Public webhook handlers must verify signatures.

New projects default to localhost with independent names/ports/volumes/credentials.
Never tunnel gateway/Studio, database or email administration. No destructive reset
command or production data copying by default. Run make check, make test, make up,
and make smoke for runtime changes; document executed versus pending validation.
