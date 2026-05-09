"""One-off script that populates tests/cases/<case>/ for the 12 spec cases.

Re-run with `python3 -m tests._lib.bootstrap` to overwrite goldens after a
spec change. Once brat exists, `BRAT_UPDATE_GOLDENS=1 pytest` is the
authoritative regen path; running this bootstrap at that point would
overwrite brat-verified goldens with spec-derived ones and should only
be done when the spec itself has changed.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from tests._lib.header import block_header

CASES_DIR = Path(__file__).resolve().parent.parent / "cases"


def write_case(
    name: str,
    args: list[str],
    inputs: dict[str, bytes],
    subdirs: list[str],
    expected_out: bytes,
    expected_err: bytes,
    expected_exit: int,
) -> None:
    case_dir = CASES_DIR / name
    if case_dir.exists():
        shutil.rmtree(case_dir)
    (case_dir / "inputs").mkdir(parents=True)
    (case_dir / "args").write_text("\n".join(args) + ("\n" if args else ""))
    for fname, content in inputs.items():
        (case_dir / "inputs" / fname).write_bytes(content)
    for d in subdirs:
        (case_dir / "inputs" / d).mkdir()
    (case_dir / "expected.out").write_bytes(expected_out)
    (case_dir / "expected.err").write_bytes(expected_err)
    (case_dir / "expected.exit").write_text(f"{expected_exit}\n")


def main() -> None:
    # 1: empty file
    write_case(
        "empty",
        args=["empty.txt"],
        inputs={"empty.txt": b""},
        subdirs=[],
        expected_out=block_header("empty.txt"),
        expected_err=b"",
        expected_exit=0,
    )

    # 2: one-line file, no trailing newline
    write_case(
        "one-line-no-eol",
        args=["hello.txt"],
        inputs={"hello.txt": b"hi"},
        subdirs=[],
        expected_out=block_header("hello.txt") + b"hi" + b"\n",
        expected_err=b"",
        expected_exit=0,
    )

    # 3: multi-line file with trailing newline
    write_case(
        "multiline-with-eol",
        args=["greet.txt"],
        inputs={"greet.txt": b"hi\nbye\n"},
        subdirs=[],
        expected_out=block_header("greet.txt") + b"hi\nbye\n",
        expected_err=b"",
        expected_exit=0,
    )

    # 4: multi-file invocation
    write_case(
        "multi-file",
        args=["a.txt", "b.txt"],
        inputs={"a.txt": b"alpha\n", "b.txt": b"beta\n"},
        subdirs=[],
        expected_out=(
            block_header("a.txt") + b"alpha\n"
            + block_header("b.txt") + b"beta\n"
        ),
        expected_err=b"",
        expected_exit=0,
    )

    # 5: uppercase filename → header lowercased
    write_case(
        "uppercase-name",
        args=["README.MD"],
        inputs={"README.MD": b"shouty\n"},
        subdirs=[],
        expected_out=block_header("README.MD") + b"shouty\n",
        expected_err=b"",
        expected_exit=0,
    )

    # 6: long filename (>46 chars) → block grows; no trailing pad
    long_name = "x" * 47
    write_case(
        "long-name",
        args=[long_name],
        inputs={long_name: b"long\n"},
        subdirs=[],
        expected_out=block_header(long_name) + b"long\n",
        expected_err=b"",
        expected_exit=0,
    )

    # 7: unicode passthrough
    unicode_body = "naïve café 🥐\n".encode("utf-8")
    write_case(
        "unicode",
        args=["unicode.txt"],
        inputs={"unicode.txt": unicode_body},
        subdirs=[],
        expected_out=block_header("unicode.txt") + unicode_body,
        expected_err=b"",
        expected_exit=0,
    )

    # 8: binary content with NUL byte
    write_case(
        "binary-nul",
        args=["nul.bin"],
        inputs={"nul.bin": b"a\x00b\n"},
        subdirs=[],
        expected_out=block_header("nul.bin") + b"a\x00b\n",
        expected_err=b"",
        expected_exit=0,
    )

    # 9: missing file
    write_case(
        "missing",
        args=["missing.txt"],
        inputs={},
        subdirs=[],
        expected_out=b"",
        expected_err=b"missing.txt? never heard of her\n",
        expected_exit=1,
    )

    # 10: directory as arg
    write_case(
        "directory",
        args=["subdir"],
        inputs={},
        subdirs=["subdir"],
        expected_out=b"",
        expected_err=b"subdir is a directory fam\n",
        expected_exit=1,
    )

    # 11: no args
    write_case(
        "no-args",
        args=[],
        inputs={},
        subdirs=[],
        expected_out=b"",
        expected_err=b"bestie you have to give me a file\n",
        expected_exit=1,
    )

    # 12: good, missing, good
    write_case(
        "good-missing-good",
        args=["hi.txt", "missing.txt", "bye.txt"],
        inputs={"hi.txt": b"hi\n", "bye.txt": b"bye\n"},
        subdirs=[],
        expected_out=(
            block_header("hi.txt") + b"hi\n"
            + block_header("bye.txt") + b"bye\n"
        ),
        expected_err=b"missing.txt? never heard of her\n",
        expected_exit=1,
    )


if __name__ == "__main__":
    main()
