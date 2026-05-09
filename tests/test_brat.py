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

# Ratchet: bump when intentionally adding cases. Catches silent deletions.
MIN_CASES = 18

REQUIRED_CASE_ENTRIES = ("args", "expected.out", "expected.err", "expected.exit", "inputs")


def test_every_case_has_required_files() -> None:
    cases = _discover_cases()
    missing: list[str] = []
    for case_dir in cases:
        for entry in REQUIRED_CASE_ENTRIES:
            if not (case_dir / entry).exists():
                missing.append(f"{case_dir.name}/{entry}")
    assert not missing, f"incomplete cases: {missing}"


def test_case_count_floor() -> None:
    assert len(_discover_cases()) >= MIN_CASES, (
        f"fewer than {MIN_CASES} cases discovered; bump MIN_CASES intentionally if removing"
    )


def test_update_goldens_disabled_in_ci() -> None:
    if os.environ.get("CI") != "1":
        pytest.skip("only enforced in CI")
    assert os.environ.get("BRAT_UPDATE_GOLDENS") != "1", (
        "BRAT_UPDATE_GOLDENS=1 must not be set in CI"
    )


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

    Skips the case if the suite is running as root: every existing modes
    entry today is a chmod intended to *deny* access (e.g. 0o000 for the
    EACCES bratism), and root bypasses DAC, so the case cannot exercise
    the path it claims to. Common in Docker/CI containers that run as
    root.
    """
    modes_file = case_dir / "modes"
    if not modes_file.exists():
        return []
    if os.geteuid() == 0:
        pytest.skip(
            f"case {case_dir.name} uses chmod-based access denial which is "
            "ineffective under root; run as a non-root user"
        )
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

    before = sorted(os.listdir(inputs_dir))
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
    after = sorted(os.listdir(inputs_dir))
    assert before == after, f"brat mutated inputs/ in case {case_dir.name}: {before} -> {after}"

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
    expected_exit = int(expected_exit_path.read_text().strip())
    assert 0 <= expected_exit < 256, (
        f"expected.exit in {case_dir.name} out of range: {expected_exit}"
    )
    assert actual_exit == expected_exit, (
        f"exit code mismatch for case {case_dir.name}"
    )
