# brat — design

**Status:** approved (brainstorming, 2026-05-09)
**Next step:** implementation plan via writing-plans skill.

## 1. Overview

`brat` is a `cat`-style file printer, written in pure CURSED, with a brat-album-coded aesthetic. It reads files by name, prints each one with a lime-green block header, and emits lowercase bratism error messages on failure.

The pitch is the combination, not any single layer:

- A real, runnable Unix utility shipped as `brat`
- Implemented in CURSED (the gen-z-slang esoteric language by Geoffrey Huntley)
- The first non-trivial CURSED program that requires real file I/O, motivating the addition of real file I/O to CURSED itself
- Album-cover-coded UI: lime `#8ACE00`, lowercase, austere

## 2. Scope

### In scope (v1.0)

- `brat file1 file2 ...` reads each file and prints its contents to stdout, preceded by a lime-green block header showing the (lowercased) filename
- Lowercase bratism error messages to stderr
- Continue-don't-abort error semantics: a missing file logs an error; the next file still gets printed
- Native binary built from a single `.💀` source via `cursed-compiler`
- Source distribution + pre-built binaries for Linux x64 and macOS arm64

### Out of scope

- No flags. No `-n`, no `--help`, no `--version`. brat doesn't speak.
- No syntax highlighting (wrong feature, wrong aesthetic, scope risk in a half-baked language)
- No stdin support; no `-` filename
- No paging, no TTY detection, no `NO_COLOR` support
- No multi-file separator beyond the block header
- No internationalization. Lowercase English forever.
- No package manager integration in v1.0 (no Homebrew tap, no nix derivation)

## 3. Architecture

Single source file (`brat.💀`), ~150 lines of CURSED. Three internal `slay` functions:

```
main():
    args = os.argv()[1:]                  # PR-2
    if args is empty:
        io.eprintln("bestie you have to give me a file")  # PR-4
        os.exit(1)                         # PR-3
    exit_code = 0
    for filename in args:
        (contents, errno) = fs.read_file(filename)  # PR-1
        if errno != 0:
            io.eprintln(brat_message_for(errno, filename))
            exit_code = 1
            continue
        print_block_header(filename)
        io.write(contents)                 # PR-4: raw, no implicit newline
        if last byte of contents is not '\n':
            io.write("\n")                 # ensures next header starts cleanly
    os.exit(exit_code)
```

Helpers:

- `print_block_header(name tea)` — assembles the three-line lime block header and writes via `io.write` (raw bytes, with explicit `\n` after each header line). Lowercases the name before printing.
- `brat_message_for(errno normie, filename tea) tea` — maps a `read_file` errno to one of the canonical bratisms. Used by the error path.

There is no flag-parsing function; argv minus arg 0 is the filename list.

### Why `io.write` and not `vibez.spill`

`vibez.spill` is line-oriented and always appends `\n`. Using it for file contents would (a) add a trailing newline to files that don't end in one, breaking `cat`-style verbatim semantics, and (b) double the trailing newline on files that do. brat needs a byte-oriented stdout primitive (`io.write`) that emits exactly the bytes given, no more. This is part of PR-4's scope (see Section 6).

`vibez.spill` is still fine for places where we *do* want an implicit newline — e.g., terminating block-header lines — but the spec uses `io.write` for both header and body to keep newline behavior explicit and predictable.

### Graceful degradation

Three behaviors degrade if the corresponding upstream PR doesn't land:

- **Non-zero exit code (PR-3):** falls back to always-exit-0.
- **Stderr writing (part of PR-4):** falls back to stdout for errors via `io.write`. Raw stdout writing itself is non-negotiable.
- **Lowercased filename in header (PR-5):** falls back to filename as-given.

The architecture is unchanged in any of these fallback modes.

## 4. Output specification

### ANSI color codes (24-bit truecolor)

- Lime fg: `\x1b[38;2;138;206;0m`
- Lime bg: `\x1b[48;2;138;206;0m`
- Black fg: `\x1b[30m`
- Reset: `\x1b[0m`

