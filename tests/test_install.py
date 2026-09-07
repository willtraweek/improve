import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install.py"
spec = importlib.util.spec_from_file_location("installer", INSTALLER)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / "home"
        self.home.mkdir()

    def run_installer(self, *args):
        return subprocess.run(
            [sys.executable, str(INSTALLER), "--home", str(self.home), *args],
            text=True, capture_output=True, check=False,
        )

    def write(self, relative, content):
        destination = self.home / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
        return destination

    def assert_installed(self):
        canonical = self.home / ".agents/skills/improve"
        self.assertFalse(canonical.is_symlink())
        self.assertEqual(installer.inventory(canonical), installer.inventory(installer.SOURCE))
        for host in (".claude", ".grok"):
            link = self.home / host / "skills/improve"
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), canonical)
        self.assertFalse(installer.exists(self.home / ".codex/skills/improve"))
        self.assertEqual(self.run_installer("--check").returncode, 0)

    def test_dry_run_and_check_never_write(self):
        self.assertEqual(self.run_installer().returncode, 0)
        self.assertEqual(self.run_installer("--check").returncode, 1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_fresh_install_and_repeat_are_idempotent(self):
        self.assertEqual(self.run_installer("--apply").returncode, 0)
        self.assert_installed()
        before = installer.inventory(self.home)
        self.assertEqual(self.run_installer("--apply").returncode, 0)
        self.assertEqual(installer.inventory(self.home), before)

    def test_migration_archives_old_payloads_and_preserves_unrelated_state(self):
        self.write(".agents/skills/improve/SKILL.md", "old shared skill")
        self.write(".agents/skills/improve/references/obsolete.md", "old reference")
        self.write(".codex/skills/improve/SKILL.md", "old codex skill")
        unrelated = self.write(".claude/skills/unrelated/SKILL.md", "keep me")
        for host in (".claude", ".grok"):
            folder = self.home / host / "skills"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "improve").symlink_to("../../.agents/skills/improve")
        lock_data = {"version": 3, "skills": {"improve": {"source": "shadcn/improve"},
                     "unrelated": {"source": "someone/else"}}, "dismissed": {"intro": True}}
        lock = self.write(".local/state/skills/.skill-lock.json", json.dumps(lock_data))
        result = self.run_installer("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_installed()
        self.assertEqual(unrelated.read_text(), "keep me")
        backup = next((self.home / ".local/state/improve/backups").iterdir())
        self.assertEqual((backup / ".agents/skills/improve/SKILL.md").read_text(), "old shared skill")
        self.assertEqual((backup / ".codex/skills/improve/SKILL.md").read_text(), "old codex skill")
        self.assertEqual(json.loads((backup / ".local/state/skills/.skill-lock.json").read_text()), lock_data)
        del lock_data["skills"]["improve"]
        self.assertEqual(json.loads(lock.read_text()), lock_data)
        self.assertFalse((self.home / ".agents/skills/improve/references/obsolete.md").exists())

    def test_replacing_skill_symlinks_does_not_change_their_targets(self):
        external = Path(self.temporary.name) / "external"
        external.mkdir()
        (external / "SKILL.md").write_text("leave target alone")
        for host in (".agents", ".claude", ".codex", ".grok"):
            folder = self.home / host / "skills"
            folder.mkdir(parents=True)
            (folder / "improve").symlink_to(external, target_is_directory=True)
        self.assertEqual(self.run_installer("--apply").returncode, 0)
        self.assert_installed()
        self.assertEqual((external / "SKILL.md").read_text(), "leave target alone")

    def test_invalid_lock_fails_before_changing_active_skills(self):
        active = self.write(".agents/skills/improve/SKILL.md", "old skill")
        self.write(".local/state/skills/.skill-lock.json", "not json")
        self.assertEqual(self.run_installer("--apply").returncode, 2)
        self.assertEqual(active.read_text(), "old skill")
        self.assertFalse((self.home / ".local/state/improve").exists())

    def test_shared_symlink_root_is_not_mutated(self):
        external = Path(self.temporary.name) / "external"
        external.mkdir()
        (self.home / ".agents").symlink_to(external, target_is_directory=True)
        self.assertEqual(self.run_installer("--apply").returncode, 2)
        self.assertEqual(list(external.iterdir()), [])

    def test_failure_restores_the_previous_active_installation(self):
        old = self.write(".agents/skills/improve/SKILL.md", "old skill")
        codex = self.write(".codex/skills/improve/SKILL.md", "old codex")
        lock = self.write(".local/state/skills/.skill-lock.json", '{"skills":{"improve":{}}}')
        rename = Path.rename

        def fail_grok(source, destination):
            if source.parent.name.startswith("stage-") and destination == self.home / ".grok/skills/improve":
                raise OSError("simulated install failure")
            return rename(source, destination)

        actions = installer.plan(self.home)
        with patch.object(Path, "rename", fail_grok):
            with self.assertRaisesRegex(OSError, "simulated install failure"):
                installer.apply(self.home, actions)
        self.assertEqual(old.read_text(), "old skill")
        self.assertEqual(codex.read_text(), "old codex")
        self.assertIn("improve", json.loads(lock.read_text())["skills"])
        for host in (".claude", ".grok"):
            self.assertFalse(installer.exists(self.home / host / "skills/improve"))


if __name__ == "__main__":
    unittest.main()
