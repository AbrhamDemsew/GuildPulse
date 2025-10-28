"""Tests for mypy configuration."""

import tomllib


def test_mypy_strict_mode():
    """Test mypy is configured with strict type checking."""
    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)

    mypy_config = config.get("tool", {}).get("basedpyright", {})

    # Check for strict type checking
    assert mypy_config.get("typeCheckingMode") == "strict", (
        "Mypy should be configured with strict type checking"
    )

    # Check for reporting of common issues
    assert mypy_config.get("reportMissingTypeArgument") == "warning", (
        "Should report missing type arguments"
    )

    assert mypy_config.get("reportUnknownMemberType") == "warning", (
        "Should report unknown member types"
    )
