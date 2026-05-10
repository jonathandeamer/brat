# CURSED Gaps for brat

A per-primitive roadmap of what CURSED is missing for brat to be
implementable. Captured as of 2026-05-09. Diagnostics may drift; this
doc is a snapshot, not a live contract.

## Gap entry conventions

Each gap has:

- **Need:** what brat needs this for, in one sentence.
- **Status:** `missing` | `partial` | `broken` (implementation state per
  `~/cursed/specs/current_llvm_subset.md`).
- **Design status:** `spec'd` (with a `~/cursed/specs/*.md` citation) or
  `undesigned` (no documented surface).
- **Evidence:** runtime-C citation, subset-doc quote, fenced probe
  output, or compiler_subset fixture filename — at least one.
- **Brat cases blocked:** list of `tests/cases/<name>` dirs.
- **Upstream framing:** one-line issue title + the minimal surface that
  would unblock brat.

## Gaps

<!-- one section per gap below -->

### stderr-write

**Need:** brat writes its `cat:` error messages to stderr.
**Status:** missing.
**Design status:** spec'd at the stdlib-design level but absent from the implemented subset — `~/cursed/specs/stdlib/main_character.md:125` documents an `ErrorVibe = NewVibeFile(uintptr(syscall.Stderr), "/dev/stderr")` handle and `~/cursed/specs/stdlib/dropz.md:172` mentions a `stderr Writer`, but `~/cursed/specs/current_llvm_subset.md:25-35` lists only `vibez.spill` and four `stringz` calls in the implemented stdlib slice.
**Evidence:** `~/cursed/src-zig/cursed_runtime.c:1-42` — only `cursed_runtime_spill_string/_int/_float/_bool` exist, all writing via `printf`/`fflush(stdout)`. No `fprintf`, no `stderr`, no write-to-fd-2 path anywhere in the runtime. Confirmed by execution: a baseline program (`vibez.spill("hi")`) compiled and run as `./prog 2>err.txt 1>out.txt` yields zero bytes on stderr — no IR-level injection writes to fd 2 either, so the runtime read isn't hiding a compiler-side path.
**Brat cases blocked:** dash-filename, directory, good-missing-good, missing, multi-missing, no-args, permission-denied.
**Upstream framing:** "runtime: add stderr write surface" — minimum: a `vibez.spill_err(s)` (or equivalent) that maps to `fprintf(stderr, ...)`.

### exit-code-control

**Need:** brat must exit non-zero when any file fails to read, so `cat`-style pipelines can detect failure.
**Status:** missing.
**Design status:** spec'd at the stdlib-design level — `~/cursed/specs/stdlib/main_character.md:89` documents `slay VibeOut(code normie)` ("Exits with status code (like os.Exit)") — but absent from the implemented subset (`~/cursed/specs/current_llvm_subset.md:25-35`). `~/cursed/specs/error_handling.md` does not document a process-exit primitive at all.
**Evidence:** `~/cursed/src-zig/cursed_runtime.c:1-42` — no `exit(`, `_exit`, or `abort` symbol referenced; the runtime exposes only the four `spill_*` print helpers, so the exit code of any compiled program is whatever `main` returns by default. Confirmed by execution: the baseline program above exits 0; the existing `experiments/probes/argv-access.💀` binary also exits 0 despite the compile-time "Variable argv not found" warning. Across success and induced-error paths, `$?` is always 0.
**Brat cases blocked:** dash-filename, directory, good-missing-good, missing, multi-missing, no-args, permission-denied.
**Upstream framing:** "runtime: expose process exit primitive" — minimum: a `vibe_life.exit(code normie)` (or `os.exit`) that maps to libc `exit(int)`.

### file-read

