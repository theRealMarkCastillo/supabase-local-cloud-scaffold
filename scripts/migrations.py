"""Create and apply versioned local SQL migrations; no remote database target."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse
import hashlib
import re
import subprocess
from sql_safety import validate_sql

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'supabase/migrations'


def ordered():
    files = sorted(DIRECTORY.glob('*.sql'))
    versions = []
    for path in files:
        match = re.fullmatch(r'(\d{14})_([a-z0-9_]+)\.sql', path.name)
        if not match or path.is_symlink():
            raise SystemExit('Migrations require regular YYYYMMDDHHMMSS_description.sql files')
        versions.append(match.group(1))
    if len(set(versions)) != len(versions):
        raise SystemExit('Duplicate migration versions')
    return files


def create(name):
    if not re.fullmatch(r'[a-z][a-z0-9_]{0,79}', name):
        raise SystemExit('Use a lowercase migration description with letters, digits and underscores')
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    for offset in range(60):
        version = (now + timedelta(seconds=offset)).strftime('%Y%m%d%H%M%S')
        if any(DIRECTORY.glob(version + '_*.sql')):
            continue
        path = DIRECTORY / (version + '_' + name + '.sql')
        with path.open('x') as output:
            output.write('-- Add reviewed schema, grants and RLS here. Keep synthetic fixtures separate.\n')
        print('Created:', path.relative_to(ROOT))
        return path
    raise SystemExit('Could not allocate a migration version; retry later')


def apply(compose):
    for path in ordered():
        sql = path.read_text()
        validate_sql(sql)
        version = path.name.split('_', 1)[0]
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        command = rf"""BEGIN;
SELECT pg_advisory_xact_lock(879312);
SET LOCAL standard_conforming_strings=on;
CREATE SCHEMA IF NOT EXISTS scaffold_internal;
REVOKE ALL ON SCHEMA scaffold_internal FROM PUBLIC, anon, authenticated;
CREATE TABLE IF NOT EXISTS scaffold_internal.migrations(version text PRIMARY KEY, checksum text NOT NULL);
CREATE SCHEMA IF NOT EXISTS supabase_migrations;
CREATE TABLE IF NOT EXISTS supabase_migrations.schema_migrations(version text PRIMARY KEY, statements text[], name text);
SELECT EXISTS(SELECT 1 FROM scaffold_internal.migrations WHERE version='{version}') AS applied \gset
\if :applied
DO $$ BEGIN IF (SELECT checksum FROM scaffold_internal.migrations WHERE version='{version}') <> '{checksum}' THEN RAISE EXCEPTION 'Applied migration was edited'; END IF; END $$;
\else
DO $$ BEGIN IF EXISTS(SELECT 1 FROM supabase_migrations.schema_migrations WHERE version >= '{version}') THEN RAISE EXCEPTION 'Existing or later history requires baseline review'; END IF; END $$;
{sql}
INSERT INTO supabase_migrations.schema_migrations(version,name) VALUES ('{version}','{path.stem}');
INSERT INTO scaffold_internal.migrations VALUES ('{version}','{checksum}');
\endif
COMMIT;
"""
        log = ROOT / '.runtime/migration.log'
        log.parent.mkdir(exist_ok=True, mode=0o700)
        with log.open('wb') as output:
            log.chmod(0o600)
            try:
                compose('exec', '-T', 'db', 'psql', '-v', 'ON_ERROR_STOP=1', '-U', 'postgres', '-d', 'postgres', input=command.encode(), stdout=output, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                raise SystemExit('Migration failed; inspect private .runtime/migration.log. Earlier files may have committed.')
        print('Migration ready:', path.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('new',))
    parser.add_argument('name')
    create(parser.parse_args().name)
