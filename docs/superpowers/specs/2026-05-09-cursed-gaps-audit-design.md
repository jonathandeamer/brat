# CURSED Gaps Audit — Design

**Date:** 2026-05-09
**Status:** approved (brainstorm) — pending implementation plan

## Purpose

Produce a per-primitive roadmap of what CURSED is missing for brat to be
implementable. The artifact is a doc that doubles as:

- a check on which brat test cases are currently buildable;
- seed text for upstream CURSED issues;
- a single source of truth for "is X possible in CURSED today?" so future
  sessions don't have to re-derive the answer.

Scope is intentionally local to brat. We are *not* trying to inventory all
of CURSED — only the primitives any of brat's 18 test cases would need.

## Artifact

A new file: `docs/cursed-gaps.md`, structured as one section per missing
primitive, plus a mapping table.

### Per-gap entry shape

```
## <gap-name>

**Need:** what brat needs this for, in one sentence.
**Status:** missing | partial | broken.
**Evidence:** runtime-C citation, subset-doc quote, or probe output
(verbatim, fenced).
**Brat cases blocked:** list of `tests/cases/<name>` dirs.
**Upstream framing:** one-line issue title + the minimal surface that
would unblock brat.
```

`Status` values:

- `missing` — no implementation at all (e.g. no stderr write in
  `cursed_runtime.c`).
- `partial` — present in some form but doesn't cover the brat use case
  (e.g. `vibez.spill` exists but only writes stdout).
- `broken` — accepted by parser but produces wrong behavior or unhelpful
  diagnostic (e.g. `ready` in current subset emits
  `error.MissingMainCharacter` instead of an "unsupported construct"
  diagnostic).

### Mapping table

A `## Cases ↔ Gaps` table at the bottom listing every `tests/cases/<name>`
directory with the gap(s) it depends on, or `implementable today` if
none.

## Process

The audit happens in this order. Each step's output feeds the next.

### 1. Seed (paper evidence)

Pre-populate `docs/cursed-gaps.md` with gaps already evidenced from the
brainstorming session, citing `cursed_runtime.c` and
`test_suite/compiler_subset/test_compiler_subset.sh`:

- stderr write — runtime defines only `spill_*` to stdout via `printf`.
- exit-code control — no `exit()` or equivalent in runtime.
- file read — no file primitives in runtime.
- `mathz` / non-`vibez`/`stringz` imports — integration script asserts
  rejection.
- user-defined functions — integration script asserts rejection.
- member access — integration script asserts rejection.
- array literals / indexing — integration script asserts rejection.

These get `Status: missing` and `Evidence:` lines pointing at the file
and line range.

### 2. Probe (parser/validator-layer gaps)

For language-layer gaps where the parser or validator decides — and where
the failure mode itself is interesting — write a minimal `.💀` probe in
`/tmp/`, run it through `~/cursed/zig-out/bin/cursed-compiler --compile`,
and paste the verbatim diagnostic into the gap's `Evidence:` block.

Probes are ephemeral. Do not commit them.

Known probes needed at start of step:

- conditionals (`ready x > 0 { ... }`) — already probed once during
  brainstorming; redo cleanly so the captured output matches the
  committed doc.
- argv access — there is no documented surface for this; try a plausible
  shape (e.g. `vibez.spill(args.argv)` or similar) and capture the error,
  whatever it is. If the diagnostic is itself unhelpful, that's
  worth flagging in `Upstream framing`.

Additional probes get added in step 3 if a test-case audit turns up a
candidate primitive whose status isn't already pinned by the runtime C
file.

### 3. Audit (walk all 18 cases)

For each directory in `tests/cases/`:

1. Read `args`, `expected.out`, `expected.err`, `expected.exit`,
   `inputs/`, and (if present) `modes`.
2. Enumerate the primitives an implementation would need. Examples:
   - any case with `expected.exit` ≠ 0 → exit-code control
   - any non-empty `expected.err` → stderr write
   - any case with files in `inputs/` whose contents appear in
     `expected.out` → file read
   - any case with `args` distinguishing behavior (e.g. zero vs one
     filename) → conditionals + argv access
   - cases using `modes` for chmod-based denial → file open errors,
     errno surfacing
3. For each primitive identified: if not already in the gaps doc, add a
   new section (and probe it per step 2 if it's parser/validator-layer);
   then append `tests/cases/<name>` to that gap's `Brat cases blocked:`
   list.
4. Add a row to the `Cases ↔ Gaps` table.

Cases where every needed primitive is already implemented get
`implementable today` in the mapping table.

### 4. Learnings entry

Write one entry in `docs/learnings.md` summarising the audit. Should
include:

- the count: N cases / M gaps.
- the standout finding (e.g. "every error case is blocked on the same
  three primitives").
- a pointer to `docs/cursed-gaps.md` as the canonical doc.

Match the existing entry style in the doc (entry template, tags, brevity,
trope discipline). Tags likely: `#cursed` `#contributing`.

Do not write 18 entries. The doc explicitly warns against this kind of
per-item logging — one summary entry that points at the gaps doc is the
right granularity.

### 5. Commits

Two commits, in order:

1. `docs(gaps): seed cursed-gaps roadmap` — adds `docs/cursed-gaps.md`.
2. `docs(learnings): cursed-gaps audit summary` — adds the learnings
   entry.

## Validation

Two invariants must hold when the audit is done. Self-check inline; no
automation.

1. Every gap section has at least one citation in `Evidence:` — either a
   file/line reference or fenced probe output.
2. Every directory in `tests/cases/` appears as a row in the
   `Cases ↔ Gaps` table, with at least one gap or `implementable today`.

## Out of Scope

- Filing the upstream issues themselves. The `Upstream framing` lines are
  seed text for issues, not the act of opening them. Filing is a separate
  follow-up.
- Inventorying CURSED capabilities not relevant to brat.
- Building any of the missing primitives upstream. This audit only
  identifies gaps; closing them is a separate project.
- Implementing any brat test case. This audit precedes implementation.

## Risks and Mitigations

- **Probe diagnostics change between CURSED versions.** Mitigation: the
  doc captures the diagnostic as of today and cites the date in the
  learnings entry. Future drift is acceptable; the doc is a snapshot, not
  a live contract.
- **Audit is biased toward primitives we already know about.** Mitigation:
  step 3 enumerates from the test cases outward, not from the
  already-known gaps. New gaps surface as new sections.
- **The empirical/paper split is a judgment call per gap.** Mitigation:
  default to paper when `cursed_runtime.c` is dispositive (no symbol →
  conclusively missing); probe when the parser or validator could
  surprise us.
