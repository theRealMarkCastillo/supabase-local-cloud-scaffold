"""Prepare application Edge Functions without modifying upstream vendor files."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'supabase/functions'
RUNTIME = ROOT / '.runtime'


def settings():
    config = tomllib.loads((ROOT / 'supabase/config.toml').read_text())
    policies = {}
    for folder in sorted(SOURCE.iterdir()):
        if not folder.is_dir() or folder.name.startswith('_'):
            continue
        if folder.name == 'main' or not re.fullmatch(r'[a-zA-Z0-9_-]+', folder.name):
            raise SystemExit('Reserved or invalid function name')
        values = config.get('functions', {}).get(folder.name, {})
        if values.get('enabled', True) is False:
            continue
        if values.get('entrypoint') not in (None, f'./functions/{folder.name}/index.ts') or not (folder / 'index.ts').is_file():
            raise SystemExit('Each function needs index.ts; custom entrypoints require an adapter')
        verify = values.get('verify_jwt', True)
        if not isinstance(verify, bool):
            raise SystemExit('verify_jwt must be boolean')
        mapping = values.get('import_map')
        if mapping:
            path = Path(mapping)
            if path.is_absolute() or '..' in path.parts or path.parts[0] != 'functions':
                raise SystemExit('Import map must be under supabase/functions')
            path = Path(*path.parts[1:])
        else:
            path = next((Path(folder.name) / name for name in ('deno.json', 'deno.jsonc') if (folder / name).is_file()), None)
            path = path or next((Path(name) for name in ('deno.json', 'deno.jsonc') if (SOURCE / name).is_file()), None)
        if path and not (SOURCE / path).is_file():
            raise SystemExit('Function import map is missing')
        policies[folder.name] = {'verify_jwt': verify, 'import_map': '/home/deno/functions/' + path.as_posix() if path else None}
    return policies


def prepare():
    policies = settings()
    main = (ROOT / 'vendor/supabase/volumes/functions/main/index.ts').read_text()
    guard = "  if (req.method !== 'OPTIONS' && VERIFY_JWT) {"
    mapping = 'const importMapPath = `/home/deno/functions/deno.jsonc`'
    if main.count(guard) != 1 or main.count(mapping) != 1:
        raise SystemExit('Pinned upstream function router changed; review adapter')
    main = main.replace(guard, "  const slug = new URL(req.url).pathname.split('/')[1];\n  const policies = JSON.parse(Deno.env.get('SCAFFOLD_FUNCTION_POLICIES') || '{}');\n  if (!Object.hasOwn(policies, slug)) return new Response('Not found', {status:404});\n  if (req.method !== 'OPTIONS' && policies[slug].verify_jwt !== false) {")
    main = main.replace(mapping, 'const importMapPath = policies[service_name].import_map || undefined')
    files = []
    hash_value = hashlib.sha256(main.encode() + json.dumps(policies, sort_keys=True).encode())
    for path in sorted(SOURCE.rglob('*')):
        if path.is_symlink():
            raise SystemExit('Symlinks in function source are refused')
        if not path.is_file():
            continue
        if path.name.startswith('.env') or path.suffix == '.pem' or 'node_modules' in path.parts:
            raise SystemExit('Keep secrets and installed dependencies outside function source')
        relative = path.relative_to(SOURCE)
        data = path.read_bytes()
        hash_value.update(relative.as_posix().encode() + b'\0' + data)
        files.append((relative, path))
    RUNTIME.mkdir(exist_ok=True, mode=0o700)
    target = RUNTIME / ('functions-' + hash_value.hexdigest()[:24])
    if target.exists():
        return target, policies
    stage = Path(tempfile.mkdtemp(prefix='functions-building-', dir=RUNTIME))
    try:
        for relative, path in files:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(path, destination)
            destination.chmod(0o600)
        (stage / 'main').mkdir(mode=0o700)
        (stage / 'main/index.ts').write_text(main)
        (stage / 'main/index.ts').chmod(0o600)
        stage.rename(target)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return target, policies


def create(name):
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,49}', name) or name == 'main':
        raise SystemExit('Use a lowercase function name with letters, digits and hyphens')
    target = SOURCE / name
    if target.exists():
        raise SystemExit('Function already exists')
    target.mkdir(parents=True)
    (target / 'index.ts').write_text("""// The default JWT policy is only the first check: verify the caller's user identity.
const origin = new URL(Deno.env.get('SUPABASE_PUBLIC_URL')!).origin;
const cors = {'Access-Control-Allow-Origin':origin, 'Access-Control-Allow-Headers':'authorization, apikey, content-type, x-client-info', 'Access-Control-Allow-Methods':'POST, OPTIONS', 'Vary':'Origin'};
Deno.serve(async (request) => {
  if (request.method === 'OPTIONS') return new Response(null,{status:204,headers:cors});
  const respond = (body:unknown,status=200) => Response.json(body,{status,headers:cors});
  if (request.method !== 'POST') return respond({error:'POST required'},405);
  const authorization=request.headers.get('authorization') || '';
  const identity=await fetch(Deno.env.get('SUPABASE_URL')+'/auth/v1/user',{headers:{apikey:Deno.env.get('SUPABASE_ANON_KEY')!,authorization}});
  if (!identity.ok) return respond({error:'Sign in first'},401);
  const user=await identity.json();
  return respond({message:'Hello from your function',user_id:user.id});
});
""")
    print('Created:', target.relative_to(ROOT), '; run make up to load it')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('new',))
    parser.add_argument('name')
    create(parser.parse_args().name)
