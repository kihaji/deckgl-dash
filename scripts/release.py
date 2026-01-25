#!/usr/bin/env python3
"""Create a release: bump version, build, commit, and tag.

Usage:
    python scripts/release.py 0.2.0
    python scripts/release.py 0.2.0 --dry-run  # Preview without making changes
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

FILES_TO_UPDATE = [
    ("pyproject.toml", r'version = "[^"]+"', 'version = "{version}"'),
    ("package.json", r'"version": "[^"]+"', '"version": "{version}"'),
    ("deckgl_dash/package-info.json", r'"version": "[^"]+"', '"version": "{version}"'),
]


def run(cmd: str, dry_run: bool = False) -> bool:
    """Run a shell command."""
    print(f"  → {cmd}")
    if dry_run:
        return True
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)
    return result.returncode == 0


def bump_version(new_version: str, dry_run: bool = False) -> bool:
    """Update version in all configuration files."""
    print(f"\n📝 Bumping version to {new_version}")

    for filepath, pattern, replacement in FILES_TO_UPDATE:
        full_path = PROJECT_ROOT / filepath
        if not full_path.exists():
            print(f"  ⚠ Warning: {filepath} not found, skipping")
            continue

        content = full_path.read_text()
        new_content = re.sub(pattern, replacement.format(version=new_version), content, count=1)

        if content == new_content:
            print(f"  ⚠ Warning: No version found in {filepath}")
        else:
            if not dry_run:
                full_path.write_text(new_content)
            print(f"  ✓ Updated {filepath}")

    return True


def release(version: str, dry_run: bool = False) -> None:
    """Execute the full release workflow."""
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print(f"❌ Error: Invalid version format '{version}'. Expected format: X.Y.Z")
        sys.exit(1)

    tag = f"v{version}"

    print(f"\n🚀 Creating release {tag}")
    if dry_run:
        print("   (DRY RUN - no changes will be made)\n")

    # Step 1: Bump version
    if not bump_version(version, dry_run):
        sys.exit(1)

    # Step 2: Build JavaScript
    print("\n📦 Building JavaScript bundle")
    if not run("npm run build:js", dry_run):
        print("❌ Error: npm build failed")
        sys.exit(1)

    # Step 3: Git add and commit
    print("\n📝 Committing changes")
    if not run("git add -A", dry_run):
        sys.exit(1)
    if not run(f'git commit -m "Release {tag}"', dry_run):
        print("❌ Error: git commit failed (maybe no changes?)")
        sys.exit(1)

    # Step 4: Create tag
    print("\n🏷️  Creating tag")
    if not run(f"git tag {tag}", dry_run):
        print("❌ Error: git tag failed (tag may already exist)")
        sys.exit(1)

    # Success!
    print(f"\n✅ Release {tag} created successfully!")
    print("\n📤 To publish, run:")
    print(f"   git push && git push --tags")
    print(f"\n   This will trigger the GitHub Action to publish to PyPI.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/release.py <version> [--dry-run]")
        print("Example: python scripts/release.py 0.2.0")
        print("         python scripts/release.py 0.2.0 --dry-run")
        sys.exit(1)

    version = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    release(version, dry_run)
