# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`brat` is a `cat`-style file printer written in **CURSED** (Geoffrey Huntley's gen-z-slang esoteric language). Single source file `brat.💀`, compiled to a native binary via `cursed-compiler`.

The aesthetic is **gen-z-coded**, matching CURSED itself: lowercase, terse, slang-inflected. Charli XCX's *brat* (lime `#8ACE00` block headers, lowercase bratism error messages, no flags) is the most visible reference — and CURSED's own site leans on the same album theming — but it's not the only register. Any gen-z-flavoured idiom is in scope; "bestie", "no thoughts", "it's giving" etc. are as on-brand as direct *brat* references. Don't constrain yourself to Charli XCX quotes when picking copy.

## CURSED is half-built — check what actually works first

Most of CURSED's documentation, examples, and reference material is **aspirational design docs, not implemented behavior**. Do not trust syntax you "remember" — the language is too young and too thinly trained-on to guess at.

**Source of truth (brat-local):** `docs/cursed-subset.md` and `experiments/verify_cursed_gaps.sh`. The subset doc is a four-bucket classification of what the upstream `cursed-compiler --compile` accepts/runs today, captured against `ghuntley/cursed` `zig` HEAD. The verifier is the runnable probe set — re-run when in doubt or when upstream moves. Read these before writing or editing any `.💀` code, and re-check when something doesn't compile. If a primitive you need isn't usable per these, note the gap in `docs/cursed-gaps.md`, track upstream issue/PR status in `UPSTREAM.md`, and surface anything genuinely surprising in `docs/learnings.md` rather than inventing syntax. Upstream has no published subset doc — the local files in this repo are the only such doc that exists.

**Runtime semantics live across two layers.** The C runtime (`~/cursed/src-zig/cursed_runtime.c`) is one layer; the IR the compiler emits is the other. The compiler can inject calls the runtime grep won't show (e.g., a `\n`-spill after every `vibez.spill`). When auditing what a primitive *actually does* — print bytes, exit code, fd written — compile a tiny program, run it, inspect bytes/exit. Don't substitute a source read for execution. See `docs/learnings.md` 2026-05-09 "read the runtime, missed the IR."

## Workflow

- **Red-green TDD.** Write the failing test first, watch it fail for the right reason, then implement. The discipline is load-bearing here because CURSED's compiler errors are sparse and misleading — a green test is your main signal that the feature works.
- **Specs and plans are point-in-time snapshots.** `docs/superpowers/specs/` and `docs/superpowers/plans/` capture intent at the moment they were written. If implementation diverges, you do **not** need to retroactively update them unless the divergence is materially important to future readers (e.g. a contract other code depends on). Routine drift is fine.
- **Update `docs/learnings.md` when you're surprised.** The doc has its own "When to update" section — read it. The short version: CURSED limitations, hallucinated syntax, tooling gaps, quotable user remarks. Not for routine green tests or normal commits.
- **Avoid AI-writing tropes in `learnings.md`.** Read `~/tropes/tropes.md` before writing entries. The biggest offender for this doc is **"this changes everything" grandiosity** — small surprises don't "fundamentally reshape" anything; they're just notes. Also watch for `delve`, `tapestry`, `landscape`, `serves as`, magic adverbs (`quietly`, `deeply`), and the urge to inflate a one-paragraph observation into a thesis. Concrete and small beats sweeping every time.
- **Attribute agent commits.** Both Claude and Codex may work in this repo. When an agent creates or amends a commit, include its own `Co-authored-by` trailer so later readers can identify who did the work: `Co-authored-by: Claude <noreply@anthropic.com>` for Claude, and `Co-authored-by: Codex <codex@openai.com>` for Codex. Do not add agent attribution to commits you did not create or amend.
- **Name Claude-only tools when they drove a decision.** Claude has
  skills, slash commands, and `~/.claude` hooks; Codex does not. When
  a Claude-only tool drove a non-trivial decision in this repo, name
  the tool in the commit body so Codex review can replay the
  reasoning.

## Files to keep current

When work changes the relationship between brat and CURSED, update the
tracking docs in the same session:

- `README.md` — public-facing project status or reviewer entry points.
- `UPSTREAM.md` — CURSED issues, PRs, links, status, and which brat gap
  they address.
- `docs/cursed-subset.md` — verified current behavior of
  `cursed-compiler --compile`.
- `docs/cursed-gaps.md` — brat blockers, failure modes, blocked cases,
  and upstream framing.
- `docs/learnings.md` — durable surprises only, using the tag guidance
  in that file.

Keep routine implementation notes out of these docs. Update them when a
future reviewer or agent would otherwise be misled.

**When the trigger is upstream work in `~/cursed`:** the cursed-side
CLAUDE.md describes the `cross-repo-sync` discipline that lands the
brat doc updates here. The Claude skill of the same name automates
the walk; without it, follow the cursed CLAUDE.md `## Cross-Repo Doc
Sync` section.

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
