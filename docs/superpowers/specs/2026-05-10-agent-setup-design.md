# Agent and Tooling Setup for the brat ↔ cursed Loop

Date: 2026-05-10
Status: Approved, pending implementation plan
Scope: `~/brat` and `~/cursed`

## Context

Work for the next stretch is concentrated on CURSED compiler/runtime
fixes in `~/cursed`, motivated by gaps brat surfaces. Both repos are
worked by Claude and Codex, and the two agents review each other's
work. The current setup is functional but leaves the highest-friction
disciplines — TDD on the compiler/runtime, and the cross-repo
tracking-doc updates — entirely to agent memory. This spec captures the
agreed setup changes that move those disciplines into tools, scripts,
and short documents both agents can rely on.

The recommendations are organized as the user asked: agent setup,
Claude setup, skills, other tooling, and repo hygiene. A final section
covers cross-repo concerns that don't fit cleanly under any single
category.

## Goals

- Make the high-friction disciplines (compiler/runtime TDD, cross-repo
  doc sync) cheap to follow and obvious when skipped.
- Keep dual-agent symmetry: nothing Claude does via a skill or hook
  should silently bias work that Codex will review.
- Reduce permission-prompt noise on commands that are already standard.
- Give cursed a place to put session brainstorms without colliding
  with the upstream language specs that already live in `specs/`.

## Out of Scope

The following were considered and explicitly deferred:

- A `commit-msg` hook that enforces `Co-authored-by` agent trailers
  (the hook can't reliably tell who committed; trust CLAUDE.md).
- A repo-scoped Claude model override.
- A `bratism` style skill (the voice guidance fits in CLAUDE.md).
- Reorganizing parallel `src-zig/*_fixed`, `*_complete`,
  `advanced_*`, and `llvm_ir_pipeline_*` files — leaving them is the
  right call; deletion is upstream's.
- A CI workflow for brat — premature without outside contributors.
- The `PreToolUse` "did you re-read cursed-subset?" nudge and a
  `learnings-entry` skill — kept as nice-to-haves, not in this scope.

## Workstreams

### W1. Agent setup

**W1.1 — Codex parity note in both `CLAUDE.md`/`AGENTS.md`.**
Add one paragraph to each repo's `CLAUDE.md` (the symlink covers
`AGENTS.md`) describing the asymmetry: Claude has skills, slash
commands, and `~/.claude` hooks; Codex does not. When a Claude-only
tool drove a non-trivial decision, name it in the commit body so Codex
review can replay the reasoning. Keep the paragraph short and concrete
— the point is to keep cross-agent review honest, not to reproduce
this spec.

**W1.2 — Upstream-branch ritual as a script.**
Add `~/cursed/scripts/upstream-sync.sh` that performs the documented
fork-update sequence: `git fetch upstream`, switch to `zig`, fast-forward
merge from `upstream/zig`, push to `origin/zig`, switch to a
caller-provided topic branch. Refuse to run with a dirty working tree.
Both Claude and Codex call the same script, leaving identical traces.
The script replaces the inline command list in `~/cursed/CLAUDE.md`;
update CLAUDE.md to point at it.

**W1.3 — Make `~/tropes/tropes.md` discoverable from each repo.**
Create symlinks `~/brat/tropes.md → ~/tropes/tropes.md` and
`~/cursed/tropes.md → ~/tropes/tropes.md`, gitignored in both. A fresh
clone on another machine will have a missing-link signal rather than
silently missing the reference. (The alternative — moving tropes into
one canonical repo — was considered and rejected because the file is
useful beyond these two repos.)

### W2. Claude setup

**W2.1 — Per-repo `.claude/settings.json` permission allowlists.**
Run `/fewer-permission-prompts` once in `~/brat` and once in
`~/cursed`. Narrow allowlists only — reproduce the exact commands seen
in recent transcripts (`zig build`, `./zig-out/bin/cursed-compiler`
invocations, `bash experiments/verify_cursed_gaps.sh`, `pytest`
patterns, `cz check`, `git fetch upstream`, `xxd -p`, etc.). No
wildcards beyond what the skill produces. Commit
`.claude/settings.json` per repo.

**W2.2 — `SessionStart` banner in `~/cursed/.claude/settings.json`.**
Three lines, printed at session start:

```
active build target: src-zig/cursed_compiler_main.zig
active runtime: src-zig/cursed_runtime.c
ignore: advanced_*, *_fixed, *_complete, llvm_ir_pipeline_* unless wired in build.zig
```

The `~/cursed/CLAUDE.md` text says this, but it sits ~20 lines deep.
A session-start banner is a far cheaper read. No equivalent for brat.

### W3. Skills

**W3.1 — `cursed-tdd` skill.**
A rigid checklist skill. Triggers when about to fix a CURSED
compiler/runtime behavior. Required steps:

1. Write a minimal failing `.💀` reproducer in `/tmp` and confirm it
   fails for the right reason (not a parse error, etc.).
2. Verify the fix using the bytes-and-exit quartet: stdout via
   `xxd -p`, stderr bytes, exit code, and emitted IR via `--emit-ir`
   when codegen is implicated.
3. Run `~/brat/experiments/verify_cursed_gaps.sh`. New failures are
   blockers unless intentional and called out in the commit body.
4. Update `~/brat/docs/cursed-subset.md` and
   `~/brat/docs/cursed-gaps.md` if the fix moves a gap (see W3.2).

