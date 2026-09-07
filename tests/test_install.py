import importlib.util
import json
import os
from pathlib import Path
import shutil
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


def inventory(path):
    """Capture files and links without following installed skill symlinks."""
    result = {}
    for item in sorted(path.rglob("*")):
        relative = str(item.relative_to(path))
        if item.is_symlink():
            result[relative] = ("link", os.readlink(item))
        elif item.is_file():
            result[relative] = ("file", item.read_bytes())
        elif item.is_dir():
            result[relative] = ("dir",)
    return result


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
        self.assertTrue(canonical.is_symlink())
        self.assertEqual(os.readlink(canonical), str(installer.SOURCE.resolve()))
        for host in (".claude", ".grok"):
            link = self.home / host / "skills/improve"
            self.assertTrue(link.is_symlink())
            self.assertEqual(os.readlink(link), "../../.agents/skills/improve")
            self.assertEqual(link.resolve(), installer.SOURCE.resolve())
        self.assertFalse(installer.exists(self.home / ".codex/skills/improve"))
        self.assertEqual(self.run_installer("--check").returncode, 0)

    def test_dry_run_and_check_never_write(self):
        self.assertEqual(self.run_installer().returncode, 0)
        self.assertEqual(self.run_installer("--check").returncode, 1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_fresh_install_and_repeat_are_idempotent(self):
        self.assertEqual(self.run_installer("--apply").returncode, 0)
        self.assert_installed()
        before = inventory(self.home)
        self.assertEqual(self.run_installer("--apply").returncode, 0)
        self.assertEqual(inventory(self.home), before)

    def test_matching_snapshot_is_replaced_by_a_link_and_archived(self):
        canonical = self.home / ".agents/skills/improve"
        shutil.copytree(installer.SOURCE, canonical)
        previous = inventory(canonical)
        self.assertEqual(self.run_installer("--apply").returncode, 0)
        self.assert_installed()
        backup = next((self.home / ".local/state/improve/backups").iterdir())
        self.assertEqual(inventory(backup / ".agents/skills/improve"), previous)

    def test_checkout_edits_additions_and_deletions_propagate_without_reinstall(self):
        source = Path(self.temporary.name) / "checkout/skills/improve"
        references = source / "references"
        references.mkdir(parents=True)
        (source / "SKILL.md").write_text("original skill")
        (references / "guide.md").write_text("original guide")
        (references / "obsolete.md").write_text("remove this reference")

        with patch.object(installer, "SOURCE", source):
            installer.apply(self.home, installer.plan(self.home))
            paths = [self.home / host / "skills/improve" for host in (".agents", ".claude", ".grok")]
            for path in paths:
                self.assertEqual((path / "SKILL.md").read_text(), "original skill")
                self.assertTrue((path / "references/obsolete.md").is_file())

            (source / "SKILL.md").write_text("updated skill")
            (references / "guide.md").write_text("updated guide")
            (references / "new.md").write_text("new reference")
            (references / "obsolete.md").unlink()

            for path in paths:
                self.assertEqual((path / "SKILL.md").read_text(), "updated skill")
                self.assertEqual((path / "references/guide.md").read_text(), "updated guide")
                self.assertEqual((path / "references/new.md").read_text(), "new reference")
                self.assertFalse((path / "references/obsolete.md").exists())
            self.assertEqual(installer.plan(self.home), [])

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
