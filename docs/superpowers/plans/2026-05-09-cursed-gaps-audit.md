# CURSED Gaps Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce `docs/cursed-gaps.md` — a per-primitive roadmap of what CURSED is missing for brat to be implementable, with each gap evidenced from runtime C, the subset doc, the language specs, and (where useful) committed `.💀` probes.

**Architecture:** A research/documentation task, not a code task. The artifact is one markdown file plus a small set of committed probes. Work proceeds in the order the spec lays out: scaffold the doc, seed paper-evidence gaps, write probes for parser/validator-layer gaps, walk all 18 brat test cases to enumerate needed primitives and fill the mapping table, then write a single learnings summary. Validation is two invariants self-checked at the end.

**Tech Stack:** Markdown for the doc; `.💀` source files compiled via `~/cursed/zig-out/bin/cursed-compiler --compile` for probes; `~/cursed/specs/` and `~/cursed/cursed_runtime.c` and `~/cursed/test_suite/compiler_subset/` as evidence sources.

**Source spec:** `docs/superpowers/specs/2026-05-09-cursed-gaps-audit-design.md` — re-read it; this plan executes it.

---

## Pre-flight

- [ ] **Step 0: Re-read the spec end-to-end.**

Run: `cat docs/superpowers/specs/2026-05-09-cursed-gaps-audit-design.md`

