# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`brat` is a `cat`-style file printer written in **CURSED** (Geoffrey Huntley's gen-z-slang esoteric language). Single source file `brat.💀`, compiled to a native binary via `cursed-compiler`.

The aesthetic is **gen-z-coded**, matching CURSED itself: lowercase, terse, slang-inflected. Charli XCX's *brat* (lime `#8ACE00` block headers, lowercase bratism error messages, no flags) is the most visible reference — and CURSED's own site leans on the same album theming — but it's not the only register. Any gen-z-flavoured idiom is in scope; "bestie", "no thoughts", "it's giving" etc. are as on-brand as direct *brat* references. Don't constrain yourself to Charli XCX quotes when picking copy.

## CURSED is half-built — check what actually works first

Most of CURSED's documentation, examples, and reference material is **aspirational design docs, not implemented behavior**. Do not trust syntax you "remember" — the language is too young and too thinly trained-on to guess at.

**Source of truth:** `~/cursed/specs/current_llvm_subset.md` lists what the compiler actually supports today. Read it before writing or editing any `.💀` code, and re-check when something doesn't compile. If a primitive you need isn't in the subset doc, it doesn't exist yet — note the gap in `docs/learnings.md` (see below) rather than inventing syntax.

## Workflow

- **Red-green TDD.** Write the failing test first, watch it fail for the right reason, then implement. The discipline is load-bearing here because CURSED's compiler errors are sparse and misleading — a green test is your main signal that the feature works.
- **Specs and plans are point-in-time snapshots.** `docs/superpowers/specs/` and `docs/superpowers/plans/` capture intent at the moment they were written. If implementation diverges, you do **not** need to retroactively update them unless the divergence is materially important to future readers (e.g. a contract other code depends on). Routine drift is fine.
- **Update `docs/learnings.md` when you're surprised.** The doc has its own "When to update" section — read it. The short version: CURSED limitations, hallucinated syntax, tooling gaps, quotable user remarks. Not for routine green tests or normal commits.
- **Avoid AI-writing tropes in `learnings.md`.** Read `~/tropes/tropes.md` before writing entries. The biggest offender for this doc is **"this changes everything" grandiosity** — small surprises don't "fundamentally reshape" anything; they're just notes. Also watch for `delve`, `tapestry`, `landscape`, `serves as`, magic adverbs (`quietly`, `deeply`), and the urge to inflate a one-paragraph observation into a thesis. Concrete and small beats sweeping every time.

## Commands

```bash
# Run the full test suite (requires the brat binary)
pytest

# Run a single case
pytest tests/test_brat.py -k <case-name>

# Regenerate goldens after a deliberate output change (only when you trust current output)
BRAT_UPDATE_GOLDENS=1 pytest tests/test_brat.py
# Then review the diff carefully before committing.

# Point tests at a non-default binary
BRAT_BIN=/path/to/brat pytest
```

CI sets `CI=1`; the suite refuses to run with `BRAT_UPDATE_GOLDENS=1` under CI.

## Test architecture

- **Golden-file walker** (`tests/test_brat.py`): one parametrized test per `tests/cases/<name>/` directory. Each case has `args`, `inputs/`, `expected.out`, `expected.err`, `expected.exit`, and optionally `modes` (octal chmods applied to `inputs/` files before the run, restored after). Adding a case = adding a directory; no test code changes needed.
- **Header unit tests** (`tests/test_header.py`): pin the ANSI byte sequences and block-header geometry from the spec. If you change the visual output, these will fail loudly.
- **Harness smoke tests** (`tests/test_harness_smoke.py`): validate the subprocess capture machinery against a fake binary, independent of `./brat`. If real-case tests fail in confusing ways, check these first to rule out the harness.
- **Backpressure guards** (in `test_brat.py`): case completeness, `MIN_CASES` floor, exit-code range, and an inputs/ mutation check per case. Bump `MIN_CASES` deliberately when adding cases.

`modes`-using cases auto-skip when the suite runs as root (chmod-based access denial is a no-op under root).