**Need:** brat must read the bytes of each file named on the command line.
**Status:** missing.
**Design status:** spec'd at the stdlib-design level — `~/cursed/specs/stdlib/dropz.md:59-99` documents `slay read_file(filename tea) ([]byte, tea)`, `read_text_file`, `open`, `open_file`, and `(f *File) read` — but absent from the implemented subset (`~/cursed/specs/current_llvm_subset.md:25-35`).
**Evidence:** `~/cursed/src-zig/cursed_runtime.c:1-42` — no `fopen`, `fread`, `read`, or `open` symbol; the runtime is entirely `printf`-shaped output helpers. No file-read entry point exists for the compiler to lower a `dropz` call against. Confirmed by probe: every `dropz`-import shape (`dropz.read_file`, `dropz.open`, `dropz.Read`, `fs.read_file`, `io.read_all`) is rejected at the *import* with ``unsupported import `dropz`; only `vibez` and `stringz` are supported in LLVM compile mode``. A bare `read_file(...)` call (no import) is rejected as ``user-defined function calls are unsupported``. There is no surface that reaches a file-read at all.
**Brat cases blocked:** all 18 cases except no-args (no-args never opens a file).
**Upstream framing:** "runtime+stdlib: implement `dropz.read_file`" — minimum: a `dropz.read_file(path tea) ([]byte, tea)` that maps to libc `fopen`/`fread`/`fclose` and surfaces errno-shaped errors.

### non-stdlib-imports

**Need:** brat needs whichever stdlib module owns file I/O, stderr, and exit (e.g. `dropz`, `main_character`). Today only `vibez` and `stringz` imports compile.
**Status:** missing — actively rejected by the compiler.
**Design status:** spec'd as a hard failure. `~/cursed/specs/current_llvm_subset.md:39-46` enumerates "Unsupported imports such as `mathz`, `collections`, or selective import forms" as constructs the compiler must reject with diagnostics.
**Evidence:** fixture `~/cursed/test_suite/compiler_subset/unsupported_import.💀:1-7` imports `"mathz"`; the assertion in `~/cursed/test_suite/compiler_subset/test_compiler_subset.sh:56-59` expects the compile to fail with the diagnostic fragment ``unsupported import `mathz` ``.
**Brat cases blocked:** all 18 cases (every brat program needs at least one non-`vibez`/`stringz` import — `dropz` for file I/O, plus whichever module owns stderr/exit).
**Upstream framing:** "compiler: widen import allow-list as new stdlib modules land" — coupled to whichever runtime/stdlib gap (file-read, stderr-write, exit-code-control) is being unblocked.

### user-defined-functions

**Need:** brat needs helpers (e.g. `print_block_header`, `brat_message_for`) factored out of `main_character`. The design spec assumes ordinary user-defined functions.
**Status:** missing — actively rejected by the compiler.
**Design status:** spec'd in the grammar (`~/cursed/specs/grammar.md:333-335,399-413` describes the full `PrimaryExpr ... Arguments` call form and selector/method machinery) but explicitly excluded from the implemented subset. `~/cursed/specs/current_llvm_subset.md:18-22,39-46` restricts programs to "A single `slay main_character()` entry point" and lists "User-defined function calls" as a hard-fail construct.
**Evidence:** fixture `~/cursed/test_suite/compiler_subset/unsupported_user_call.💀:1-10` defines `slay greet(name tea)` alongside `main_character` and calls it; the assertion in `~/cursed/test_suite/compiler_subset/test_compiler_subset.sh:71-74` expects the compile to fail with the diagnostic fragment ``only `slay main_character()` is supported``.
**Brat cases blocked:** all 18 cases (the design factors `print_block_header` and `brat_message_for` out of `main_character`; without user-defined `slay`, every case has to inline everything into one entry point).
**Upstream framing:** "compiler: support user-defined `slay` declarations and calls" — minimum: top-level `slay name(args) { ... }` with parameters, return values, and call-site lowering.

### member-access

