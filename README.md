# brat

`brat` is a small `cat`-style file printer intended to be written in
[CURSED](https://github.com/ghuntley/cursed), Geoffrey Huntley's
Gen-Z-slang programming language.

The program is deliberately tiny: `brat file1 file2 ...` should print
each file with a lime block header, continue after per-file read errors,
write bratism error messages to stderr, and exit non-zero if anything
failed. That small surface is enough to exercise real native-compiled
CURSED behavior: argv, file I/O, stderr, exit codes, raw stdout,
conditionals, loops, arrays, and user-defined functions.

## For CURSED Maintainers

If you are reviewing a CURSED compiler/runtime PR, brat is the downstream
program motivating several of the small missing primitives.

The shortest path through the evidence is:

- [`docs/cursed-subset.md`](docs/cursed-subset.md) — what clean upstream
  `cursed-compiler --compile` actually does today for the brat-relevant
  subset.
- [`docs/cursed-gaps.md`](docs/cursed-gaps.md) — per-primitive gap map:
  what brat needs, current failure mode, blocked test cases, and an
  upstream framing line.
- [`experiments/verify_cursed_gaps.sh`](experiments/verify_cursed_gaps.sh)
  — runnable probes for the current compiler behavior.
- [`UPSTREAM.md`](UPSTREAM.md) — reviewer-oriented tracker for issues and
  PRs against CURSED.

This repo is not trying to prove that all of CURSED works. It is a small
downstream test case for the native compiler path, with byte-exact tests
for Unix-tool behavior.

## Current State

brat currently has a pytest golden test suite and CURSED gap audit. The
real `brat.💀` implementation is blocked on missing or broken CURSED
compiler/runtime primitives. See [`UPSTREAM.md`](UPSTREAM.md) for the
current unblock list.

## Test Suite

The tests live under [`tests/cases/`](tests/cases/). Each case has:

- `args` — one argv item per line, relative to the case's `inputs/`
  directory;
- `inputs/` — files and directories passed to brat;
- `expected.out`, `expected.err`, `expected.exit` — byte-exact goldens;
- optional `modes` — chmod setup for permission-denied cases.

Run the suite with:

```bash
python3 -m pytest
```

Point it at a non-default binary with:

```bash
BRAT_BIN=/path/to/brat python3 -m pytest
```

Regenerate goldens only after an intentional output contract change:

```bash
BRAT_UPDATE_GOLDENS=1 python3 -m pytest
```

## Design Shape

The intended command is:

```bash
brat file1 file2 ...
```

For each readable file, brat emits:

1. a three-line lime block header containing the filename;
2. the file bytes, verbatim;
3. one extra newline only if the file does not already end with `\n`.

For unreadable files, brat emits a lowercase bratism to stderr, skips the
header for that file, keeps processing later files, and exits with status
1 at the end.

No flags, stdin mode, paging, TTY detection, or `NO_COLOR` behavior are
in scope.

## Repository Map

- [`tests/`](tests/) — pytest golden harness and byte-exact cases.
- [`docs/cursed-subset.md`](docs/cursed-subset.md) — verified CURSED
  compile subset as of the current audit snapshot.
- [`docs/cursed-gaps.md`](docs/cursed-gaps.md) — detailed gap audit.
- [`docs/learnings.md`](docs/learnings.md) — append-only notes from
  working on brat and CURSED.
- [`experiments/verify_cursed_gaps.sh`](experiments/verify_cursed_gaps.sh)
  — reproducible CURSED probe runner.