Truecolor is universal in modern terminals. Older terminals get default colors — acceptable degradation.

### Block header

Three lines per file, width = `max(50, len(filename) + 4)`:

```
ESC[48;2;138;206;0m<W spaces>ESC[0m
ESC[48;2;138;206;0mESC[30m  <filename>  <padding>ESC[0m
ESC[48;2;138;206;0m<W spaces>ESC[0m
```

Filename is lowercased (PR-5; falls back to as-given). No truncation logic — block grows to fit.

Visual:

```
██████████████████████████████████████████████████
█  readme.md                                     █
██████████████████████████████████████████████████
```

### File contents

Printed verbatim, default terminal color, no transformation. If the final byte isn't `\n`, brat emits one extra newline so the next file's block header starts cleanly.

### Multi-file behavior

Files are emitted back-to-back with no blank-line separator — the block header itself provides the visual break.

### Failure cases

When `fs.read_file` returns a non-empty error string:

1. Write the bratism to stderr (or stdout in fallback).
2. Set `exit_code = 1`.
3. **Do not** emit a partial block header for the failed file.
4. Continue to the next file.

### TTY/piping

brat does not detect TTY. ANSI escapes are emitted unconditionally. Users who pipe brat are doing it deliberately (e.g., to `less -R`) or accept that downstream tools will see escape sequences.

## 5. Error handling

### Bratism catalog

A *bratism* is brat's signature error voice: lowercase, terse, vocative, gen-z internet vernacular. The catalog below enumerates the canonical strings.


| Trigger | Message |
|---|---|
| No filenames passed | `bestie you have to give me a file` |
| File doesn't exist | `<filename>? never heard of her` |
| File exists but not readable | `<filename> said no` |
| File is a directory | `<filename> is a directory fam` |
| Generic read failure | `<filename> is not giving` |

`fam` is CURSED's `try`-block keyword (paired with `shook`/`yikes` for error handling); using it as a vocative winks at the language. `bestie` is CURSED's `for` keyword. The catalog uses two CURSED keywords as easter eggs.

### Mapping rules

`fs.read_file` returns an integer `errno` on failure (see PR-1 in Section 6). `brat_message_for(errno, filename)` matches on the errno value, using POSIX-standard codes:

- `errno == 2` (ENOENT) → `<filename>? never heard of her`
- `errno == 13` (EACCES) → `<filename> said no`
- `errno == 21` (EISDIR) → `<filename> is a directory fam`
- otherwise → `<filename> is not giving`

ENOENT/EACCES/EISDIR values are stable across Linux and macOS (the only platforms we ship for in v1.0). Returning structured errno avoids the platform-specific text matching that `strerror` would force (e.g., `"No such file or directory"` would otherwise misroute through the directory branch).

If at any point PR-1 cannot return errno cleanly, fallback: collapse to two cases — `<filename> is not giving` for any read failure, and `bestie you have to give me a file` for empty argv.

### Style rules

- All-lowercase always
- No trailing punctuation
- Filename is included verbatim (not lowercased) in error messages — preserves the diagnostic signal

### Errors are always default-color

No lime, no escapes. Errors should be readable when redirected to logs.

## 6. Required CURSED contributions

brat develops against a **local fork of CURSED**. As capabilities turn out to be missing or mocked, we patch them locally and submit upstream PRs in parallel. brat's `cursed/` submodule pins to a known-good local commit until upstream merges.

**"Pure CURSED" boundary.** brat itself (`brat.💀`) is pure CURSED user code. The contributions below add new compiler builtins to `cursed-compiler` (Zig source) — those are language/runtime work, not user code. The pitch "brat is written in pure CURSED" refers to brat the program, and is not invalidated by the fact that we extended CURSED's compiler/runtime to support real I/O.

### Critical-path PRs

