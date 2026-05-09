"""Pytest fixtures for the brat test suite."""
import os
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def brat_bin() -> Path:
    """Absolute path to the brat binary.

    Source: $BRAT_BIN if set, else <project_root>/brat.
    Fails the session if the path is not an executable file.
    """
    explicit = os.environ.get("BRAT_BIN")
    candidate = (
        Path(explicit).resolve() if explicit else (PROJECT_ROOT / "brat").resolve()
    )
    if not candidate.is_file():
        pytest.fail(
            f"brat binary not found at {candidate}. "
            "Build brat first or set BRAT_BIN to an existing path.",
            pytrace=False,
        )
    if not os.access(candidate, os.X_OK):
        pytest.fail(
            f"brat binary at {candidate} is not executable.",
            pytrace=False,
        )
    return candidate
