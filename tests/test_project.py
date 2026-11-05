"""Offline checks for new-project credentials, schema history and function boundaries."""
from pathlib import Path
from contextlib import redirect_stdout
import importlib.util
import io
import tempfile
import unittest
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,REPO/'scripts'/f'{name}.py')
 value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
migrations=module('migrations');functions=module('functions');stack=module('stack')

class ProjectTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name).resolve()
 def test_migration_names_are_unique_and_ordered(self):
  with patch.object(migrations,'ROOT',self.root),patch.object(migrations,'DIRECTORY',self.root/'supabase/migrations'),redirect_stdout(io.StringIO()):
   first=migrations.create('add_projects');second=migrations.create('add_members')
   self.assertNotEqual(first.name,second.name)
   self.assertEqual(migrations.ordered(),sorted([first,second]))
   with self.assertRaises(SystemExit):migrations.create('../unsafe')
 def test_duplicate_versions_and_symlinked_sql_are_refused(self):
  directory=self.root/'migrations';directory.mkdir()
  first=directory/'20260101000000_first.sql';first.write_text('SELECT 1;')
  second=directory/'20260101000000_second.sql';second.write_text('SELECT 2;')
  with patch.object(migrations,'DIRECTORY',directory):
   with self.assertRaises(SystemExit):migrations.ordered()
   second.unlink();first.unlink();first.symlink_to('/etc/hosts')
   with self.assertRaises(SystemExit):migrations.ordered()
 def test_transaction_control_is_rejected_before_database_access(self):
  directory=self.root/'migrations';directory.mkdir()
  (directory/'20260101000000_bad.sql').write_text('COMMIT;')
  with patch.object(migrations,'DIRECTORY',directory):
   with self.assertRaises(SystemExit):migrations.apply(lambda *args,**kwargs:self.fail('database access'))
 def config(self,text=''):
  source=self.root/'supabase/functions';source.mkdir(parents=True)
  (self.root/'supabase/config.toml').write_text(text)
  return source
 def test_function_jwt_default_and_public_policy_are_independent(self):
  source=self.config('[functions.webhook]\nverify_jwt=false\n')
  for name in ['private','webhook']:
   (source/name).mkdir();(source/name/'index.ts').write_text('Deno.serve(()=>new Response("ok"));')
  with patch.object(functions,'ROOT',self.root),patch.object(functions,'SOURCE',source):
   values=functions.settings()
   self.assertTrue(values['private']['verify_jwt']);self.assertFalse(values['webhook']['verify_jwt'])
 def test_import_map_escape_is_refused(self):
  source=self.config('[functions.private]\nimport_map="../outside.json"\n')
  (source/'private').mkdir();(source/'private/index.ts').write_text('')
  with patch.object(functions,'ROOT',self.root),patch.object(functions,'SOURCE',source):
   with self.assertRaises(SystemExit):functions.settings()
 def test_fresh_credentials_and_existing_environment_protection(self):
  (self.root/'vendor/supabase').mkdir(parents=True)
  (self.root/'vendor/supabase/.env.example').write_text('POSTGRES_DB=postgres\n')
  environment=self.root/'.env'
  with patch.object(stack,'ROOT',self.root),patch.object(stack,'ENV',environment),redirect_stdout(io.StringIO()):
   stack.initialize({'name':'unit-project','port':8097,'admin_port':19807,'mail_port':18032})
   first=stack.env_values(environment)
   self.assertEqual(first['PUBLIC_URL'],'http://localhost:8097')
   self.assertEqual(first['FRONTEND_KIND'],'tanstack')
   self.assertEqual(environment.stat().st_mode&0o777,0o600)
   environment.unlink();stack.initialize({'name':'unit-project'})
   self.assertNotEqual(first['JWT_SECRET'],stack.env_values(environment)['JWT_SECRET'])
   environment.write_text('EXISTING=preserve\n')
   with self.assertRaises(SystemExit):stack.initialize()
   self.assertEqual(environment.read_text(),'EXISTING=preserve\n')

if __name__=='__main__':unittest.main()
