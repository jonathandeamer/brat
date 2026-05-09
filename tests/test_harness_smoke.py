"""Validates harness mechanics with a runtime-built fake brat.

Independent of the real ./brat binary: writes a tiny Python script to
tmp_path, invokes it via the same subprocess.run(...) pattern
test_brat.py uses, and asserts byte-exact capture (including NUL bytes
and trailing newlines).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ECHO_SCRIPT = """\
import sys
if len(sys.argv) > 1:
    sys.stdout.buffer.write(b"\\n".join(a.encode() for a in sys.argv[1:]) + b"\\n")
sys.stderr.buffer.write(b"fake\\n")
sys.exit(len(sys.argv) - 1)
"""

NUL_SCRIPT = """\
import sys
sys.stdout.buffer.write(b"a\\x00b\\n")
"""

NEWLINE_SCRIPT = """\
import sys
sys.stdout.buffer.write(b"line\\n\\n\\n")
"""


def _write_script(tmp_path: Path, name: str, source: str) -> Path:
    p = tmp_path / name
    p.write_text(source)
    return p


def test_subprocess_capture_is_byte_exact(tmp_path: Path) -> None:
    fake = _write_script(tmp_path, "echo.py", ECHO_SCRIPT)
    result = subprocess.run(
        [sys.executable, str(fake), "one", "two"],
        cwd=str(tmp_path),
        capture_output=True,
        check=False,
    )
    assert result.stdout == b"one\ntwo\n"
    assert result.stderr == b"fake\n"
    assert result.returncode == 2


def test_nul_bytes_survive_capture(tmp_path: Path) -> None:
    """Confirms stdout capture preserves NUL bytes (relevant to case 8)."""
    fake = _write_script(tmp_path, "nul.py", NUL_SCRIPT)
    result = subprocess.run(
        [sys.executable, str(fake)],
        capture_output=True,
        check=False,
    )
    assert result.stdout == b"a\x00b\n"


def test_no_trailing_newline_strip(tmp_path: Path) -> None:
    """Confirms capture does NOT strip trailing newlines (the shell footgun)."""
    fake = _write_script(tmp_path, "nl.py", NEWLINE_SCRIPT)
    result = subprocess.run(
        [sys.executable, str(fake)],
        capture_output=True,
        check=False,
    )
    assert result.stdout == b"line\n\n\n"
