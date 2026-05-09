# brat — TDD addendum

**Status:** approved (brainstorming, 2026-05-09)
**Parent spec:** [2026-05-09-brat-design.md](./2026-05-09-brat-design.md)
**Next step:** implementation plan for the test suite via writing-plans skill.

## Purpose

The parent spec is sufficient for a red→green TDD workflow *except* in three areas that this addendum rewrites:

1. **Six small ambiguities** that would make byte-exact goldens non-deterministic (Sections 1–6 below).
2. **Test harness:** the parent spec proposes pure shell (`tests/run.sh`); we are switching to pytest (Section 7 below).
3. **Upstream CURSED workflow:** the parent spec front-loads PR-1 through PR-5 against the local CURSED fork; we are flipping to discovery-driven (Section 8 below).

When this addendum and the parent spec disagree, this addendum wins.

## 1. Block-header geometry (extends parent §4)

The filename row is constructed as:

```
bg + black + "  " + filename + "  " + (width - len(filename) - 4) spaces + reset + "\n"
```

where `width = max(50, len(filename) + 4)`. The `bg` and `black` codes are the lime-bg and black-fg ANSI escapes from parent §4. The fill character is the ASCII space (`0x20`).

For filenames where `len + 4 > 50`, the trailing pad becomes zero and the block grows to fit. The 2-space left and right gutters are always present.

Worked examples (with `name` lowercased per PR-5):

| Filename       | len | width | Filename row visible bytes                       |
|----------------|-----|-------|--------------------------------------------------|
| `readme.md`    |  9  |  50   | `"  readme.md  "` + 37 spaces                    |
| `unicode.txt`  | 11  |  50   | `"  unicode.txt  "` + 35 spaces                  |
| 47 `x`s        | 47  |  51   | `"  "` + 47 `x`s + `"  "` (no trailing pad)      |

Top and bottom rows are `bg + width spaces + reset + "\n"`. Each of the three rows ends with exactly one `\n`.

## 2. Empty file body (extends parent §§3, 4)

When `fs.read_file` returns zero bytes and `errno == 0`, brat emits the three-line header and *nothing else* for that file. The "append `\n` if last byte isn't `\n`" rule does not fire when there is no last byte.

This matches `cat empty.txt` (zero bytes for the body) and matches the parent §7 table row "Single empty file: block header, no body."

## 3. Mixed success/failure test case (extends parent §7)

Add one test case to the table (full table reproduced at the end of this addendum):

| Case | stdout | stderr | exit |
|---|---|---|---|
| `good, missing, good` (3 args) | two header+body sections, in argv order, for the two existing files | one bratism for the missing file | 1 |

Pins three properties at once: the header is *not* emitted for the failing file, the exit code persists past a later success, and stdout flow continues after a per-file error.

## 4. Stream semantics in tests

Each test case has up to three goldens — `expected.out`, `expected.err`, `expected.exit`. **No merged-stream golden is captured for any case.** Cross-stream byte interleave order is libc-buffering-dependent (line-buffered stdout vs unbuffered stderr) and is not part of brat's contract.

`subprocess.run([...], capture_output=True)` returns `stdout` and `stderr` as `bytes` objects with no decoding and no trailing-newline stripping. Goldens are read with `Path.read_bytes()` and compared with `==`. The shell-pipeline footgun the parent §7 warned about (`$(...)` stripping trailing newlines) does not apply.

## 5. Binary input (extends parent §§4, 7)

File contents are emitted verbatim. NUL bytes (`0x00`), high-bit bytes, and any other non-text bytes pass through unchanged. Add one test case:

| Case | Input | stdout | stderr | exit |
|---|---|---|---|---|
| `binary-nul` | 4-byte file `a\x00b\n` | header + `a\x00b\n` | empty | 0 |

This case is the cheapest test that distinguishes a real byte-oriented `io.write` from a string primitive that NUL-terminates. The unicode-passthrough case in the parent spec does not catch a NUL-truncating implementation because UTF-8 produces no mid-stream NUL.

## 6. Bratism line-termination contract (extends parent §§3, 5, 6)

Bratism strings in the parent §5 catalog are line *content* only. They do not include a trailing `\n`. The `io.eprintln` primitive is solely responsible for appending exactly one `\n` per call.

Consequences:

- Every `expected.err` golden ends in exactly one `\n` byte.
- Adding a new bratism to the catalog requires no per-string newline discipline; the print primitive enforces termination.
- The `io.ewrite` primitive (no termination) is reserved for the block-header rows, where each `\n` is written explicitly.

## 7. Test harness: pytest, not shell (supersedes parent §7)

The parent spec proposes a pure-shell harness (`tests/run.sh`). This addendum supersedes that with **pytest**.

### Tooling

- `pytest` is the only required test dependency. Declare it in `pyproject.toml` under `[project.optional-dependencies] test = ["pytest"]`.
- No `syrupy` / `pytest-snapshot`. Their snapshot storage formats fight binary goldens with NUL bytes and ANSI escapes; plain files on disk plus `Path.read_bytes()` is cleaner.
- No `pytest-xdist`. Twelve cases, no parallelization benefit.

