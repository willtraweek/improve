#!/usr/bin/env python3
"""Install one Improve snapshot for Codex, Claude Code, and Grok (Python 3)."""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from datetime import datetime, timezone


SOURCE = Path(__file__).resolve().parents[1] / "skills" / "improve"


def exists(path):
    return path.exists() or path.is_symlink()


def inventory(path):
    """Compare complete payloads, including removed references and hidden files."""
    result = {}
    for item in sorted(path.rglob("*")):
        relative = str(item.relative_to(path))
        if item.is_symlink():
            result[relative] = ("link", os.readlink(item))
        elif item.is_file():
            result[relative] = ("file", item.read_bytes())
        elif item.is_dir():
            result[relative] = ("dir",)
        else:
            raise ValueError(f"Unsupported file type: {item}")
    return result


def plan(home):
    if not (SOURCE / "SKILL.md").is_file():
        raise ValueError(f"Missing source skill: {SOURCE / 'SKILL.md'}")
    canonical = home / ".agents/skills/improve"
    actions = []
    if (canonical.is_symlink() or not canonical.is_dir()
            or inventory(canonical) != inventory(SOURCE)):
        actions.append(("copy", canonical, None))
    for host in (".claude", ".grok"):
        destination = home / host / "skills/improve"
        link = os.path.relpath(canonical, destination.parent)
        if not destination.is_symlink() or os.readlink(destination) != link:
            actions.append(("link", destination, link))
    legacy = home / ".codex/skills/improve"
    if exists(legacy):
        actions.append(("remove", legacy, None))

    # This local snapshot is no longer managed by the upstream skills CLI.
    for relative in (".local/state/skills/.skill-lock.json", ".agents/.skill-lock.json"):
        lock = home / relative
        if not exists(lock):
            continue
        data = json.loads(lock.read_text())
        if not isinstance(data, dict):
            raise ValueError(f"Unexpected skills lock format: {lock}")
        skills = data.get("skills", {})
        if not isinstance(skills, dict):
            raise ValueError(f"Unexpected skills lock format: {lock}")
        if "improve" in skills:
            del skills["improve"]
            actions.append(("untrack", lock, json.dumps(data, indent=2) + "\n"))

    # Replace skill-level links without writing through a shared install root.
    destinations = [destination for _, destination, _ in actions]
    if actions:
        destinations.append(home / ".local/state/improve/backups/placeholder")
    for destination in destinations:
        for parent in destination.parents:
            if parent == home:
                break
            if parent.is_symlink():
                raise ValueError(f"Install root is a symlink: {parent}")
    return actions


def remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def apply(home, actions):
    state = home / ".local/state/improve"
    state.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = state / "backups" / stamp
    completed = []
    with tempfile.TemporaryDirectory(prefix="stage-", dir=state) as temporary:
        staging = Path(temporary)
        # Finish all copying and serialization before touching active skills.
        for index, (kind, _, content) in enumerate(actions):
            staged = staging / str(index)
            if kind == "copy":
                shutil.copytree(SOURCE, staged, symlinks=True)
            elif kind == "link":
                staged.symlink_to(content, target_is_directory=True)
            elif kind == "untrack":
                staged.write_text(content)
        try:
            for index, (kind, destination, _) in enumerate(actions):
                previous = backup / destination.relative_to(home)
                destination.parent.mkdir(parents=True, exist_ok=True)
                had_previous = exists(destination)
                if had_previous:
                    previous.parent.mkdir(parents=True, exist_ok=True)
                    destination.rename(previous)
                completed.append((destination, previous, had_previous))
                if kind != "remove":
                    (staging / str(index)).rename(destination)
        except OSError:
            for destination, previous, had_previous in reversed(completed):
                remove(destination)
                if had_previous:
                    previous.rename(destination)
            raise
    if backup.exists():
        print(f"Previous installation archived: {backup}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home(),
                        help="Installation home (default: current user's home)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Apply the displayed migration")
    mode.add_argument("--check", action="store_true", help="Exit 1 if migration is needed")
    args = parser.parse_args()
    home = args.home.expanduser().resolve()
    try:
        actions = plan(home)
        if not actions:
            print("Improve is current for Codex, Claude Code, and Grok.")
            return 0
        for kind, destination, _ in actions:
            print(f"{kind:7} {destination}")
        if args.apply:
            apply(home, actions)
            print("Installed Improve for Codex, Claude Code, and Grok.")
        elif not args.check:
            print("Dry run. Use --apply to install; existing entries will be archived.")
        return int(args.check)
    except (OSError, ValueError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
