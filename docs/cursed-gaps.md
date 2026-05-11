# CURSED Gaps for brat

A per-primitive roadmap of what CURSED is missing for brat to be
implementable. Updated as of 2026-05-11 against local `~/cursed`
`main`: clean upstream `ghuntley/cursed` (`zig` branch, HEAD =
`ecda33d49`) plus runtime-path portability commits `2fa866746` and
`7dafe251c`. Diagnostics and IR shapes will drift; this doc is a
snapshot, not a live contract.

## Companion docs

- `docs/cursed-subset.md` — what `cursed-compiler --compile`
  *actually does* in clean upstream today, organised by failure-mode
  bucket. Anchor for every Status line below.
- `experiments/verify_cursed_gaps.sh` — runnable probe set; output
  reproduces every Evidence line involving compile/run behavior.

## Gap entry conventions

Each gap has:

- **Need:** what brat needs this for, in one sentence.
- **Status:** one of:
  - `no-surface` — runtime/stdlib doesn't expose what brat needs
  - `silent-no-op` — call compiles but does nothing at runtime
  - `silent-miscompile` — compiles + runs but produces wrong output
  - `broken-IR` — cursed-compiler reaches clang, but generated IR
    fails to link
  - `partial` — some shapes work, others fail in one of the modes above
- **Evidence:** runtime-C / spec citation, fenced probe output, or
  reference to a `verify_cursed_gaps.sh` probe — at least one.
- **Brat cases blocked:** list of `tests/cases/<name>` dirs.
- **Upstream framing:** one-line issue title + the minimal surface
  that would unblock brat.

## Gaps

### stderr-write

**Need:** brat writes its bratism error messages to stderr.
**Status:** no-surface.
**Evidence:** `~/cursed/src-zig/cursed_runtime.c:1-42` — only
`cursed_runtime_spill_string/_int/_float/_bool` exist, all writing
via `printf`/`fflush(stdout)`. No `fprintf`, no `stderr`, no fd-2
write path. `~/cursed/specs/stdlib/main_character.md:125`
documents an `ErrorVibe = NewVibeFile(uintptr(syscall.Stderr),
"/dev/stderr")` handle and `~/cursed/specs/stdlib/dropz.md:172`
mentions a `stderr Writer` — neither is reachable. Probed with
`vibez.spill_err("error")`: compiles cleanly, runs cleanly, zero
bytes on stderr (silent no-op for any unknown function call).
**Brat cases blocked:** dash-filename, directory, good-missing-good, missing, multi-missing, no-args, permission-denied.
**Upstream framing:** "runtime: add stderr write surface" — minimum: a `vibez.spill_err(s)` (or equivalent) that maps to `fprintf(stderr, ...)`.

### exit-code-control

**Need:** brat must exit non-zero when any file fails to read, so `cat`-style pipelines can detect failure.
**Status:** no-surface.
**Evidence:** `~/cursed/src-zig/cursed_runtime.c:1-42` — no `exit(`, `_exit`, or `abort` symbol referenced; the runtime exposes only the four `spill_*` print helpers. `~/cursed/specs/stdlib/main_character.md:89` documents `slay VibeOut(code normie)` ("Exits with status code (like os.Exit)") but it isn't wired. Probed with `os.exit(1)` and `vibez.exit(1)`: both compile clean, run clean, `$? = 0`. Silent no-op for any unknown call.
**Brat cases blocked:** dash-filename, directory, good-missing-good, missing, multi-missing, no-args, permission-denied.
**Upstream framing:** "runtime: expose process exit primitive" — minimum: a `vibe_life.exit(code normie)` (or `os.exit`) that maps to libc `exit(int)`.

### file-read

**Need:** brat must read the bytes of each file named on the command line.
**Status:** no-surface.
**Evidence:** `~/cursed/src-zig/cursed_runtime.c:1-42` — no `fopen`, `fread`, `read`, or `open`. `~/cursed/specs/stdlib/dropz.md:59-99` documents `slay read_file(filename tea) ([]byte, tea)`, `read_text_file`, `open`, `open_file`, and `(f *File) read` — none implemented. Probed: `dropz.read_file("foo")` and other module-prefixed calls compile clean and silently no-op (calls into an unloaded module are dropped). Bare `read_file("foo")` reaches LLVM code generation, then `cursed-compiler` exits 1 with `error.FunctionNotFound`.
**Brat cases blocked:** all 18 cases except no-args (no-args never opens a file).
**Upstream framing:** "runtime+stdlib: implement `dropz.read_file`" — minimum: a `dropz.read_file(path tea) ([]byte, tea)` that maps to libc `fopen`/`fread`/`fclose` and surfaces errno-shaped errors.

