"""Tests for Silver-compliant Dockerfile."""

from pathlib import Path


def test_dockerfile_copies_full_repo():
    content = Path("Dockerfile").read_text(encoding="utf-8")
    assert "COPY . ." in content, "Dockerfile must copy full repo including .git"


def test_dockerfile_installs_git():
    content = Path("Dockerfile").read_text(encoding="utf-8")
    assert "git" in content, "Dockerfile must install git for task-based resets"


def test_dockerfile_pinned_python_base():
    content = Path("Dockerfile").read_text(encoding="utf-8")
    assert "python:3.12.9-slim-bookworm" in content


def test_dockerfile_non_root_user():
    content = Path("Dockerfile").read_text(encoding="utf-8")
    assert "USER guildpulse" in content


def test_dockerfile_no_unpinned_pip_upgrade():
    content = Path("Dockerfile").read_text(encoding="utf-8").lower()
    assert "pip install --upgrade pip" not in content