**Need:** brat's design spec uses method-call / selector syntax extensively (`io.write`, `os.argv`, `state.ExitCode()`); even simple field reads like `result.err` are out of reach.
**Status:** missing — actively rejected by the compiler.
**Design status:** spec'd in the grammar (`~/cursed/specs/grammar.md:333-335,409-412` defines `Selector = "." identifier` and `PrimaryExpr Selector` as a productive form) but explicitly excluded from the implemented subset (`~/cursed/specs/current_llvm_subset.md:39-46`: "Member access expressions" listed as a hard-fail construct). `~/cursed/specs/types.md` defines composite types whose fields presuppose selector access.
**Evidence:** fixture `~/cursed/test_suite/compiler_subset/unsupported_member_access.💀:1-7` does `vibez.spill(msg.length)`; the assertion in `~/cursed/test_suite/compiler_subset/test_compiler_subset.sh:61-64` expects the compile to fail with the diagnostic fragment "member access is unsupported". Stdlib calls like `vibez.spill` are recognised as a special-cased form, not general member access.
**Brat cases blocked:** all 18 cases (the design uses `os.argv`, `state.ExitCode()`, and `result.err`-shaped reads throughout; even the no-args branch needs `os.argv` length).
**Upstream framing:** "compiler: implement general selector / member-access lowering" — minimum: `expr.field` and `expr.method(args)` for user types and stdlib values, not just hard-coded `module.fn` patterns.

### array-literals-and-indexing

**Need:** brat takes a list of filenames from argv and iterates over them; the design spec walks `argv[1:]`. No array literal, no slice, no index expression compiles today.
**Status:** missing — actively rejected by the compiler.
**Design status:** spec'd in the grammar and types (`~/cursed/specs/grammar.md:110-116,335,413` — `ArrayType`, `PrimaryExpr Index`, `Index = "[" Expression "]"`; `~/cursed/specs/types.md:43-44,122,127` — array and slice types with indexable values) but explicitly excluded from the implemented subset (`~/cursed/specs/current_llvm_subset.md:39-46`: "Array literals, array indexing, and slice access" listed as hard-fail constructs).
**Evidence:** fixture `~/cursed/test_suite/compiler_subset/unsupported_array_access.💀:1-7` declares `sus nums [3]normie = [1, 2, 3]` and reads `nums[1]`; the assertion in `~/cursed/test_suite/compiler_subset/test_compiler_subset.sh:66-69` expects the compile to fail with the diagnostic fragment "array literals are unsupported".
**Brat cases blocked:** all 18 cases (every brat program reads `argv[i]` at least once — even no-args needs to test `len(argv) < 2`, which requires argv to be a sequence).
**Upstream framing:** "compiler: support array/slice literals, types, and index expressions" — minimum: `[N]T` storage, `[v1, v2, ...]` literals, and `e[i]` index expressions, lowered for at least `tea` and `normie` element types.

### conditionals

**Need:** brat branches on argv length (zero args → error; otherwise iterate files) and on per-file open errors.
**Status:** broken — the `ready` keyword is in the grammar but the supported-subset validator does not recognise the resulting AST as containing `main_character()`, so a program with one `ready` block inside `main_character()` fails with `MissingMainCharacter`.
**Design status:** spec'd — `~/cursed/specs/grammar.md:173-204` (IfStmt: `"ready" [ SimpleStmt ";" ] Expression Block [ "otherwise" ( IfStmt | Block ) ]`).
**Evidence:** see `experiments/probes/conditionals.💀`. Diagnostic from `cursed-compiler --compile`:

```
error: LLVM compile mode requires exactly one `slay main_character()` entry point
error: MissingMainCharacter
/home/ec2-user/cursed/src-zig/supported_subset.zig:43:9: 0x11f4e8a in validateProgram (cursed_compiler_main.zig)
        return error.MissingMainCharacter;
        ^
/home/ec2-user/cursed/src-zig/cursed_compiler_main.zig:178:5: 0x11e5fb8 in compileToExecutable (cursed_compiler_main.zig)
    try supported_subset.validateProgram(&program);
    ^
/home/ec2-user/cursed/src-zig/cursed_compiler_main.zig:111:9: 0x11e88fa in main (cursed_compiler_main.zig)
        try compileToExecutable(allocator, source, filename.?, output_name.?, verbose, debug_mode, optimize, emit_ir);
        ^
```

The diagnostic is a misleading proxy: the program plainly has `slay main_character()`, but introducing `ready` somewhere along the parse / subset-validation path makes the validator stop seeing it. Effectively conditionals are unreachable from the LLVM compile pipeline today.