### errno-surfacing

**Need:** brat distinguishes ENOENT, EACCES, EISDIR, and "other" so it can pick the right bratism for each failure.
**Status:** no-surface (depends on file-read).
**Evidence:** `~/cursed/specs/stdlib/dropz.md:59-99` documents the multi-return `(content, errno)` shape but no implementation exists. Without `file-read` reachable, errno can't be surfaced regardless. Once file-read lands, errno-as-int needs to come back through whatever return-value mechanism CURSED exposes — currently UDF return values silently disappear (see `user-defined-functions`), so the multi-return mechanism is its own gap.
**Brat cases blocked:** dash-filename, directory, good-missing-good, missing, multi-missing, permission-denied.
**Upstream framing:** "runtime+stdlib: surface POSIX errno from `dropz.read_file`" — minimum: integer errno as second return value, stable across Linux and macOS.

### non-stdlib-imports

**Need:** brat needs whichever stdlib module owns file I/O, stderr, and exit (e.g. `dropz`, `main_character`). Today only `vibez` and `stringz` imports load.
**Status:** silent-no-op.
**Evidence:** Probed with `yeet "dropz"` followed by `dropz.read_file("x")`: compiles clean, exits 0, no output. The compile log reports `Unknown stdlib module: dropz`, then `Method dropz.read_file not found - skipping for core language testing`; compilation continues and produces a binary that runs as a no-op. Any call against an unloaded module is silently dropped at IR generation. (An earlier audit recorded these as compile-time *rejections*; that was an artifact of a local-only validator since reset away — see `docs/cursed-subset.md`.)
**Brat cases blocked:** all 18 cases (every brat program needs at least one non-`vibez`/`stringz` import — `dropz` for file I/O, plus whichever module owns stderr/exit).
**Upstream framing:** "compiler: load and expose `dropz` module against the runtime" — coupled to whichever runtime/stdlib gap (file-read, stderr-write, exit-code-control) is being unblocked.

### user-defined-functions

**Need:** brat needs helpers (e.g. `print_block_header`, `brat_message_for`) factored out of `main_character`. The design spec assumes ordinary user-defined functions with arguments and return values.
**Status:** partial — argless void UDFs work; arguments silently lower to integer 0; return values are silently lost.
**Evidence:** Probe `slay helper() { vibez.spill("helper") }` then `helper()` from main: works correctly, prints `helper\n`. Probe `slay greet(name tea) { vibez.spill(name) }` then `greet("hello")`: prints `0`, not `hello` (argument silently substituted with int 0 — same failure mode as `argv`). Probe `slay double(x normie) normie { yeet x + x }` then `vibez.spill(double(21))`: prints nothing. Reproduces in `verify_cursed_gaps.sh` (the `user_defined_function` probe is the argless case and works).
**Brat cases blocked:** all 18 cases (the design factors `print_block_header(name)` and `brat_message_for(errno, filename)` out of `main_character`; both take arguments and `brat_message_for` returns a string).
**Upstream framing:** "compiler: lower UDF parameters and return values to LLVM IR" — minimum: scalar and string parameters, scalar and string returns, multi-return for the `(content, errno)` shape `dropz.read_file` exposes.

### member-access

**Need:** brat's design spec uses method-call / selector syntax extensively (`io.write`, `os.argv`, `state.ExitCode()`); even simple field reads like `result.err` are out of reach.
**Status:** broken-IR.
**Evidence:** Probe `sus s tea = "hello"; vibez.spill(s.length)`: cursed-compiler emits IR with an undefined string reference, clang fails with `error: use of undefined value '@.str.0'`, and the compiler exits 1 with `error.ClangFailed`. No binary is produced. Stdlib calls like `vibez.spill` are recognised as a special-cased form (parsed as a call to the runtime helper directly), not as general member access.
**Brat cases blocked:** all 18 cases (the design uses `os.argv`, `state.ExitCode()`, and `result.err`-shaped reads throughout; even the no-args branch needs `os.argv` length).
**Upstream framing:** "compiler: implement general selector / member-access lowering" — minimum: `expr.field` and `expr.method(args)` for user types and stdlib values, not just hard-coded `module.fn` patterns.