Codex won't invoke the skill, so the same checklist must also live as
a short section in `~/cursed/CLAUDE.md` titled "Compiler/runtime fix
protocol". The skill body and the CLAUDE.md section reference each
other; agents follow whichever they have access to.

**W3.2 — `cross-repo-sync` skill.**
A flexible skill, triggered when a `~/cursed` change closes (or
surfaces) a gap. Walks the four brat tracking files and asks "did this
change require an update?":

- `~/brat/UPSTREAM.md` (issue/PR/status)
- `~/brat/docs/cursed-subset.md` (verified behavior)
- `~/brat/docs/cursed-gaps.md` (failure modes / blocked cases)
- `~/brat/docs/learnings.md` (durable surprises only — re-read the
  doc's own "When to update" section first; load `~/tropes/tropes.md`
  before drafting)

The skill commits the brat-doc update *separately* from the cursed
commit, per `~/cursed/CLAUDE.md`'s existing rule.

A short paragraph in both `CLAUDE.md` files describes the same
discipline so Codex follows it without the skill.

### W4. Other tooling

**W4.1 — Cursed-side probe harness.**
Add `~/cursed/probes/` with a small pytest-driven harness that
compiles `.💀` cases and asserts stdout bytes, stderr bytes, and exit
code. Mirror brat's golden-walker shape: one directory per case with
`source.💀`, `args`, `expected.out`, `expected.err`, `expected.exit`.
Keep the runner simple — invoke `./zig-out/bin/cursed-compiler
--compile --output=/tmp/...` and capture bytes. This is the
load-bearing piece for compiler/runtime work; without it, "fix is
done" rests on ad-hoc /tmp probing.

`make test` continues to run the Zig build target. Add `make probes`
that runs the new harness. Document both in `~/cursed/CLAUDE.md`.

**W4.2 — Wire `verify_cursed_gaps.sh` into cursed `pre-push`.**
On push of a cursed topic branch, run
`bash ~/brat/experiments/verify_cursed_gaps.sh` when the brat checkout
is present at `~/brat` and surface any diff from the recorded subset as
a warning (not a blocker). Add a `CURSED_SKIP_DOWNSTREAM_CHECK=1`
environment-variable escape hatch. When `~/brat` is missing (other
machine, moved checkout), fall through silently.

### W5. Repo hygiene

**W5.1 — Create `~/cursed/docs/superpowers/{specs,plans}/`.**
Empty directories with a one-line `README.md` in each documenting the
naming convention (`YYYY-MM-DD-<topic>-design.md` /
`YYYY-MM-DD-<topic>-plan.md`).

**W5.2 — Disambiguation sentence in `~/cursed/CLAUDE.md`.**
One sentence under a new `## Spec Locations` heading: "`specs/` holds
upstream language specs; do not put session work there.
`docs/superpowers/specs/` and `docs/superpowers/plans/` hold session
brainstorms with date-prefixed filenames."

## Cross-Repo Concerns

The `~/cursed`→`~/brat` doc-update obligation is the most failure-prone
discipline in the current setup. W3.2 (`cross-repo-sync` skill plus
parallel CLAUDE.md paragraph) is the primary fix. W4.2
(`verify_cursed_gaps.sh` in pre-push) is the secondary fix — it catches
a regression even when the doc-update step was skipped.

Two post-commit auto-pushes can fire back-to-back when an agent
commits in both repos. This is intended (best-effort backup), but
worth knowing for incident debugging if a push appears unauthorized.

## Sequencing

The workstreams are mostly independent, but a sensible order is:

1. W5 (cursed `docs/superpowers/` directories and CLAUDE.md sentence)
   — unblocks any brainstorming done in cursed, including W3 if the
   skills get spec'd there.
2. W1.1 + W1.3 (CLAUDE.md Codex paragraph, tropes symlinks) —
   small, lands the dual-agent and shared-references decisions.
3. W4.1 (probes harness) — biggest single piece; everything below
   benefits from being able to run probes from a real harness.
4. W3.1 (`cursed-tdd` skill + CLAUDE.md section) — leans on W4.1.
5. W3.2 (`cross-repo-sync` skill + CLAUDE.md section) — independent
   of W4.1 but should land after W3.1 to keep skill conventions
   consistent.
6. W1.2 (`upstream-sync.sh`) — small, independent.
7. W2.1 + W2.2 (`.claude/settings.json` per repo, SessionStart
   banner) — landed once the rest is settled, so the allowlists
   reflect the new commands (`make probes`, `scripts/upstream-sync.sh`).
8. W4.2 (pre-push hook) — last; depends on W4.1 being trusted.

## Success Criteria

- A fresh session in `~/cursed` shows the active-path banner; common
  commands no longer prompt for permission.
- `make probes` exists and exercises at least one runtime behavior.
- `bash ~/brat/experiments/verify_cursed_gaps.sh` runs as part of
  cursed `pre-push` (non-blocking).
- `cursed-tdd` and `cross-repo-sync` skills exist and are invoked on
  the next CURSED-fix session; their checklists are duplicated as
  short sections in `CLAUDE.md` so Codex follows the same discipline.
- `~/cursed/docs/superpowers/{specs,plans}/` exist; the next
  cursed-side brainstorm lands there, not in `specs/`.
- Both `CLAUDE.md` files include the Codex parity paragraph and
  reference the cross-repo-sync discipline.
- `~/brat/tropes.md` and `~/cursed/tropes.md` exist as symlinks to
  `~/tropes/tropes.md` and are gitignored.