**Brat cases blocked:** all 18 cases (no-args needs `ready argv-len < 2`; every other case needs `ready open-failed` to choose between header+content and the bratism error path).
**Upstream framing:** "compiler: lower already-spec'd `ready` conditional to LLVM IR" — minimum: a single `ready <expr> { ... }` form inside `main_character()`, no `otherwise` branch required for brat's blocking cases.

### argv-access

**Need:** brat reads filenames from argv to decide which files to print.
**Status:** missing — `argv` as a bare identifier is silently defaulted to `0`, so there is no way to read process arguments from a compiled CURSED program.
**Design status:** undesigned — no documented surface in `~/cursed/specs/`. Probed against the most plausible shape (bare `argv` identifier).
**Evidence:** see `experiments/probes/argv-access.💀`. Diagnostic from `cursed-compiler --compile`:

```
🔧 Processing import: yeet "vibez"
📚 Loading stdlib module: vibez
❌ Failed to load module vibez: error.FileNotFound
🔧 Declaring LLVM function: main_character
📝 Stored AST for function: main_character
⚠️ Variable argv not found, returning 0
🔍 DEBUG: Unknown parameter argv defaulted to 0
🔍 Generating dynamic LLVM IR from 1 captured calls and 1 variables
✅ Generated dynamic LLVM IR with 0 strings, 1 variables, 1 calls
🔧 Compiling to native binary: clang -O2 -o /tmp/argv_probe /tmp/argv_probe.ll /home/ghuntley/cursed/src-zig/cursed_runtime.c
🎉 Successfully compiled CURSED program to native binary: /tmp/argv_probe
💡 Run with: .//tmp/argv_probe
```

The diagnostic itself is unhelpful — the compiler doesn't reject `argv`, it just warns "Variable argv not found, returning 0" and produces a binary that ignores process arguments. This is evidence that no argv surface exists rather than evidence of an error message about argv specifically.

Runtime confirmation: `vibez.spill("BEFORE"); vibez.spill(argv); vibez.spill("AFTER")` compiled and run as `./prog one two three` prints `BEFORE\n0\nAFTER\n` regardless of arguments. The emitted IR shows `argv` lowered to `call void @cursed_runtime_spill_int(i64 0)` — the silent default is *typed* as integer 0, not an empty string or null. Worse than missing: any brat-shaped program that reads `argv` will silently substitute `0` and produce nonsense, with no compile-time or run-time error.

**Brat cases blocked:** all 18 cases (every brat case is parameterised by the filename(s) on the command line; no-args is the case that argv-length-zero must distinguish from the rest).
**Upstream framing:** "language: design and implement argv access surface" — minimum: a way to read argv as an iterable or indexable sequence of strings inside `main_character()`. Naming, shape (slice vs. iterator), and length-discovery primitive all need to be designed.

### raw-stdout-write