### array-literals-and-indexing

**Need:** brat reads `argv[i]` to walk filenames, and the design's pseudocode uses `args = os.argv()[1:]` to slice off arg 0.
**Status:** silent-miscompile.
**Evidence:** Probe `sus xs [3]normie = [10, 20, 30]; vibez.spill(xs[2])`: compiles clean, runs clean, prints `1\n` regardless of array contents or index. The IR is `call void @cursed_runtime_spill_int(i64 1)` — both the array literal and the index are ignored; the compiler emits a hardcoded `1`. (A previous audit recorded these as compile-time rejections — see `non-stdlib-imports` evidence note for the gating-layer history.)
**Brat cases blocked:** all 18 cases (every brat program reads `argv[i]` at least once — even no-args needs to test `len(argv) < 2`, which requires argv to be a sequence).
**Upstream framing:** "compiler: lower array literals and `[]` indexing to LLVM IR" — minimum: stack-allocated arrays of strings/ints with constant-index reads. Slice syntax (`[1:]`) can come later.

### conditionals

**Need:** brat branches on argv length (zero args → error; otherwise iterate files) and on per-file open errors.
**Status:** silent-miscompile (whole-function-dropping).
**Evidence:** Probe `vibez.spill("BEFORE"); ready 1 { vibez.spill("INSIDE") }; vibez.spill("AFTER")`: compiles clean, runs clean, **empty stdout**. The compile log reports `Generated dynamic LLVM IR with 0 strings, 0 variables, 0 calls`. The mere presence of `ready` anywhere in a function drops the entire function body from the captured-calls list — even spills outside the `ready` block don't run. `~/cursed/specs/grammar.md:333-335,409-413` documents `ready` as part of the language; the LLVM IR generator just doesn't handle it and silently drops the function.
**Brat cases blocked:** all 18 cases (no-args needs `ready argv-len < 2`; every other case needs `ready open-failed` to choose between header+content and the bratism error path).
**Upstream framing:** "compiler: lower already-spec'd `ready` conditional to LLVM IR" — minimum: a single `ready <expr> { ... }` form, no `else` branch required for brat's blocking cases. Stop dropping the enclosing function from the captured-calls list.

### loops

**Need:** brat iterates over `argv[1:]` to handle multi-file invocation, and uses a loop to pad the lime block header.
**Status:** silent-miscompile (whole-function-dropping, same as `conditionals`).
**Evidence:** Probe `vibez.spill("BEFORE"); bestie 3 { vibez.spill("INSIDE") }; vibez.spill("AFTER")`: compiles clean, runs clean, empty stdout. Same failure mode as `ready`: the compile log reports zero captured calls; the function body is silently dropped. `~/cursed/specs/grammar.md` documents `bestie` as the loop keyword; not wired into the LLVM IR generator.
**Brat cases blocked:** binary-nul, boundary-46, empty, good-missing-good, long-name, multi-file, multi-missing, multiline-with-eol, one-line-no-eol, spaced-filename, subdir-path, unicode, uppercase-name (every successful-print case needs a padding loop in the header; multi-file/multi-missing/good-missing-good additionally need argv iteration).
**Upstream framing:** "compiler: lower already-spec'd `bestie` loop to LLVM IR" — minimum: `bestie <count> { ... }` (counted form) sufficient for brat's header-padding case. Iterator forms (`bestie x in xs`) would help but aren't strictly required if argv is exposed as indexable.

### argv-access