**PR-1: `fs.read_file(path tea) (tea, normie)` — real file reading**
Today: returns the literal string `"Hello World"`. Implementation: compiler builtin in `cursed-compiler` (Zig) emitting LLVM IR that calls libc `open`/`read`/`close` (or `fopen`/`fread`/`fclose`). Returns `(content, errno)`: integer errno is 0 on success, otherwise the standard POSIX errno (e.g., 2 = ENOENT, 13 = EACCES, 21 = EISDIR). Multi-return is already supported in CURSED. Returning a numeric errno (not `strerror` text) is what lets brat's error mapping be platform-stable.
Estimated effort: 3–5 evenings.

**PR-2: `os.argv() [tea]` — real command-line arguments**
Today: not a usable primitive; `command_line` stdlib parses against hardcoded internal state. Implementation: compiler builtin + a runtime hook capturing `argc`/`argv` at program entry into a global; expose `os.argv()` returning a `[tea]` slice.
Estimated effort: 2–3 evenings.

**PR-4 (now critical-path): `io.write` / `io.eprintln` — raw byte I/O**
brat needs three I/O primitives beyond the line-oriented `vibez.spill`:

- `io.write(s tea)` — write raw bytes to stdout, no implicit newline. **Critical.** Required to print file contents byte-perfectly (`vibez.spill` always appends `\n` and so cannot match `cat`-style verbatim semantics).
- `io.ewrite(s tea)` — same but to stderr.
- `io.eprintln(s tea)` — convenience wrapper around `io.ewrite` that adds `\n`. Used for error messages.

Implementation: compiler builtins emitting `write(1, ...)` and `write(2, ...)` syscalls, or `fwrite(stdout, ...)` and `fwrite(stderr, ...)`.
Estimated effort: 2 evenings.
Fallback: if stderr writing can't be made to work, errors go to stdout via `io.write`. If `io.write` itself can't be made to work, brat cannot ship — raw byte writing is non-negotiable for `cat` semantics.

### Soft PRs (graceful degradation if absent)

**PR-3: `os.exit(code normie)` — non-zero exit codes**
Builtin emitting `call void @exit(i32 %code)`. 1 evening.
Fallback: always exit 0.

**PR-5: `string.to_lowercase(s tea) tea` — lowercase the filename**
Probe first; may already exist in some `stringz` variant. If absent, implement in pure CURSED (ASCII byte-iteration) or as a builtin. 1–2 evenings.
Fallback: filename printed as-given.

### Workflow

1. Build `cursed-compiler` from source via `zig build`. Confirm a hello-world `.💀` compiles and runs end-to-end before changing anything.
2. Implement PR-1 on a feature branch in the local fork. Submit upstream. Continue on the local fork for brat development.
3. Implement PR-2. Submit upstream.
4. With PR-1 and PR-2 working in the local fork, write `brat.💀`. Submit soft PRs in parallel as needed.
5. Track all open PRs in `brat/UPSTREAM.md`. Pin `brat/cursed/` to the local fork commit including all required patches.
6. As upstream merges, rebase the local fork onto upstream main and drop the corresponding patches.

### Bail-out criteria

- If PR-1 (read_file) requires understanding CURSED's codegen at a depth that takes >2 weeks of evenings just to orient: pause; reconsider whether to fall back to a "brat as art piece" pivot (a hardcoded printer, no real file I/O).
- If upstream is unresponsive to PRs for >3 weeks: ship brat against the pinned local fork; document the situation in UPSTREAM.md.
- If LLVM IR generation in `cursed-compiler` proves too brittle for builtins: consider landing I/O via a minimal CURSED runtime library in C/Zig that the compiler links against. Increases effort; preserves the "pure CURSED on the user-facing side" pitch.

## 7. Project layout, build, testing

### Repo layout

