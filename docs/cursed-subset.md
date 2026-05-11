# Cursed compile subset (local cursed main, 2026-05-11)

A brat-local note recording what `cursed-compiler --compile` actually
does today against local `~/cursed` `main`. This is clean upstream
`ghuntley/cursed` (`zig` branch, HEAD = `ecda33d49`) plus the
runtime-path portability fix in `~/cursed` commits `2fa866746` and
`7dafe251c`. Companion to `docs/cursed-gaps.md`, which identifies the
primitives brat needs that aren't reachable here.

## Why this doc exists

An earlier audit (committed earlier in this branch) anchored every
gap section against `~/cursed/specs/current_llvm_subset.md`,
`~/cursed/test_suite/compiler_subset/`, and
`~/cursed/src-zig/supported_subset.zig` — files that *looked* like
upstream sources of truth but were actually three local-only commits,
sitting unpushed on the local `zig` branch for a month. They've since
been reset away (`docs/learnings.md` 2026-05-10 entry has the
chronology). The clean upstream binary has no validator gating layer
and behaves quite differently from the gated one the original audit
used. This doc captures the new picture so future work doesn't
re-anchor on the missing files.

## Reproducer

`experiments/verify_cursed_gaps.sh` builds and runs all 12 probes,
prints exit codes, hex-encoded stdout, and the IR-grep for the
newline-injection finding. Re-run anytime the upstream `zig` branch
moves.

```
bash experiments/verify_cursed_gaps.sh
```

## Failure-mode taxonomy

The compiler doesn't reject much. Almost everything "compiles" (exit
0). But many compiled programs misbehave at runtime in distinct ways,
falling into four buckets. Since `~/cursed` commit `7dafe251c`, clang
link failures now propagate as compiler exit 1 instead of reporting
success with no binary.

### A. Compiles + runs correctly

These primitives are usable today. brat can rely on them:

- One `slay main_character()` entry point with a body
- `vibe main`, `yeet "vibez"`, `yeet "stringz"` headers
- `sus name tea = "literal"` and `sus name normie = 42` declarations
- Variable reassignment: `x = 99` works
- Integer arithmetic: `+`, `-`, `*`, `/`, `%` all produce correct values
- `vibez.spill(s)` for non-NUL strings — see bucket D for the newline catch
- `stringz.concat`, `stringz.length`, `stringz.upper`, `stringz.lower`
- Argless, void user-defined functions — `slay helper() { vibez.spill("hi") }` then `helper()` works

### B. Compiles + runs but produces wrong output (silent miscompile)

Most hostile bucket — no error at compile or run; just wrong values.

- `ready <expr> { ... }` — having `ready` *anywhere* in a function
  drops the entire function body from the captured-calls list.
  Spills outside the `ready` block also stop running. The compile log
  reports `Generated dynamic LLVM IR with 0 strings, 0 variables, 0
  calls`.
- `bestie <expr> { ... }` — same failure mode as `ready`.
- Array literals + indexing — `sus xs [3]normie = [10, 20, 30]` then
  `xs[i]` for any `i` always emits `cursed_runtime_spill_int(i64 1)`.
  Index and array contents are both ignored.
- UDF parameters — `slay greet(name tea) { vibez.spill(name) }` then
  `greet("hello")` prints `0`, not `hello`. Arguments lower to
  integer 0 (same failure mode as `argv`).
- UDF return values — `slay double(x normie) normie { yeet x + x }`
  produces no output at the call site. Returns don't propagate.
- Comparisons — `<`, `==` etc. produce integer `0` or `1` rather than
  `based`/`cringe`. The values are *numerically* correct but typed
  wrong. Combined with bucket B's `ready` failure this is moot for
  brat, but worth noting if `ready` is ever fixed.
- Imports of non-`vibez`/`stringz` modules — `yeet "dropz"` and any
  `dropz.foo(...)` calls silently no-op. No error.

### C. Compiles cursed-side, fails at clang/link

- Member access — `s.length` on a `tea` value emits IR with an
  undefined `@.str.0` reference; clang fails with
  `error: use of undefined value '@.str.0'`, and cursed-compiler now
  exits 1 with `error.ClangFailed`. No binary is produced.

### D. Genuinely missing — no surface to call

- File I/O: no `dropz.read_file`, no bare `read_file` (rejected during
  LLVM code generation with `error.FunctionNotFound`), no `open`/`read`
  runtime helpers.
- stderr writes: `vibez.spill_err`, `vibez.ewrite`, etc. silently
  no-op (bucket B catches them).
- Process exit codes: `os.exit`, `vibez.exit` silently no-op. Return
  from `main_character` always exits 0.
- argv: bare identifier lowers to `cursed_runtime_spill_int(i64 0)`.
  No documented surface to read process arguments.
- Byte-faithful stdout: `vibez.spill(s)` is `printf("%s", str)` in
  `~/cursed/src-zig/cursed_runtime.c:7-11`, then the compiler emits a
  separate `cursed_runtime_spill_string(@newline_str)` call after
  every user spill. Effective behavior: each `spill` appends `\n`
  (compiler-side, not runtime-side). And `printf("%s", ...)` truncates
  at the first NUL byte, so binary content can't pass through.

## Non-goals of this doc

- It is a snapshot, not a contract. Diagnostics and IR shapes will
  drift; re-run the verifier to refresh.
- It does not enumerate everything CURSED documents. Many designed
  features (channels, async, generics, error-handling syntax, FFI,
  HTTP/2, etc.) aren't probed here because brat doesn't need them.
- It does not claim parser-level rejections. Several constructs in
  bucket B *parse* fine and only break at IR generation time.

## Pointers

- `docs/cursed-gaps.md` — what brat needs and how each gap maps to
  the buckets above.
- `experiments/verify_cursed_gaps.sh` — runnable probe set.
- `experiments/probes/*.💀` — earlier individual probe files;
  `verify_cursed_gaps.sh` covers most of the same ground.
- `docs/learnings.md` — the chronology of how this picture came
  together (and the misreads along the way).