**Need:** brat must emit file bytes verbatim. `vibez.spill` is the only documented stdout path and it always appends `\n` to its argument — so it can't print files that don't end in newline (it'd add one), can't print files that do (it'd double it), and `printf("%s", ...)` truncates at the first NUL byte. brat needs a `(ptr, len)`-shaped, NUL-safe, no-implicit-newline stdout primitive.
**Status:** partial — `vibez.spill` covers line-terminated, NUL-free writes only.
**Design status:** undesigned in the implemented subset — `~/cursed/specs/current_llvm_subset.md:25-35` lists only `vibez.spill` for output; no `io.write`, `dropz.write`, or `slay_io` byte-write entry point appears in the supported stdlib slice. `~/cursed/specs/stdlib/dropz.md` documents Reader/Writer interfaces and a `Write(b []byte)` shape, but none of it is reachable from a compiled program today.
**Evidence:** `cursed_runtime_spill_string` in `~/cursed/src-zig/cursed_runtime.c:7-11` is `printf("%s", str)` with no newline — but the compiler emits an *additional* `cursed_runtime_spill_string(@newline_str)` call after every user spill in the LLVM IR. Reproduce: compile `vibez.spill("A"); vibez.spill("B")` with `--emit-ir` (or read `/tmp/<name>.ll` after `--compile`), grep for `@newline_str` and `call void @cursed_runtime_spill_string`. Output bytes: `A\nB\n`. Net effect: every `vibez.spill` call appends `\n`. brat design spec covers this gap at `docs/superpowers/specs/2026-05-09-brat-design.md:55-72,192-201`.
**Brat cases blocked:** binary-nul, boundary-46, empty, good-missing-good, long-name, multi-file, multi-missing, multiline-with-eol, one-line-no-eol, spaced-filename, subdir-path, unicode, uppercase-name. Every successful-print case: `vibez.spill` would either double the trailing newline (files ending in `\n`) or add one where there is none (`one-line-no-eol`, `empty`), and would truncate at the NUL byte for `binary-nul`. The five pure-error cases (dash-filename, directory, missing, no-args, permission-denied) write only bratisms to stderr, so they don't depend on this surface.
**Upstream framing:** "runtime+stdlib: add byte-faithful stdout primitive" — minimum: `io.write(s tea)` (or `dropz.write_all(stdout, b)`) that emits exactly the bytes given as a `(ptr, len)` pair, no implicit newline, NUL-safe.

### errno-surfacing

**Need:** brat's bratism error messages branch on errno (`ENOENT → never heard of her`, `EACCES → said no`, `EISDIR → is a directory fam`, otherwise `is not giving`). Without an errno surface from the file-open path, brat cannot distinguish "missing" from "permission denied" from "is a directory".
**Status:** missing.
**Design status:** spec'd at the stdlib-design level — `~/cursed/specs/stdlib/dropz.md:59-99` describes `read_file(filename tea) ([]byte, tea)` with a paired error value, and `docs/superpowers/specs/2026-05-09-brat-design.md:154-160` enumerates the brat-side errno mapping — but absent from the implemented subset (`~/cursed/specs/current_llvm_subset.md:25-35` exposes no error type, errno value, or `(value, err)` tuple).
**Evidence:** `~/cursed/src-zig/cursed_runtime.c:1-42` — the entire runtime is the four `spill_*` print helpers, no `errno.h` include, no `errno`-shaped global, no error-returning entry point. There is no path from a compiled CURSED program to the libc errno value.
**Brat cases blocked:** dash-filename, directory, good-missing-good, missing, multi-missing, permission-denied.
**Upstream framing:** "runtime+stdlib: surface libc errno from `dropz.read_file`" — minimum: `read_file` returns a paired `(bytes, errno_or_zero)` (or named error value) so brat can branch the four bratisms.

### loops

**Need:** brat iterates `argv[1:]` over filenames and (per the design's header geometry) loops to emit padding spaces inside the lime block header.
**Status:** missing — `bestie` loops fail the same `MissingMainCharacter` proxy diagnostic as `ready` (the supported-subset validator stops seeing `slay main_character()` once a loop body is present).
**Design status:** spec'd — `~/cursed/specs/grammar.md:232,241-249` documents `ForStmt = "bestie" [ Condition | ForClause | RangeClause ] Block` with C-style, while-style, and infinite forms.
**Evidence:** see `experiments/probes/loops.💀`. Diagnostic from `cursed-compiler --compile`:

```
error: LLVM compile mode requires exactly one `slay main_character()` entry point
error: MissingMainCharacter
/home/ec2-user/cursed/src-zig/supported_subset.zig:43:9: 0x11f4e8a in validateProgram (cursed_compiler_main.zig)
        return error.MissingMainCharacter;
        ^
```

Same misleading proxy as the conditionals gap — `slay main_character()` is plainly present, but a `bestie` body inside it makes the validator stop recognising it.

**Brat cases blocked:** binary-nul, boundary-46, empty, good-missing-good, long-name, multi-file, multi-missing, multiline-with-eol, one-line-no-eol, spaced-filename, subdir-path, unicode, uppercase-name (every successful-print case needs a padding loop in the header; multi-file/multi-missing/good-missing-good additionally need argv iteration).
**Upstream framing:** "compiler: lower already-spec'd `bestie` loops to LLVM IR" — minimum: a single `bestie <cond> { ... }` form inside `main_character()`, sufficient to drive both the argv walk and the header padding write.

### binary-expressions

**Need:** brat compares argv length against zero to choose the no-args branch, computes `pad = max_width - len(filename)` for header geometry, and tests `errno == N` to map to bratism strings. All three are binary expressions.
**Status:** missing — the supported-subset validator rejects all binary expressions, including `+`, `-`, `<`, and `==`.
**Design status:** spec'd in the grammar (`~/cursed/specs/grammar.md` defines arithmetic, comparison, and logical operators) but explicitly excluded by the implemented validator.
**Evidence:** see `experiments/probes/integer-arithmetic.💀`. Diagnostic from `cursed-compiler --compile`:

```
error: expression `Binary` is unsupported in the current LLVM subset
error: UnsupportedConstruct
/home/ec2-user/cursed/src-zig/supported_subset.zig:126:13: 0x12ec97b in validateSupportedExpression (cursed_compiler_main.zig)
            return error.UnsupportedConstruct;
            ^
```

Probe content was `sus c normie = a + b` over two `normie` locals, the smallest arithmetic shape; the validator rejects all `Binary` AST nodes uniformly, so comparison (`<`, `==`) lands in the same path.

**Brat cases blocked:** all 18 cases (no-args needs `argv-len < 2`; every other case needs both header pad arithmetic and at least one `errno == N` comparison).
**Upstream framing:** "compiler: lower binary expressions to LLVM IR" — minimum: integer `+`/`-`/`<`/`==` over `normie`, plus `tea`-comparison if the errno mapping is keyed on string equality instead of int.

### assignment-statement

**Need:** any loop that walks argv or builds up a padding string mutates a counter or accumulator (`i = i + 1`, `pad = pad + " "`). brat's design walks `argv[1:]` in a `bestie` loop and increments through it.
**Status:** missing — the supported-subset validator rejects assignment statements; only variable declarations and expression statements are accepted.
**Design status:** spec'd — `~/cursed/specs/grammar.md` includes assignment as a statement form — but explicitly excluded by the implemented validator.
**Evidence:** see `experiments/probes/assignment.💀`. Diagnostic from `cursed-compiler --compile`:

```
error: statement `Assignment` is unsupported in the current LLVM subset; supported statements are variable declarations and expression statements
error: UnsupportedConstruct
/home/ec2-user/cursed/src-zig/supported_subset.zig:92:13: 0x12980f6 in validateSupportedStatement (cursed_compiler_main.zig)
            return error.UnsupportedConstruct;
            ^
```

The validator's own diagnostic enumerates the allow-list ("variable declarations and expression statements"); assignment is a hard exclusion.

**Brat cases blocked:** binary-nul, boundary-46, empty, good-missing-good, long-name, multi-file, multi-missing, multiline-with-eol, one-line-no-eol, spaced-filename, subdir-path, unicode, uppercase-name (every loop body brat needs — argv walk or header padding — assigns to a counter).
**Upstream framing:** "compiler: lower assignment statements to LLVM IR" — minimum: `name = expr` for already-declared locals.

## Cases ↔ Gaps

| Case | Gaps blocking |
|------|---------------|
| tests/cases/binary-nul | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/boundary-46 | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/dash-filename | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, errno-surfacing, stderr-write, exit-code-control, binary-expressions |
| tests/cases/directory | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, errno-surfacing, stderr-write, exit-code-control, binary-expressions |
| tests/cases/empty | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/good-missing-good | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, errno-surfacing, stderr-write, exit-code-control, loops, binary-expressions, assignment-statement |
| tests/cases/long-name | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/missing | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, errno-surfacing, stderr-write, exit-code-control, binary-expressions |
| tests/cases/multi-file | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/multi-missing | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, errno-surfacing, stderr-write, exit-code-control, loops, binary-expressions, assignment-statement |
| tests/cases/multiline-with-eol | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/no-args | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, stderr-write, exit-code-control, binary-expressions |
| tests/cases/one-line-no-eol | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/permission-denied | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, errno-surfacing, stderr-write, exit-code-control, binary-expressions |
| tests/cases/spaced-filename | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/subdir-path | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/unicode | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
| tests/cases/uppercase-name | non-stdlib-imports, user-defined-functions, member-access, array-literals-and-indexing, conditionals, argv-access, file-read, raw-stdout-write, loops, binary-expressions, assignment-statement |
