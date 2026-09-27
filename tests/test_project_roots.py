import importlib.machinery, importlib.util, os, subprocess, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
loader=importlib.machinery.SourceFileLoader('roots',str(Path(__file__).parents[1]/'cc-skill-usage'))
spec=importlib.util.spec_from_loader(loader.name,loader);usage=importlib.util.module_from_spec(spec);loader.exec_module(usage)

class ProjectRoots(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name).resolve();self.home=self.base/'home';self.home.mkdir();self.repo=self.base/'repo';self.repo.mkdir()
  subprocess.run(['git','init','-q',str(self.repo)],check=True)
  self.old=Path.cwd();os.chdir(self.repo)
  self.env=patch.dict(os.environ,{},clear=False);self.env.start();os.environ.pop('CC_SKILL_ROOTS',None)
  self.mock=patch.object(Path,'home',return_value=self.home);self.mock.start()
 def tearDown(self):
  os.chdir(self.old);self.mock.stop();self.env.stop();self.tmp.cleanup()
 def skill(self,root):
  p=root/'demo/SKILL.md';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('---\nname: demo\n---\nbody\n');return p
 def test_project_roots_and_nested_cwd(self):
  paths=[self.skill(self.repo/d/'skills') for d in ['.agents','.claude','.codex']]
  nested=self.repo/'src/a';nested.mkdir(parents=True);os.chdir(nested)
  for p in paths:self.assertEqual(usage.validated_skill(p,'demo')[0],p)
 def test_external_git_worktree(self):
  subprocess.run(['git','-C',str(self.repo),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','--allow-empty','-qm','fixture'],check=True)
  work=self.base/'external';subprocess.run(['git','-C',str(self.repo),'worktree','add','-qb','test',str(work)],check=True)
  p=self.skill(work/'.agents/skills');os.chdir(work);self.assertEqual(usage.validated_skill(p,'demo')[0],p)
 def test_non_git_current_project(self):
  root=self.base/'plain';root.mkdir();p=self.skill(root/'.agents/skills');os.chdir(root)
  self.assertEqual(usage.validated_skill(p,'demo')[0],p)
 def test_plugins_and_global(self):
  for d in ['.codex/plugins/cache/vendor/plugin/1/skills','.claude/plugins/cache/vendor/plugin/1/skills','.agents/skills']:
   p=self.skill(self.home/d);self.assertEqual(usage.validated_skill(p,'demo')[0],p)
 def test_reject_sibling_repository(self):
  p=self.skill(self.base/'sibling/.agents/skills')
  with self.assertRaisesRegex(ValueError,'outside allowed'):usage.validated_skill(p,'demo')
 def test_reject_symlink_escape(self):
  outside=self.skill(self.base/'outside');root=self.repo/'.agents/skills';root.mkdir(parents=True);(root/'escaped').symlink_to(outside.parent)
  with self.assertRaisesRegex(ValueError,'outside allowed'):usage.validated_skill(root/'escaped/SKILL.md','demo')
 def test_reject_root_symlink_escape(self):
  outside=self.base/'outside';p=self.skill(outside);(self.repo/'.agents').mkdir();(self.repo/'.agents/skills').symlink_to(outside)
  with self.assertRaisesRegex(ValueError,'outside allowed'):usage.validated_skill(p,'demo')
 def test_explicit_roots_remain_exclusive(self):
  os.environ['CC_SKILL_ROOTS']=str(self.home/'allowed');p=self.skill(self.repo/'.agents/skills')
  with self.assertRaisesRegex(ValueError,'outside allowed'):usage.validated_skill(p,'demo')
if __name__=='__main__':unittest.main()