**Need:** brat reads filenames from argv to decide which files to print.
**Status:** silent-miscompile (silent-zero substitution).
**Evidence:** Probe `vibez.spill("BEFORE"); vibez.spill(argv); vibez.spill("AFTER")` run as `./prog one two three`: prints `BEFORE\n0\nAFTER\n` regardless of arguments. The IR shows `argv` lowered to `call void @cursed_runtime_spill_int(i64 0)`; the compile log says `🔍 DEBUG: Unknown parameter argv defaulted to 0`. Bare `argv` isn't rejected as an unknown identifier — it's silently substituted with integer 0. No documented argv surface anywhere in `~/cursed/specs/`.
**Brat cases blocked:** all 18 cases (every brat case is parameterised by the filename(s) on the command line; no-args is the case that argv-length-zero must distinguish from the rest).
**Upstream framing:** "language: design and implement argv access surface" — minimum: a way to read argv as an iterable or indexable sequence of strings inside `main_character()`. Naming, shape (slice vs. iterator), and length-discovery primitive all need to be designed. *Also* the silent-zero failure mode for unknown identifiers should become a hard error — it bites any probe author who mistypes a name.

### raw-stdout-write

**Need:** brat must emit file bytes verbatim. `vibez.spill` always appends `\n` to its argument and `printf("%s", ...)` truncates at the first NUL byte. brat needs a `(ptr, len)`-shaped, NUL-safe, no-implicit-newline stdout primitive.
**Status:** partial — `vibez.spill` covers line-terminated, NUL-free writes only.
**Evidence:** `cursed_runtime_spill_string` in `~/cursed/src-zig/cursed_runtime.c:7-11` is `printf("%s", str)` with no newline — but the compiler emits an *additional* `cursed_runtime_spill_string(@newline_str)` call after every user spill in the IR. Reproduce: run the `spill_two` probe in `verify_cursed_gaps.sh`; output bytes `41 0a 42 0a` (`A\nB\n`); IR shows two `@newline_str` calls injected. Net effect: every `vibez.spill` call appends `\n`. brat design spec covers this gap at `docs/superpowers/specs/2026-05-09-brat-design.md:55-72,192-201`.
**Brat cases blocked:** binary-nul, boundary-46, good-missing-good, long-name, multi-file, multi-missing, multiline-with-eol, spaced-filename, subdir-path, unicode, uppercase-name. Every successful-print case whose input either contains a NUL byte (`binary-nul`) or ends in `\n` (the other 10 — `vibez.spill` would double the final newline). Two successful-print cases coincidentally work via `vibez.spill`: `empty` (brat's algorithm produces `"\n"` either way) and `one-line-no-eol` (input `"hi"` plus the auto-newline matches the expected `"hi\n"`).
**Upstream framing:** "runtime+stdlib: add byte-faithful stdout primitive" — minimum: `io.write(s tea)` (or `dropz.write_all(stdout, b)`) that emits exactly the bytes given as a `(ptr, len)` pair, no implicit newline, NUL-safe.

## Cases ↔ Gaps

| Case | Gaps blocking |
|------|---------------|
| tests/cases/binary-nul | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |
| tests/cases/boundary-46 | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |
| tests/cases/dash-filename | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, errno-surfacing, stderr-write, exit-code-control |
| tests/cases/directory | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, errno-surfacing, stderr-write, exit-code-control |
| tests/cases/empty | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, loops |
| tests/cases/good-missing-good | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, errno-surfacing, stderr-write, exit-code-control, loops |
| tests/cases/long-name | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |
| tests/cases/missing | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, errno-surfacing, stderr-write, exit-code-control |
| tests/cases/multi-file | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |
| tests/cases/multi-missing | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, errno-surfacing, stderr-write, exit-code-control, loops |
| tests/cases/multiline-with-eol | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |
| tests/cases/no-args | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, stderr-write, exit-code-control |
| tests/cases/one-line-no-eol | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, loops |
| tests/cases/permission-denied | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, errno-surfacing, stderr-write, exit-code-control |
| tests/cases/spaced-filename | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |
| tests/cases/subdir-path | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |
| tests/cases/unicode | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |
| tests/cases/uppercase-name | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops |

## Drops since the original audit

These appeared as gaps in the earlier audit but are not gaps in clean
upstream — the rejections were artifacts of a local-only validator
that has since been reset away (see `docs/cursed-subset.md`). They
work correctly today:

- **Integer arithmetic** (`+`, `-`, `*`, `/`, `%`) — produces correct
  values.
- **Variable assignment** (`x = expr`) — works.
- **Comparisons** (`<`, `==`, `!=` etc.) — produce integer `0`/`1`
  rather than `based`/`cringe`. Numerically correct; if `ready` ever
  works, brat can use them as truthy values without further changes.