### Layout

```
tests/
├── conftest.py        ← session-scoped fixture: locates ./brat or fails loudly
├── test_brat.py       ← single parametrized test, walks tests/cases/
└── cases/
    ├── empty/
    │   ├── args            (one arg per line, paths relative to inputs/)
    │   ├── inputs/
    │   │   └── empty.txt   (the 0-byte file)
    │   ├── expected.out    (binary-clean, exact bytes)
    │   ├── expected.err
    │   └── expected.exit   (one-line integer)
    ├── one-line-no-eol/
    │   └── ...
    └── ...
```

One sub-folder per case. The test function is parametrized over `Path("tests/cases").iterdir()` and runs `subprocess.run([brat_bin, *args], cwd=case_dir / "inputs", capture_output=True)`, where `brat_bin` is the absolute path returned by the session fixture. It then asserts `result.stdout == expected_out.read_bytes()`, same for stderr, and `result.returncode == int(expected_exit.read_text().strip())`. The "no args" case (#11) has an empty `args` file, which the test loads as an empty list.

### Regenerating goldens

`BRAT_UPDATE_GOLDENS=1 pytest tests/` overwrites `expected.*` instead of asserting. Replaces the parent spec's `make regenerate-golden` target. The `make test` target (parent §7) becomes `python -m pytest tests/`.

### Why pytest over shell

- `bytes` round-trip is byte-exact at the language level — no shell-quoting and no command-substitution stripping.
- Parametrization gives one diff-per-case in failure output instead of a single shell `diff` dump.
- Setting up per-case fixture directories (input files with NUL bytes, files with no trailing newline) is straightforward in Python and awkward in shell.
- The cost is one Python dependency in a project that previously had zero. Acceptable in exchange.

## 8. Upstream CURSED workflow: discovery-driven (supersedes parent §6 workflow)

The parent §6 lists PR-1 through PR-5 against the local CURSED fork with effort estimates and a sequenced workflow ("implement PR-1, submit upstream, then PR-2, then write `brat.💀`"). This addendum supersedes that.

### New rule

Write `brat.💀` against current CURSED. Run the test suite. When — and only when — a test goes red because something in CURSED is missing, broken, or hardcoded:

1. **File an issue** against upstream CURSED with the failing test as a reproducer. The reproducer is a small CURSED snippet, not a brat-shaped repro.
2. **Implement the fix locally** in the CURSED fork (`~/cursed`) until the brat test goes green.
3. **Continue** with the next failing test.
4. **Track** the open issue and the local patch in `brat/UPSTREAM.md`. When upstream merges (or rejects), update the row.

### Why this over pre-planned PRs

- We only fix what brat actually needs. The parent spec's PR-3 (`os.exit`) and PR-5 (`string.to_lowercase`) might never be required if the fallback paths work; the discovery-driven approach skips speculative work.
- Each upstream issue is grounded in a concrete failing test, which makes the bug report unambiguous and the upstream review trivial.
- It avoids investing days in PR-1 only to discover during PR-2 that the read-file errno shape needs to change.
- It keeps brat itself moving forward at all times — the moment a CURSED gap is closed locally, the next red test is already waiting.

### What the parent §6 PR catalog becomes

The PR-1 through PR-5 catalog in parent §6 is now **informational, not prescriptive**: a likely-missing-pieces list to set expectations. Reality may produce a different set, in a different order, with different shapes. The fallback strategies described per-PR in parent §6 still apply if a particular fix proves too hard to land in the local fork.

### Bail-out criteria (unchanged from parent §6)

The bail-out criteria from parent §6 still hold: if local fork work on a single capability exceeds two weeks of evenings, pause and reconsider. If LLVM IR codegen proves too brittle, consider a CURSED runtime library in C/Zig.

## Test-case roster (final)

The full parent §7 table after this addendum:

| # | Case | stdout | stderr | exit |
|---|---|---|---|---|
| 1 | Single empty file | header, no body, no `\n` after | empty | 0 |
| 2 | Single one-line file (no trailing `\n`) | header + line + appended `\n` | empty | 0 |
| 3 | Single multi-line file (with trailing `\n`) | header + content verbatim | empty | 0 |
| 4 | Multi-file invocation | concatenated headers + bodies | empty | 0 |
| 5 | Filename with uppercase letters | header lowercased (or as-given in PR-5 fallback) | empty | 0 |
| 6 | Long filename (>46 chars) | block grows to fit; no trailing pad | empty | 0 |
| 7 | Unicode content | passthrough | empty | 0 |
| 8 | Binary content with NUL byte | passthrough including `\x00` | empty | 0 |
| 9 | Missing file | empty | `<filename>? never heard of her\n` | 1 |
| 10 | Directory as arg | empty | `<filename> is a directory fam\n` | 1 |
| 11 | No args | empty | `bestie you have to give me a file\n` | 1 |
| 12 | `good, missing, good` (3 args) | two header+body sections in argv order | one bratism `\n`-terminated | 1 |

Each case gets `expected.out`, `expected.err`, `expected.exit` goldens under `tests/cases/<case>/`. The `.exit` file is a one-line integer.