Expected: full spec including the per-gap entry shape (Need, Status, Design status, Evidence, Brat cases blocked, Upstream framing), the three-bucket framing (in subset / spec'd-but-unimplemented / undesigned), and the experiments/probes/ commit policy.

- [ ] **Step 1: Verify evidence sources are reachable.**

Run:
```bash
ls ~/cursed/cursed_runtime.c \
   ~/cursed/specs/current_llvm_subset.md \
   ~/cursed/specs/error_handling.md \
   ~/cursed/specs/grammar.md \
   ~/cursed/specs/types.md \
   ~/cursed/test_suite/compiler_subset/test_compiler_subset.sh \
   ~/cursed/zig-out/bin/cursed-compiler
```

Expected: all paths exist. If `cursed-compiler` is missing, run `cd ~/cursed && make build` first.

---

## Task 1: Scaffold the gaps doc

**Files:**
- Create: `docs/cursed-gaps.md`

- [ ] **Step 1: Write the scaffold.**

Create `docs/cursed-gaps.md` with this exact content:

```markdown
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

## Cases ↔ Gaps

| Case | Gaps blocking |
|------|---------------|

<!-- one row per directory in tests/cases/ -->
```

- [ ] **Step 2: Verify the file exists with the expected headings.**

Run: `grep -E "^#{1,3} " docs/cursed-gaps.md`

Expected:
```
# CURSED Gaps for brat
## Gap entry conventions
## Gaps
## Cases ↔ Gaps
```

---

## Task 2: Seed paper-evidence gaps

These seven gaps are dispositively settled by `~/cursed/cursed_runtime.c` and `~/cursed/test_suite/compiler_subset/test_compiler_subset.sh`. No probing needed — write each section with citations.

**Files:**
- Modify: `docs/cursed-gaps.md` (append seven `### <gap-name>` sections under `## Gaps`)

For each step below: open the cited file, read the relevant lines, and write the gap section using the conventions above. Do NOT invent line numbers; verify them by reading the file.

- [ ] **Step 1: Seed `stderr-write`.**

Read `~/cursed/cursed_runtime.c` and grep for `printf`, `fprintf`, `stderr`. Confirm only stdout is written via `printf`-family calls in `spill_*`. Also grep `~/cursed/specs/stdlib/` for any documented stderr surface.

Append to `docs/cursed-gaps.md` under `## Gaps`:

```markdown
### stderr-write

**Need:** brat writes its `cat:` error messages to stderr.
**Status:** missing.
**Design status:** <spec'd with citation OR undesigned — fill in from your read>.
**Evidence:** `~/cursed/cursed_runtime.c:<lines>` — only `spill_*` exists, all writing to stdout via `printf`. No `fprintf(stderr, ...)` anywhere in the runtime.
**Brat cases blocked:** (filled in during Task 4)
**Upstream framing:** "runtime: add stderr write surface" — minimum: a `vibez.spill_err(s)` (or equivalent) that maps to `fprintf(stderr, ...)`.
```

- [ ] **Step 2: Seed `exit-code-control`.**

Read `~/cursed/cursed_runtime.c` and grep for `exit(`, `_exit`, `return` from main. Confirm no exit-code surface. Check `~/cursed/specs/error_handling.md` for designed surface.

Append a `### exit-code-control` section in the same shape.

- [ ] **Step 3: Seed `file-read`.**

Grep `~/cursed/cursed_runtime.c` for `fopen`, `read`, `open`, `fread`. Check `~/cursed/specs/stdlib/` for any documented file I/O module.

Append `### file-read`.

- [ ] **Step 4: Seed `non-stdlib-imports`.**

Read `~/cursed/test_suite/compiler_subset/unsupported_import.💀` and the relevant assertion in `test_compiler_subset.sh`. Note that `mathz` and other non-`vibez`/`stringz` imports are explicitly rejected.

Append `### non-stdlib-imports` citing both the fixture and the script.

- [ ] **Step 5: Seed `user-defined-functions`.**

Read `~/cursed/test_suite/compiler_subset/unsupported_user_call.💀` and its assertion. Cross-reference `~/cursed/specs/grammar.md` for the designed function-definition surface.

Append `### user-defined-functions`.

- [ ] **Step 6: Seed `member-access`.**

Read `~/cursed/test_suite/compiler_subset/unsupported_member_access.💀` and its assertion. Cross-reference `~/cursed/specs/types.md` and `grammar.md`.

Append `### member-access`.

- [ ] **Step 7: Seed `array-literals-and-indexing`.**

Read `~/cursed/test_suite/compiler_subset/unsupported_array_access.💀` and its assertion. Cross-reference `~/cursed/specs/types.md` for designed collection types.

Append `### array-literals-and-indexing`.

- [ ] **Step 8: Seed `raw-stdout-write`.**

This gap is not visible from the runtime alone — `vibez.spill` exists and writes to stdout, so a naive runtime grep would call this "implemented." It isn't, for brat's purposes: `vibez.spill` is line-oriented and always appends `\n`. brat needs byte-faithful stdout (an `io.write` equivalent) to print file contents verbatim — see `docs/superpowers/specs/2026-05-09-brat-design.md` lines 55–72 and 192–201, which mark this "non-negotiable" / "critical-path."

Append to `docs/cursed-gaps.md`:

```markdown
### raw-stdout-write

**Need:** brat must emit file bytes verbatim. `vibez.spill` always appends `\n`, so it can't print files that don't end in newline (would add one) or files that do (would double it), and it can't carry NUL bytes through cleanly.
**Status:** partial — `vibez.spill` covers line-terminated writes only.
**Design status:** undesigned — no `io.write` (or equivalent byte-faithful surface) is documented in `~/cursed/specs/stdlib/`. Verify by `grep -ri "io\.write\|raw\|bytes" ~/cursed/specs/stdlib/` and cite either the absence or the closest documented surface.
**Evidence:** `~/cursed/cursed_runtime.c:<lines>` — only `spill_*` exists, all calling `printf("%s\n", ...)` or equivalent. brat design spec marks this gap explicitly: `docs/superpowers/specs/2026-05-09-brat-design.md:55-72,192-201`.
**Brat cases blocked:** (filled in during Task 4 — expected to block every case that prints any file content)
**Upstream framing:** "runtime+stdlib: add byte-faithful stdout primitive" — minimum: `io.write(s tea)` that emits exactly the bytes given, no implicit newline, NUL-safe.
```

- [ ] **Step 9: Verify all eight sections exist.**

Run: `grep -c "^### " docs/cursed-gaps.md`

Expected: `8`

Run: `grep -E "^### " docs/cursed-gaps.md`

Expected:
```
### stderr-write
### exit-code-control
### file-read
### non-stdlib-imports
### user-defined-functions
### member-access
### array-literals-and-indexing
### raw-stdout-write
```

- [ ] **Step 10: Verify every seeded gap has Status, Design status, and Evidence lines.**

Run: `awk '/^### /{name=$0; s=d=e=0} /\*\*Status:\*\*/{s=1} /\*\*Design status:\*\*/{d=1} /\*\*Evidence:\*\*/{e=1} /^### |^## /{if(name && (!s||!d||!e)) print "MISSING:", name, "s="s" d="d" e="e; if(/^### /){name=$0; s=d=e=0}}' docs/cursed-gaps.md`

Expected: no `MISSING:` output.

---

## Task 3: Set up `experiments/probes/` and write the two upfront probes

The spec calls for two probes upfront: `conditionals` (parser-layer) and `argv-access` (no documented surface — capture whatever the compiler says).

**Files:**
- Create: `experiments/probes/conditionals.💀`
- Create: `experiments/probes/argv-access.💀`
- Modify: `docs/cursed-gaps.md` (append two `### ` sections)

- [ ] **Step 1: Create the probes directory.**

Run: `mkdir -p experiments/probes`

Verify: `ls -d experiments/probes`

Expected: `experiments/probes`

- [ ] **Step 2: Write the conditionals probe.**

Base the probe on `~/cursed/test_suite/compiler_subset/supported_cli.💀` — it's the only known-good shape. Read it first:

```bash
cat ~/cursed/test_suite/compiler_subset/supported_cli.💀
```

Copy its scaffold verbatim (`vibe main` / `yeet "vibez"` / `yeet "stringz"` / `slay main_character()` / `sus <name> tea = ...`), then add **only** the construct under test (a `ready` conditional). This isolates the diagnostic to the conditional gap; using `let` or omitting the `vibe`/`yeet` headers would produce diagnostics for *those* unrelated gaps and pollute the evidence.

Consult `~/cursed/specs/grammar.md` for the designed `ready` syntax and copy it verbatim. Do NOT invent.

Example shape (replace the `ready ... { ... }` body to match what the grammar spec actually documents):

```
vibe main
yeet "vibez"
yeet "stringz"

slay main_character() {
    sus x tea = stringz.upper("hi")
    ready x == "HI" {
        vibez.spill(x)
    }
}
```

- [ ] **Step 3: Run the probe and capture the diagnostic.**

Run:
```bash
~/cursed/zig-out/bin/cursed-compiler --compile --output=/tmp/conditionals_probe experiments/probes/conditionals.💀
```

Capture the full stderr+stdout output verbatim. Expected: failure (the subset doc says no conditionals).

- [ ] **Step 4: Append the `### conditionals` gap section.**

Append to `docs/cursed-gaps.md` under `## Gaps`:

```markdown
### conditionals

**Need:** brat branches on argv length (zero args → stdin; otherwise iterate files) and on per-file open errors.
**Status:** broken (parses but rejected at validation; cite the diagnostic).
**Design status:** spec'd — `~/cursed/specs/grammar.md` <section>.
**Evidence:** see `experiments/probes/conditionals.💀`. Diagnostic from `cursed-compiler --compile`:

```
<paste the verbatim output from Step 3>
```

**Brat cases blocked:** (filled in during Task 4)
**Upstream framing:** "compiler: lower already-spec'd `ready` conditional to LLVM IR" — minimum: a single `ready <expr> { ... }` form, no `else` branch required for brat's blocking cases.
```

- [ ] **Step 5: Write the argv-access probe.**

Create `experiments/probes/argv-access.💀`. There is no documented surface — try a plausible shape and capture whatever the compiler says. **Important:** avoid syntax that exercises *other* known-rejected primitives (member access via `.`, indexing via `[]`, user-defined functions). Otherwise the diagnostic will fire on those gaps instead of argv, polluting the evidence.

Use the same `vibe main` / `yeet` / `slay main_character()` / `sus` scaffold as the conditionals probe. Probe argv as a bare identifier (the closest plausible surface that doesn't invoke `.` or `[]`):

```
vibe main
yeet "vibez"

slay main_character() {
    sus first tea = argv
    vibez.spill(first)
}
```

If even reading `argv` as a bare name is rejected with a generic "unknown identifier" message, that itself *is* the evidence: no documented surface exists. Capture it as such.

Do NOT use `args.argv[0]`, `args[0]`, or any `.`/`[]` access — those would conflate this probe with the already-seeded `member-access` and `array-literals-and-indexing` gaps.

- [ ] **Step 6: Run the argv probe and capture the diagnostic.**

Run:
```bash
~/cursed/zig-out/bin/cursed-compiler --compile --output=/tmp/argv_probe experiments/probes/argv-access.💀
```

Capture verbatim output.

- [ ] **Step 7: Append the `### argv-access` gap section.**

Append to `docs/cursed-gaps.md`:

```markdown
### argv-access

**Need:** brat reads filenames from argv to decide which files to print.
**Status:** missing.
**Design status:** undesigned — no documented surface in `~/cursed/specs/`. Probed against a plausible shape.
**Evidence:** see `experiments/probes/argv-access.💀`. Diagnostic from `cursed-compiler --compile`:

```
<paste verbatim output from Step 6>
```

If the diagnostic itself is unhelpful (e.g. a generic parse error rather than a "no argv surface" message), note that in Upstream framing.

**Brat cases blocked:** (filled in during Task 4)
**Upstream framing:** "language: design and implement argv access surface" — minimum: a way to read argv as an iterable or indexable sequence of strings inside `main_character()`.
```

- [ ] **Step 8: Verify both probes are committable and gap sections exist.**

Run:
```bash
ls experiments/probes/
grep -E "^### (conditionals|argv-access)" docs/cursed-gaps.md
```

Expected:
```
argv-access.💀
conditionals.💀
### conditionals
### argv-access
```

---

## Task 4: Audit all 18 brat test cases

For each case in `tests/cases/`: read `args`, `expected.out`, `expected.err`, `expected.exit`, `inputs/`, and (if present) `modes`. Enumerate the primitives the case needs. For each primitive: if it's not yet a gap section, add one (and probe it if it's parser/validator-layer); then append `tests/cases/<name>` to that gap's `Brat cases blocked:` line. Add a row to the `Cases ↔ Gaps` table.

The 18 cases (verified by `ls tests/cases/`):

```
binary-nul, boundary-46, dash-filename, directory, empty,
good-missing-good, long-name, missing, multi-file, multi-missing,
multiline-with-eol, no-args, one-line-no-eol, permission-denied,
spaced-filename, subdir-path, unicode, uppercase-name
```

**Files:**
- Modify: `docs/cursed-gaps.md` (append rows to `## Cases ↔ Gaps`; update existing gaps' `Brat cases blocked:` lines; possibly add new `### ` gap sections; possibly add new probes under `experiments/probes/`)

The audit per case is mechanical. Use this checklist as a reusable map from case features to primitives:

- `expected.exit` ≠ 0 → `exit-code-control`
- non-empty `expected.err` → `stderr-write`
- files in `inputs/` whose contents appear in `expected.out` → `file-read` **and** `raw-stdout-write` (every successful print of file content needs byte-faithful stdout — see Task 2 Step 8).
- `args` distinguishing behavior (zero vs one filename, single vs multi) → `conditionals` + `argv-access`
- `modes` field (chmod-based denial) → `file-read` plus a new gap if needed for errno surfacing
- `directory` case → opening a directory as a file (likely a new gap: errno propagation)
- `binary-nul`, `unicode` cases → byte-faithful read+write — these are the canary cases for `raw-stdout-write`; `vibez.spill` would corrupt them (NUL truncation, trailing-newline drift).
- `permission-denied` case → file-open errno surfacing (likely a new gap)
- `multi-file`, `multi-missing`, `good-missing-good` → loops/iteration over argv (new gap if `loops` is not yet covered)
- `no-args` → brat's design rejects no-args with `bestie you have to give me a file` and exit 1 (NOT a stdin path; brat has no stdin support — verify by reading `tests/cases/no-args/expected.err` and `expected.exit`). Primitives needed: argv-length branching (`conditionals` + `argv-access`), `stderr-write`, `exit-code-control`. Do NOT add a `stdin-read` gap.
- `boundary-46` → whatever brat's design says about the 46-character/line boundary in the lime block header (re-read `tests/cases/boundary-46/` and `docs/superpowers/specs/2026-05-09-brat-design.md`).
- **Header-geometry primitives (apply to every successful-print case, not just `boundary-46`):** the lime block header (see brat design spec line 63 and `tests/test_header.py`) needs arithmetic on string lengths, integer comparisons, padding via repeated spaces (string repeat or a loop), and lowercasing the filename. Audit each of these against the subset:
  - integer arithmetic (`+`, `-`) → check `~/cursed/specs/current_llvm_subset.md` and probe if unclear; add a gap if missing.
  - integer comparison (`<`, `==`) — same.
  - string-length → same.
  - string repeat / padding loop → same. (Loops are likely already a separate gap; if not, add one.)
  - lowercasing — `stringz.upper` exists in the supported set; check whether `stringz.lower` (or equivalent) does. Add a gap if missing.

**Decision rule for new gaps surfaced during audit:**
- If runtime-C / subset-doc settles it → add a paper-evidence section like Task 2.
- If parser/validator decides → write a probe under `experiments/probes/<name>.💀`, capture diagnostic, cite it (Task 3 shape).

- [ ] **Step 1: Audit `binary-nul`.**

Read `tests/cases/binary-nul/{args,expected.*,inputs/}`. Enumerate primitives. Update gaps' `Brat cases blocked:` lines. Append `tests/cases/binary-nul` to each blocking gap. Add a row to the table.

If a new primitive is needed (e.g. raw-bytes write), add the new `### ` section per the decision rule.

- [ ] **Step 2: Audit `boundary-46`.**

Same procedure.

- [ ] **Step 3: Audit `dash-filename`.**

Same procedure. (`-` as a filename is conventionally stdin in `cat`; check whether brat's contract honors that.)

- [ ] **Step 4: Audit `directory`.**

Same procedure.

- [ ] **Step 5: Audit `empty`.**

Same procedure.

- [ ] **Step 6: Audit `good-missing-good`.**

Same procedure.

- [ ] **Step 7: Audit `long-name`.**

Same procedure.

- [ ] **Step 8: Audit `missing`.**

Same procedure.

- [ ] **Step 9: Audit `multi-file`.**

Same procedure.

- [ ] **Step 10: Audit `multi-missing`.**

Same procedure.

- [ ] **Step 11: Audit `multiline-with-eol`.**

Same procedure.

- [ ] **Step 12: Audit `no-args`.**

Same procedure. (Stdin path. Check whether brat's contract reads stdin in this case — if so, `stdin-read` may be a new gap distinct from `file-read`.)

- [ ] **Step 13: Audit `one-line-no-eol`.**

Same procedure.

- [ ] **Step 14: Audit `permission-denied`.**

Same procedure.

- [ ] **Step 15: Audit `spaced-filename`.**

Same procedure.

- [ ] **Step 16: Audit `subdir-path`.**

Same procedure.

- [ ] **Step 17: Audit `unicode`.**

Same procedure.

- [ ] **Step 18: Audit `uppercase-name`.**

Same procedure.

- [ ] **Step 19: Verify the mapping table has 18 rows.**

Run: `awk '/^## Cases ↔ Gaps/,0' docs/cursed-gaps.md | grep -c "^| tests/cases/"`

Expected: `18`

- [ ] **Step 20: Verify every brat case is represented.**

Run:
```bash
diff <(ls tests/cases/ | sort) \
     <(awk '/^## Cases ↔ Gaps/,0' docs/cursed-gaps.md | grep -oE "tests/cases/[a-z0-9-]+" | sed 's|tests/cases/||' | sort -u)
```

Expected: empty diff.

---

## Task 5: Validate the doc against the spec's two invariants

**Files:** none modified — read-only verification.

- [ ] **Step 1: Invariant 1 — every gap has Evidence + Design status.**

Run:
```bash
awk '
/^### / { name=$0; s=d=e=0; next }
/^## / { if (name && (!s||!d||!e)) print "MISSING:", name; name="" }
/\*\*Status:\*\*/ { s=1 }
/\*\*Design status:\*\*/ { d=1 }
/\*\*Evidence:\*\*/ { e=1 }
END { if (name && (!s||!d||!e)) print "MISSING:", name }
' docs/cursed-gaps.md
```

Expected: no `MISSING:` output. If any gap fails, fix it before proceeding.

- [ ] **Step 2: Invariant 2 — every `tests/cases/` dir is in the table.**

Already verified in Task 4 Step 20. Re-run if the doc changed.

- [ ] **Step 3: Sanity-check the `Brat cases blocked:` lines are populated.**

Run:
```bash
awk '/^### / {name=$0} /\*\*Brat cases blocked:\*\*/ {print name, "->", $0}' docs/cursed-gaps.md
```

Expected: every gap section listed, each with at least one `tests/cases/...` reference (unless a gap genuinely blocks zero cases — which would be suspicious; investigate).

---

## Task 6: Write the learnings entry

**Files:**
- Modify: `docs/learnings.md` (append one new entry at the top of `## Entries`)

- [ ] **Step 1: Re-read the trope discipline rules.**

Run: `cat ~/tropes/tropes.md | head -100`

Then re-read `docs/learnings.md` lines 1–86 (the "When to update" / "Rules for entries" / "Keep it small" sections).

- [ ] **Step 2: Draft the entry.**

Aim: one entry summarising the audit. Must include:

- The count: N cases / M gaps.
- The standout finding (e.g. "every error case blocks on the same three primitives" — derive this from the actual `Cases ↔ Gaps` table).
- A pointer to `docs/cursed-gaps.md`.

Tags: `#cursed` `#contributing`.

Length: a single entry following the template in `docs/learnings.md` lines 56–61. Do NOT write 18 entries. Do NOT inflate the observation.

Example shape (do not copy verbatim — derive from your actual numbers):

```markdown
### 2026-05-09 — cursed-gaps audit  `#cursed` `#contributing`

**What happened:** Walked all 18 brat test cases and mapped each to
the CURSED primitives an implementation would need. Wrote them up in
`docs/cursed-gaps.md`. <N> distinct gaps surfaced; <M> cases are
blocked by <K> shared primitives.

**Why it's interesting:** <one concrete standout from the table —
e.g. clustering, or the spec'd-vs-undesigned split>.

**Quote-worthy bit:** (skip if nothing fits)
```

- [ ] **Step 3: Insert the entry at the top of `## Entries`.**

Use Edit on `docs/learnings.md`. Find the `## Entries` line, then the next `### ` heading, and insert the new entry between them.

- [ ] **Step 4: Verify the entry is present and properly tagged.**

Run: `grep -A1 "^### 2026-05-09 — cursed-gaps audit" docs/learnings.md`

Expected: the entry heading line followed by a blank line.

Run: `grep "^### 2026-05-09 — cursed-gaps audit" docs/learnings.md | grep -E "#cursed.*#contributing|#contributing.*#cursed"`

Expected: matches.

---

## Task 7: Commit in two pieces

The spec calls for two commits, in order.

- [ ] **Step 1: Stage and commit the gaps doc + probes.**

Run:
```bash
git add docs/cursed-gaps.md experiments/probes/
git status
```

Expected: only `docs/cursed-gaps.md` and the two `experiments/probes/*.💀` files staged (plus any additional probes added during Task 4).

Run:
```bash
git commit -m "docs(gaps): seed cursed-gaps roadmap"
```

Expected: commit succeeds.

- [ ] **Step 2: Stage and commit the learnings entry.**

Run:
```bash
git add docs/learnings.md
git status
```

Expected: only `docs/learnings.md` staged.

Run:
```bash
git commit -m "docs(learnings): cursed-gaps audit summary"
```

Expected: commit succeeds.

- [ ] **Step 3: Verify the two-commit sequence.**

Run: `git log --oneline -3`

Expected: top two commits are the two above, in order (learnings on top, gaps below).
