"""Tests for Dockerfile optimization."""


def test_dockerfile_uses_buildkit_cache():
    """Test Dockerfile uses BuildKit cache mounts for uv."""
    with open("Dockerfile", "r") as f:
        content = f.read()

    # Check for cache mount pattern
    assert "--mount=type=cache" in content, "Dockerfile should use BuildKit cache mounts"
    assert "/root/.cache/uv" in content, "Dockerfile should cache uv cache"


def test_dockerfile_multistage():
    """Test Dockerfile uses multi-stage build."""
    with open("Dockerfile", "r") as f:
        content = f.read()

    # Check for FROM statements (multiple = multi-stage)
    from_count = content.count("FROM ")
    assert from_count >= 2, "Dockerfile should use multi-stage build (multiple FROM statements)"


def test_dockerfile_non_root_user():
    """Test Dockerfile uses non-root user."""
    with open("Dockerfile", "r") as f:
        content = f.read()

    assert "USER botuser" in content or "USER appuser" in content or "USER nonroot" in content, (
        "Dockerfile should use non-root user"
    )
