"""Exercise migrations in a disposable database inside this project's local DB service."""
from pathlib import Path
from contextlib import redirect_stdout
import io
import sys
import tempfile
import uuid
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import stack
import migrations

stack.render()
name='starter_checks_'+uuid.uuid4().hex

def query(sql,database='postgres'):
 return stack.compose('exec','-T','db','psql','-At','-v','ON_ERROR_STOP=1','-U','postgres','-d',database,input=sql,text=True,capture_output=True).stdout.strip()

def test_compose(*args,**kwargs):
 args=list(args);index=args.index('-d');args[index+1]=name
 return stack.compose(*args,**kwargs)

query(f'CREATE DATABASE "{name}";')
try:
 with tempfile.TemporaryDirectory(prefix='supabase-migration-checks-') as temp:
  root=Path(temp);directory=root/'supabase/migrations';directory.mkdir(parents=True)
  first=directory/'20260101000000_base.sql'
  original='CREATE TABLE public.probe(id serial PRIMARY KEY, value text); INSERT INTO public.probe(value) VALUES (\'synthetic\'); ALTER TABLE public.probe ENABLE ROW LEVEL SECURITY; GRANT SELECT ON public.probe TO anon;'
  first.write_text(original)
  with patch.object(migrations,'ROOT',root),patch.object(migrations,'DIRECTORY',directory),redirect_stdout(io.StringIO()):
   migrations.apply(test_compose);migrations.apply(test_compose)
   assert query('SELECT count(*) FROM public.probe;',name)=='1'
   assert query('SET ROLE anon; SELECT count(*) FROM public.probe;',name).endswith('0')
   first.write_text(original+' INSERT INTO public.probe(value) VALUES (\'changed\');')
   try:migrations.apply(test_compose)
   except SystemExit:pass
   else:raise AssertionError('Edited migration was accepted')
   assert query('SELECT count(*) FROM public.probe;',name)=='1'
   first.write_text(original)
   failed=directory/'20260101000001_failed.sql';failed.write_text('CREATE TABLE public.must_rollback(id int); SELECT * FROM missing_synthetic_table;')
   try:migrations.apply(test_compose)
   except SystemExit:pass
   else:raise AssertionError('Failed migration was accepted')
   assert query("SELECT to_regclass('public.must_rollback') IS NULL;",name)=='t'
   assert query('SELECT count(*) FROM supabase_migrations.schema_migrations;',name)=='1'
   failed.unlink()
   (directory/'20260101000002_followup.sql').write_text('ALTER TABLE public.probe ADD COLUMN extra text;')
   migrations.apply(test_compose)
   assert query('SELECT count(*) FROM supabase_migrations.schema_migrations;',name)=='2'
 print('PASS: repeat execution, edited migration refusal, RLS, transactional rollback and incremental history')
finally:
 query(f'DROP DATABASE "{name}";')
 print('Removed only the disposable migration-check database.')
