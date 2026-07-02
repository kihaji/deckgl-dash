"""Tests that the package version is single-sourced and consistent across all files (issue #8 / T-01)."""
import importlib.util
import re
from pathlib import Path

import deckgl_dash

PROJECT_ROOT = Path(__file__).parent.parent

_spec = importlib.util.spec_from_file_location("check_versions", PROJECT_ROOT / "scripts" / "check_versions.py")
assert _spec is not None and _spec.loader is not None
check_versions = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_versions)


def _pyproject_version() -> str:
    match = re.search(r'^version = "([^"]+)"', (PROJECT_ROOT / "pyproject.toml").read_text(), re.MULTILINE)
    assert match is not None, "no version found in pyproject.toml"
    return match.group(1)


def test_version_sources_agree():
    versions = check_versions.collect_versions()
    assert len(set(versions.values())) == 1, f"version sources disagree: {versions}"


def test_runtime_version_matches_pyproject():
    assert deckgl_dash.__version__ == _pyproject_version()
