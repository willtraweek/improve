#!/usr/bin/env python3
"""Measure skill bytes against a pinned upstream revision, without a tokenizer."""

import argparse
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="03369ee6d7cafbfcecc4346539b05b3dc0a603bb")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])

    prefix = "skills/improve/"
    paths = git("ls-tree", "-r", "--name-only", args.baseline, "--", prefix).decode().splitlines()
    before = {p: len(git("show", f"{args.baseline}:{p}")) for p in paths}
    after = {str(p.relative_to(root)): p.stat().st_size for p in (root / prefix).rglob("*") if p.is_file()}
    entry = prefix + "SKILL.md"
    print("| Resource | Upstream bytes | Fork bytes | Reduction |")
    print("|---|---:|---:|---:|")
    for path in [entry, *sorted((before.keys() | after.keys()) - {entry})]:
        old, new = before.get(path, 0), after.get(path, 0)
        cut = f"{100 * (1 - new / old):.1f}%" if old else "new"
        print(f"| {path.removeprefix(prefix)} | {old:,} | {new:,} | {cut} |")
    old, new = sum(before.values()), sum(after.values())
    print(f"| **Total installed skill** | **{old:,}** | **{new:,}** | **{100 * (1 - new / old):.1f}%** |")


if __name__ == "__main__":
    main()