```
brat/
├── README.md          ← launch artifact: GIF, install, the joke, links to upstream PRs
├── UPSTREAM.md        ← list of CURSED PRs brat depends on, with status
├── brat.💀            ← the entire program, ~150 lines
├── cursed/            ← git submodule pinned to the local fork commit
├── Makefile           ← `make`, `make install`, `make test`, `make clean`
└── tests/
    ├── inputs/        ← sample files
    ├── expected/      ← golden ANSI-byte outputs
    └── run.sh         ← runs brat on each input, diffs against expected
```

### Build

`Makefile` targets:

- `make` — runs `zig build` in the `cursed/` submodule, then invokes the resulting `cursed-compiler` to compile `brat.💀` to a native binary at `./brat`.
- `make install` — copies `./brat` to `$PREFIX/bin/brat` (default `/usr/local/bin`).
- `make test` — runs `tests/run.sh`.
- `make clean` — removes build artifacts.

Pre-built binaries on GitHub Releases for Linux x64 and macOS arm64. Two artifacts max in v1.0. CI optional; manual release acceptable.

### Testing

Pure shell, no CURSED-side test framework (CURSED's tests largely test mocks; not modelable).

Each test case has up to three goldens — `<case>.out` for stdout, `<case>.err` for stderr, `<case>.exit` for the exit code (an integer in a one-line file). All three are checked.

`tests/run.sh` per case:

1. Run `./brat <args>`, redirecting each stream to its own temp file (never use `$(...)` capture — it strips trailing newlines, which would defeat the byte-level checks we need):
   ```
   ./brat <args> >"$tmp/out" 2>"$tmp/err"
   actual_exit=$?
   ```
2. Diff `$tmp/out` against `tests/expected/<case>.out` byte-for-byte (`diff -u` or `cmp`).
3. Diff `$tmp/err` against `tests/expected/<case>.err` byte-for-byte (empty file = expected empty stderr).
4. Compare `actual_exit` against the integer in `tests/expected/<case>.exit`.
5. Print pass/fail per case. Exit non-zero on any failure.

Why files, not shell variables: bash command substitution (`$(...)` and backticks) strips *all* trailing newlines from captured output. That would silently mask the exact behavior these tests are meant to verify — that brat appends a `\n` to file contents that don't end in one, and that error messages on stderr terminate cleanly. File-based capture preserves bytes exactly.

Test cases (each gets `.out`, `.err`, `.exit` goldens):

| Case | stdout | stderr | exit |
|---|---|---|---|
| Single empty file | block header, no body | empty | 0 |
| Single one-line file (no trailing `\n`) | block header + line + appended `\n` | empty | 0 |
| Single multi-line file (with trailing `\n`) | block header + content verbatim | empty | 0 |
| Multi-file invocation | concatenated headers + bodies | empty | 0 |
| Filename with uppercase letters | header lowercased (or as-given in PR-5 fallback mode) | empty | 0 |
| Long filename | block grows to fit | empty | 0 |
| Unicode content | passthrough | empty | 0 |
| Missing file | empty | `<filename>? never heard of her` | 1 |
| Directory as arg | empty | `<filename> is a directory fam` | 1 |
| No args | empty | `bestie you have to give me a file` | 1 |

This catches all the failure-path requirements directly: stderr-channel correctness (PR-4), exit-code correctness (PR-3), and bratism mapping (Section 5). In fallback modes (PRs not landed), the corresponding tests will fail intentionally — that's how we know which fallbacks are active.

Golden outputs are committed as binary-clean files containing exact ANSI escape bytes. Regenerate intentionally via `make regenerate-golden`.

### Out of scope for v1.0

- CI matrix
- Cross-platform binaries beyond Linux x64 / macOS arm64
- Homebrew tap, cargo install, nix derivation
- Man page, tab completion
- `--version` or `--help` flags
- Localization

## 8. Local environment

The user has a clone of `ghuntley/cursed` at `~/cursed` (working directory). brat lives at `~/brat`. The brat repo's `cursed/` submodule will be configured to point at the local fork (created from `~/cursed`); during initial development, this submodule URL is the local path, swapped to a public fork URL once one is created.
