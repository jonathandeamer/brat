"""Parametrized walker: one test per tests/cases/<case>/ folder.

Set BRAT_UPDATE_GOLDENS=1 to overwrite expected.* with captured output
instead of asserting. Use only when you trust brat's current output.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

CASES_DIR = Path(__file__).resolve().parent / "cases"


def _discover_cases() -> list[Path]:
    if not CASES_DIR.exists():
        return []
    return sorted(p for p in CASES_DIR.iterdir() if p.is_dir())


def _load_args(case_dir: Path) -> list[str]:
    """Parse the case's args file: one argument per line, trailing newline ignored.

    Empty file -> []. Blank lines mid-file are rejected: an empty-string argument
    is almost certainly a case-author bug, not an intentional invocation.
    """
    text = (case_dir / "args").read_text()
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    if any(a == "" for a in parts):
        raise ValueError(f"args file in {case_dir} contains a blank line")
    return parts


def _apply_modes(case_dir: Path) -> list[Path]:
    """Apply the case's optional modes file before the test runs.

    Reads `<case_dir>/modes` if present, with one `filename:octal` line per
    file under inputs/. Returns the list of paths whose modes were changed
    so the caller can restore them.
    """
    modes_file = case_dir / "modes"
    if not modes_file.exists():
        return []
    applied: list[Path] = []
    for line in modes_file.read_text().strip().splitlines():
        fname, octal = line.split(":", 1)
        target = case_dir / "inputs" / fname.strip()
        target.chmod(int(octal.strip(), 8))
        applied.append(target)
    return applied


@pytest.mark.parametrize(
    "case_dir",
    _discover_cases(),
    ids=lambda p: p.name,
)
def test_case(case_dir: Path, brat_bin: Path) -> None:
    args = _load_args(case_dir)
    inputs_dir = case_dir / "inputs"

    chmodded = _apply_modes(case_dir)
    try:
        result = subprocess.run(
            [str(brat_bin), *args],
            cwd=str(inputs_dir),
            capture_output=True,
            check=False,
        )
    finally:
        for target in chmodded:
            target.chmod(0o644)

    actual_out = result.stdout
    actual_err = result.stderr
    actual_exit = result.returncode

    expected_out_path = case_dir / "expected.out"
    expected_err_path = case_dir / "expected.err"
    expected_exit_path = case_dir / "expected.exit"

    if os.environ.get("BRAT_UPDATE_GOLDENS") == "1":
        expected_out_path.write_bytes(actual_out)
        expected_err_path.write_bytes(actual_err)
        expected_exit_path.write_text(f"{actual_exit}\n")
        pytest.skip("goldens updated")

    assert actual_out == expected_out_path.read_bytes(), (
        f"stdout mismatch for case {case_dir.name}"
    )
    assert actual_err == expected_err_path.read_bytes(), (
        f"stderr mismatch for case {case_dir.name}"
    )
    assert actual_exit == int(expected_exit_path.read_text().strip()), (
        f"exit code mismatch for case {case_dir.name}"
    )
