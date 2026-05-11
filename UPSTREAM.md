# Upstream CURSED Tracker

This file tracks CURSED compiler/runtime work motivated by brat. It is
intended for quick linking from issues and pull requests against
[`ghuntley/cursed`](https://github.com/ghuntley/cursed).

brat is a small downstream program, not a CURSED conformance suite. Each
entry below should be understood as: "this primitive is needed for brat's
native-compiled `cat`-style behavior, and here is the current minimal
evidence."

## Reviewer Entry Points

- Current behavior snapshot:
  [`docs/cursed-subset.md`](docs/cursed-subset.md)
- Full gap audit:
  [`docs/cursed-gaps.md`](docs/cursed-gaps.md)
- Runnable probe set:
  [`experiments/verify_cursed_gaps.sh`](experiments/verify_cursed_gaps.sh)
- Golden test cases:
  [`tests/cases/`](tests/cases/)

Run the probe set with:

```bash
bash experiments/verify_cursed_gaps.sh
```

## Tracker

| CURSED gap | brat needs it for | Current evidence | Upstream issue | Upstream PR | Status |
|---|---|---|---|---|---|
| `dropz.read_file` or equivalent file read | Reading every file argument | `docs/cursed-gaps.md#file-read` | Not filed | Not filed | Open |
| errno surfacing from file read | Distinguishing missing, denied, directory, and generic read failures | `docs/cursed-gaps.md#errno-surfacing` | Not filed | Not filed | Open |
| argv access | Deciding no-args vs file args, then iterating filenames | `docs/cursed-gaps.md#argv-access` | Not filed | Not filed | Open |
| stderr write | Printing bratism errors separately from stdout | `docs/cursed-gaps.md#stderr-write` | Not filed | Not filed | Open |
| exit-code control | Returning non-zero when any file fails | `docs/cursed-gaps.md#exit-code-control` | Not filed | Not filed | Open |
| raw stdout write | Emitting file bytes verbatim without implicit newline or NUL truncation | `docs/cursed-gaps.md#raw-stdout-write` | Not filed | Not filed | Open |
| native compile runtime path portability | Running `cursed-compiler --compile` from a checkout that is not `/home/ghuntley/cursed` | `docs/learnings.md#2026-05-10--i-re-authorized-the-symlink-workaround` | Not filed | Local branch `fix-runtime-path-upstream` | Local fix |
| non-`vibez` / `stringz` stdlib imports | Reaching whichever modules provide file I/O, stderr, and exit | `docs/cursed-gaps.md#non-stdlib-imports` | Not filed | Not filed | Open |
| user-defined function parameters and returns | Factoring header and error-message helpers out of `main_character` | `docs/cursed-gaps.md#user-defined-functions` | Not filed | Not filed | Open |
| member access / selector lowering | Calling stdlib-style APIs and reading result fields | `docs/cursed-gaps.md#member-access` | Not filed | Not filed | Open |
| array literals and indexing | Reading `argv[i]` and working with argument sequences | `docs/cursed-gaps.md#array-literals-and-indexing` | Not filed | Not filed | Open |
| `ready` conditionals | Branching on no args and per-file read errors | `docs/cursed-gaps.md#conditionals` | Not filed | Not filed | Open |
| `bestie` loops | Iterating filenames and padding headers | `docs/cursed-gaps.md#loops` | Not filed | Not filed | Open |

## PR Linking Template

When opening a CURSED PR, use a short downstream note like this:

````markdown
Downstream motivation: this unblocks part of brat, a small `cat`-style
program used to exercise native-compiled CURSED behavior.

brat tracker: https://github.com/jonathandeamer/brat/blob/master/UPSTREAM.md
brat gap: https://github.com/jonathandeamer/brat/blob/master/docs/cursed-gaps.md#<gap-anchor>

Minimal reproducer:

```cursed
vibe main
yeet "vibez"

slay main_character() {
    // reduced CURSED program here
}
```

Command:

```bash
./zig-out/bin/cursed-compiler --compile --output=/tmp/repro repro.💀
/tmp/repro
```

Expected:

```text
...
```

Actual before this PR:

```text
...
```
````

Keep the CURSED issue/PR focused on the language primitive. Mention brat
as the downstream motivation, but avoid implementing brat-specific logic
in CURSED.
