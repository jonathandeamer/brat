# Agent and Tooling Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the setup changes from `docs/superpowers/specs/2026-05-10-agent-setup-design.md` so that compiler/runtime TDD on cursed and cross-repo doc sync stop relying on agent memory.

**Architecture:** Five workstreams across two repos (`~/brat`, `~/cursed`) and the user-level Claude config (`~/.claude/`). Each workstream lands as a small set of focused commits. Skills are authored as user-level skills under `~/.claude/skills/`; their checklists are mirrored in CLAUDE.md so Codex (which has no Skill tool) follows the same protocol.

**Tech Stack:** Bash, Python (pytest harness), Zig 0.15.x (toolchain), `cursed-compiler` (in `~/.local/bin`), git, `cz` (commitizen), Claude Code skills/settings.

**Conventions for every commit in this plan:**
- Conventional commits enforced by `commit-msg` (`cz check`).
- Trailer: `Co-authored-by: Claude <noreply@anthropic.com>` (or `Codex <codex@openai.com>` if executed by Codex).
- Never push to `upstream` in `~/cursed`. Never force-push `zig`.
- The brat `post-commit` hook auto-pushes `master`; the cursed hook auto-pushes only `origin/*`. This is expected behavior, not a bug.
- All plan work in cursed lives on a single topic branch — see Task 0.

---

## File Structure

Files created or modified by this plan:

**`~/cursed/`:**
- `docs/superpowers/specs/README.md` — new (workstream W5)
- `docs/superpowers/plans/README.md` — new (W5)
- `CLAUDE.md` — modified: spec-locations sentence (W5), Codex parity paragraph (W1.1), upstream-sync ritual now points at script (W1.2), `## Compiler/Runtime Fix Protocol` section (W3.1), `## Cross-Repo Doc Sync` section (W3.2), `make probes` doc (W4.1)
- `tropes.md` — new symlink to `~/tropes/tropes.md` (W1.3)
- `.gitignore` — modified: ignore `tropes.md` symlink (W1.3)
- `probes/conftest.py` — new (W4.1)
- `probes/test_probes.py` — new (W4.1)
- `probes/cases/hello-spill/{source.💀,args,expected.out,expected.err,expected.exit}` — new (W4.1)
- `probes/README.md` — new (W4.1)
- `Makefile` — modified: `probes` target (W4.1)
- `pyproject.toml` — modified: pytest config for probes (W4.1)
- `scripts/upstream-sync.sh` — new, executable (W1.2)
- `.claude/settings.json` — new (W2.1, W2.2)
- `.githooks/pre-push` — modified: append non-blocking `verify_cursed_gaps.sh` check (W4.2)

**`~/brat/`:**
- `CLAUDE.md` — modified: Codex parity paragraph (W1.1), cross-repo-sync paragraph (W3.2)
- `tropes.md` — new symlink to `~/tropes/tropes.md` (W1.3)
- `.gitignore` — modified: ignore `tropes.md` symlink (W1.3)
- `.claude/settings.json` — new (W2.1)

**`~/.claude/skills/`:**
- `cursed-tdd/SKILL.md` — new (W3.1)
- `cross-repo-sync/SKILL.md` — new (W3.2)

---

## Task 0: Sanity check the environment + branch setup

**Files:** none

- [ ] **Step 1: Verify both repos clean**

```bash
cd ~/brat && git status
cd ~/cursed && git status
```

Expected: both `nothing to commit, working tree clean`. If either is dirty, stop and report.

- [ ] **Step 2: Verify toolchain present**

```bash
which cursed-compiler zig cz pytest
zig version
cursed-compiler --help 2>&1 | head -3
```

Expected: all four binaries resolve; `zig version` prints `0.15.x`; `cursed-compiler --help` does not error.

- [ ] **Step 3: Capture a baseline of the brat probe set**

```bash
bash ~/brat/experiments/verify_cursed_gaps.sh > /tmp/baseline-gaps.txt 2>&1
echo "exit=$?"
```

Capture the output. Task 18 (W4.2) compares against this baseline. Do NOT commit `/tmp/baseline-gaps.txt`.

- [ ] **Step 4: Create cursed topic branch for the W5 + W1 + W2 + W4 work**

```bash
cd ~/cursed
git fetch upstream
git switch zig
git merge --ff-only upstream/zig
git push origin zig
git switch -c agent-setup
```

Expected: clean fast-forward, no merge conflicts, branch `agent-setup` checked out.

If `git merge --ff-only` fails (upstream diverged in a non-fast-forward way), stop and ask the user how to proceed — do not force-merge.

- [ ] **Step 5: Brat work happens on `master`**

Brat is a personal project on `master` per its CLAUDE.md and recent history. No topic branch needed there. The post-commit hook auto-pushes; that is intentional.

---

## Task 1: cursed `docs/superpowers/` skeleton (W5.1)

**Files:**
- Create: `~/cursed/docs/superpowers/specs/README.md`
- Create: `~/cursed/docs/superpowers/plans/README.md`

- [ ] **Step 1: Create the directories and stub READMEs**

```bash
mkdir -p ~/cursed/docs/superpowers/specs ~/cursed/docs/superpowers/plans
```

Write `~/cursed/docs/superpowers/specs/README.md`:

```markdown
# Specs

Session brainstorms and design docs. Filenames are date-prefixed:
`YYYY-MM-DD-<topic>-design.md`.

Do not put upstream CURSED language specs here — those live in
`~/cursed/specs/` (no date prefix).
```

Write `~/cursed/docs/superpowers/plans/README.md`:

```markdown
# Plans

Implementation plans derived from specs in `../specs/`. Filenames are
date-prefixed: `YYYY-MM-DD-<topic>.md`.
```

- [ ] **Step 2: Verify**

```bash
ls ~/cursed/docs/superpowers/specs ~/cursed/docs/superpowers/plans
```

Expected: each shows `README.md`.

- [ ] **Step 3: Commit**

```bash
cd ~/cursed
git add docs/superpowers/
git commit -m "$(cat <<'EOF'
docs: add docs/superpowers/{specs,plans} skeleton

Session brainstorms in cursed land here, separate from upstream
language specs in specs/.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

Expected: `commit-msg` passes, `post-commit` pushes branch `agent-setup` to `origin/agent-setup`.

---

## Task 2: cursed CLAUDE.md — spec-locations disambiguation (W5.2)

**Files:**
- Modify: `~/cursed/CLAUDE.md` — add new section after "## Working Style"

- [ ] **Step 1: Read the file to find the insertion point**

Open `~/cursed/CLAUDE.md`, locate the end of the `## Working Style` section (currently ends with the line about linking `cursed_runtime.c`).

- [ ] **Step 2: Insert new `## Spec Locations` section**

Insert after the Working Style section, before `## Fork And Contribution Hygiene`:

```markdown
## Spec Locations

`specs/` holds upstream CURSED language specifications — do not put
session work there. Session brainstorms and implementation plans go
under `docs/superpowers/specs/` and `docs/superpowers/plans/` with
date-prefixed filenames (`YYYY-MM-DD-<topic>.md`).
```

- [ ] **Step 3: Commit**

```bash
cd ~/cursed
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude): disambiguate spec locations

specs/ is upstream language specs; docs/superpowers/specs/ is for
session brainstorms.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Codex parity paragraph in cursed CLAUDE.md (W1.1)

**Files:**
- Modify: `~/cursed/CLAUDE.md` — extend "## Agent Attribution" section

- [ ] **Step 1: Append the parity paragraph**

In `~/cursed/CLAUDE.md`, find the existing `## Agent Attribution` section. Append a new paragraph at the end of that section:

```markdown
Claude has skills, slash commands, and `~/.claude` hooks; Codex does
not. When a Claude-only tool drove a non-trivial decision (a skill
checklist, a slash command, a hook-gated workflow), name the tool in
the commit body so Codex review can replay the reasoning. The point
is not parity for its own sake — it is to keep cross-agent review
honest when the two agents have different scaffolding.
```

- [ ] **Step 2: Commit**

```bash
cd ~/cursed
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude): note Claude/Codex tool asymmetry for cross-agent review

When a Claude-only tool shaped a decision, name it in the commit so
Codex review can replay the reasoning.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Codex parity paragraph in brat CLAUDE.md (W1.1)

**Files:**
- Modify: `~/brat/CLAUDE.md` — extend "## Workflow" section's `Attribute agent commits` bullet

- [ ] **Step 1: Append a sub-paragraph after the `Attribute agent commits` bullet**

In `~/brat/CLAUDE.md`, find the bullet starting `- **Attribute agent commits.**` (last bullet in `## Workflow`). After that bullet, add a new bullet:

```markdown
- **Name Claude-only tools when they drove a decision.** Claude has
  skills, slash commands, and `~/.claude` hooks; Codex does not. When
  a Claude-only tool drove a non-trivial decision in this repo, name
  the tool in the commit body so Codex review can replay the
  reasoning.
```

- [ ] **Step 2: Commit**

```bash
cd ~/brat
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude): note Claude/Codex tool asymmetry for cross-agent review

Symmetric instruction to ~/cursed: when a Claude-only tool shaped a
decision, surface it in the commit body.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

Expected: `post-commit` pushes `master` to `origin/master`.

---

## Task 5: Tropes file symlinks (W1.3)

**Files:**
- Create: `~/brat/tropes.md` (symlink → `~/tropes/tropes.md`)
- Create: `~/cursed/tropes.md` (symlink → `~/tropes/tropes.md`)
- Modify: `~/brat/.gitignore`
- Modify: `~/cursed/.gitignore`

- [ ] **Step 1: Confirm tropes file exists**

```bash
ls -l ~/tropes/tropes.md
```

Expected: regular file, non-empty.

- [ ] **Step 2: Add `tropes.md` to both `.gitignore` files**

In `~/brat/.gitignore`, append the line:

```
tropes.md
```

Same in `~/cursed/.gitignore`.

- [ ] **Step 3: Create the symlinks**

```bash
ln -s ~/tropes/tropes.md ~/brat/tropes.md
ln -s ~/tropes/tropes.md ~/cursed/tropes.md
```

- [ ] **Step 4: Verify**

```bash
ls -l ~/brat/tropes.md ~/cursed/tropes.md
head -1 ~/brat/tropes.md
head -1 ~/cursed/tropes.md
```

Expected: both `ls` outputs show `tropes.md -> /home/ec2-user/tropes/tropes.md`; both `head` calls print the same first line.

```bash
cd ~/brat && git status
cd ~/cursed && git status
```

Expected: both clean (the symlinks are gitignored).

- [ ] **Step 5: Commit `.gitignore` changes**

```bash
cd ~/brat
git add .gitignore
git commit -m "$(cat <<'EOF'
chore: ignore local tropes.md symlink

CLAUDE.md references ~/tropes/tropes.md. The symlink is per-checkout
convenience, not source.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"

cd ~/cursed
git add .gitignore
git commit -m "$(cat <<'EOF'
chore: ignore local tropes.md symlink

CLAUDE.md references ~/tropes/tropes.md. The symlink is per-checkout
convenience, not source.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Probe harness — `conftest.py` + first case (W4.1)

**Files:**
- Create: `~/cursed/probes/conftest.py`
- Create: `~/cursed/probes/test_probes.py`
- Create: `~/cursed/probes/cases/hello-spill/source.💀`
- Create: `~/cursed/probes/cases/hello-spill/args`
- Create: `~/cursed/probes/cases/hello-spill/expected.out`
- Create: `~/cursed/probes/cases/hello-spill/expected.err`
- Create: `~/cursed/probes/cases/hello-spill/expected.exit`
- Create: `~/cursed/probes/README.md`
- Modify: `~/cursed/pyproject.toml` (add pytest config)

- [ ] **Step 1: Pick a known-working CURSED program for the seed case**

Read `~/brat/docs/cursed-subset.md` and `~/brat/experiments/verify_cursed_gaps.sh`. Find the simplest reliably-working example: a single `vibez.spill` of a string literal that prints to stdout and exits 0. Adapt it to the seed case below. If the source-of-truth doc disagrees with what you would have written, trust the doc.

- [ ] **Step 2: Write the failing harness**

Create `~/cursed/probes/conftest.py`:

```python
"""Probe harness for cursed-compiler native-compile behavior.

Each subdirectory of probes/cases/ is one probe. The harness compiles
source.💀 with `cursed-compiler --compile`, runs the produced binary,
and asserts stdout, stderr, and exit code against the expected.* files.
"""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path

import pytest

CASES_DIR = Path(__file__).parent / "cases"
COMPILER = os.environ.get("CURSED_COMPILER", "cursed-compiler")


@dataclass
class Case:
    name: str
    source: Path
    args: list[str]
    expected_out: bytes
    expected_err: bytes
    expected_exit: int


def _read_args(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text().strip()
    return shlex.split(text) if text else []


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes() if path.exists() else b""


def _read_exit(path: Path) -> int:
    return int(path.read_text().strip()) if path.exists() else 0


def discover_cases() -> list[Case]:
    cases: list[Case] = []
    if not CASES_DIR.is_dir():
        return cases
    for case_dir in sorted(p for p in CASES_DIR.iterdir() if p.is_dir()):
        source_candidates = list(case_dir.glob("source.*"))
        if not source_candidates:
            continue
        cases.append(
            Case(
                name=case_dir.name,
                source=source_candidates[0],
                args=_read_args(case_dir / "args"),
                expected_out=_read_bytes(case_dir / "expected.out"),
                expected_err=_read_bytes(case_dir / "expected.err"),
                expected_exit=_read_exit(case_dir / "expected.exit"),
            )
        )
    return cases


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "case" in metafunc.fixturenames:
        cases = discover_cases()
        metafunc.parametrize("case", cases, ids=[c.name for c in cases])
```

Create `~/cursed/probes/test_probes.py`:

```python
"""One parametrized test per probe under probes/cases/."""

from __future__ import annotations

import subprocess
from pathlib import Path

from conftest import COMPILER, Case


def test_probe(case: Case, tmp_path: Path) -> None:
    binary = tmp_path / case.name
    compile_proc = subprocess.run(
        [COMPILER, "--compile", f"--output={binary}", str(case.source)],
        capture_output=True,
    )
    assert compile_proc.returncode == 0, (
        f"compile failed: stdout={compile_proc.stdout!r} "
        f"stderr={compile_proc.stderr!r}"
    )

    run_proc = subprocess.run(
        [str(binary), *case.args],
        capture_output=True,
    )

    assert run_proc.stdout == case.expected_out, (
        f"stdout mismatch: got {run_proc.stdout!r} "
        f"expected {case.expected_out!r}"
    )
    assert run_proc.stderr == case.expected_err, (
        f"stderr mismatch: got {run_proc.stderr!r} "
        f"expected {case.expected_err!r}"
    )
    assert run_proc.returncode == case.expected_exit, (
        f"exit mismatch: got {run_proc.returncode} "
        f"expected {case.expected_exit}"
    )
```

- [ ] **Step 3: Run the harness before adding cases — confirm zero collected**

```bash
cd ~/cursed
pytest probes/ -v
```

Expected: `no tests ran` (zero cases discovered). This proves the harness *runs* before any case exists.

- [ ] **Step 4: Add the seed case `hello-spill`**

Use the verified working syntax from Step 1 — the example shape below is illustrative and may need adjustment.

```bash
mkdir -p ~/cursed/probes/cases/hello-spill
```

Write `~/cursed/probes/cases/hello-spill/source.💀` (use the verified working syntax — example shape):

```
vibe main_character() {
    vibez.spill "hello"
}
```

Write `~/cursed/probes/cases/hello-spill/args` (empty file is fine — no args).

Write `~/cursed/probes/cases/hello-spill/expected.out`:

```
hello
```

Write `~/cursed/probes/cases/hello-spill/expected.err`: (empty file).

Write `~/cursed/probes/cases/hello-spill/expected.exit`:

```
0
```

Note: the trailing newline in `expected.out` is significant — the cursed runtime currently injects `\n` after every `vibez.spill`. If you find this is *not* what the runtime does, fix the expected file rather than the runtime; this probe is documenting current behavior.

- [ ] **Step 5: Run the probe**

```bash
cd ~/cursed
pytest probes/ -v
```

Expected: `1 passed`. If it fails, the failure tells you what the runtime actually emits — adjust `expected.out` / `expected.exit` to match observed behavior. Goal here is "harness works and documents reality", not "runtime matches an aspiration".

- [ ] **Step 6: Configure pytest to find the probes**

Modify `~/cursed/pyproject.toml`. Current contents:

```toml
[tool.commitizen]
name = "cz_conventional_commits"
```

Append:

```toml
[tool.pytest.ini_options]
testpaths = ["probes"]
```

Verify:

```bash
cd ~/cursed
pytest -v
```

Expected: same `1 passed` from Step 5 (now invocable as bare `pytest`).

- [ ] **Step 7: Add probes README**

Create `~/cursed/probes/README.md`:

```markdown
# Probes

Compile-and-run tests for cursed-compiler native-compile behavior.

## Layout

Each subdirectory of `cases/` is one probe:

- `source.💀` — input program
- `args` — shell-quoted args for the produced binary (optional)
- `expected.out` — exact stdout bytes (optional, default empty)
- `expected.err` — exact stderr bytes (optional, default empty)
- `expected.exit` — exit code (optional, default 0)

## Running

    pytest probes/        # all cases
    pytest probes/ -k <name>  # single case
    make probes           # same as `pytest probes/`

## Adding a case

Add a directory under `cases/` with the files above. The harness picks
it up automatically — no test code changes needed. Probes document
*current* runtime behavior. If a probe fails because the runtime now
emits different bytes, decide whether the change was intentional and
update the expected files OR fix the runtime.
```

- [ ] **Step 8: Commit**

```bash
cd ~/cursed
git add probes/ pyproject.toml
git commit -m "$(cat <<'EOF'
test(probes): add cursed-compiler probe harness

Compiles each case under probes/cases/, runs the produced binary, and
asserts exact stdout/stderr bytes and exit code. Mirrors brat's
golden-walker shape so adding a case requires no test code changes.
Seeded with hello-spill.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: `make probes` Makefile target (W4.1)

**Files:**
- Modify: `~/cursed/Makefile` — add `probes` target

- [ ] **Step 1: Read existing Makefile to find a good insertion point**

```bash
grep -n '^[a-z].*:' ~/cursed/Makefile | head -20
```

Identify where existing targets like `test`, `build` are defined.

- [ ] **Step 2: Add the `probes` target**

Add to `~/cursed/Makefile`, after the existing `test` target:

```make
.PHONY: probes
probes:
	pytest probes/
```

If a `.PHONY` block exists at top of file, also append `probes` there.

- [ ] **Step 3: Verify**

```bash
cd ~/cursed
make probes
```

Expected: `1 passed` (the seed case from Task 6).

- [ ] **Step 4: Document `make probes` in cursed CLAUDE.md**

In `~/cursed/CLAUDE.md`, find the `## Build And Test` section. Add a paragraph after the existing test discussion:

```markdown
For language-behavior changes, run the probe harness:

    make probes        # pytest probes/

Each subdirectory under `probes/cases/` is one probe; add a directory
to add a case (no test code changes needed). See `probes/README.md`.
```

- [ ] **Step 5: Commit**

```bash
cd ~/cursed
git add Makefile CLAUDE.md
git commit -m "$(cat <<'EOF'
build: make probes target wired to probe harness

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: `cursed-tdd` skill (W3.1, part 1 of 2)

**Files:**
- Create: `~/.claude/skills/cursed-tdd/SKILL.md`

- [ ] **Step 1: Create skills directory if missing**

```bash
mkdir -p ~/.claude/skills/cursed-tdd
```

- [ ] **Step 2: Author the skill**

Create `~/.claude/skills/cursed-tdd/SKILL.md`:

```markdown
---
name: cursed-tdd
description: Use when fixing or extending CURSED compiler/runtime behavior in ~/cursed. Enforces minimal-reproducer-first TDD with bytes-and-exit verification, and re-runs the brat downstream probe set before claiming a fix is done.
---

# CURSED Compiler/Runtime TDD

Use this checklist for any change to compiler or runtime behavior in
`~/cursed`. The discipline is load-bearing because CURSED's compiler
errors are sparse and misleading — observed bytes and exit codes are
your only honest signal.

## Checklist

1. **Minimal failing reproducer in `/tmp`.**
   Write the smallest `.💀` program that exhibits the bug. Compile and
   run it; confirm it fails for the right reason (the actual symptom,
   not a parse error elsewhere). If the reproducer "fails" because of
   a different bug, narrow further before continuing.

2. **Bytes-and-exit verification.**
   Capture all four signals explicitly:
   - stdout: pipe to `xxd -p` to see exact bytes
   - stderr: capture separately (do not merge with stdout)
   - exit code: `echo $?` immediately after run
   - emitted IR: `cursed-compiler --emit-ir --output=/tmp/x.ll <src>` —
     read the IR when codegen is suspected

   Source reads of `src-zig/cursed_runtime.c` are not enough. The
   compiler can inject calls (e.g. `\n`-spill after `vibez.spill`)
   that grep won't show.

3. **Promote the reproducer into `probes/cases/`.**
   When the fix is in, add a probe directory documenting current
   behavior so the harness catches future regressions.

4. **Run the brat downstream probe set.**
   `bash ~/brat/experiments/verify_cursed_gaps.sh`. New failures are
   blockers unless intentional and called out in the commit body.

5. **Cross-repo doc sync if a gap moved.**
   If this fix closes or surfaces a gap, run the `cross-repo-sync`
   skill (or follow the equivalent CLAUDE.md section) to update brat's
   tracking docs in a separate commit in `~/brat`.

## Active path reminders

- Build target: `src-zig/cursed_compiler_main.zig`
- Runtime: `src-zig/cursed_runtime.c`
- Ignore `advanced_*`, `*_fixed`, `*_complete`, `llvm_ir_pipeline_*`
  unless they are wired in `build.zig`.

## Commit shape

Per `~/cursed/CLAUDE.md`: split by intent — failing test/probe
commit, implementation commit, docs update commit. Tiny changes can
combine test and fix.
```

- [ ] **Step 3: Verify the skill file is in place**

```bash
ls ~/.claude/skills/cursed-tdd/SKILL.md
head -5 ~/.claude/skills/cursed-tdd/SKILL.md
```

Expected: file exists; head shows the frontmatter (`---`, `name:`, `description:`, `---`).

- [ ] **Step 4: No commit — skill files are user-level (outside any repo)**

Skills live in `~/.claude/skills/`, which is not a git repo. No commit. Move to Task 9.

---

## Task 9: `cursed-tdd` mirror section in cursed CLAUDE.md (W3.1, part 2 of 2)

**Files:**
- Modify: `~/cursed/CLAUDE.md` — add `## Compiler/Runtime Fix Protocol` section

- [ ] **Step 1: Insert the mirror section**

In `~/cursed/CLAUDE.md`, after the `## Build And Test` section, insert:

```markdown
## Compiler/Runtime Fix Protocol

This section duplicates the `cursed-tdd` Claude skill so Codex (and
Claude without the skill) follows the same checklist.

1. Minimal failing `.💀` reproducer in `/tmp`. Confirm it fails for
   the right reason.
2. Bytes-and-exit verification: stdout via `xxd -p`, stderr captured
   separately, exit code, and `--emit-ir` output when codegen is
   suspected. Source reads alone are insufficient; the compiler can
   inject calls grep won't show.
3. Promote the reproducer into `probes/cases/` so the harness catches
   regressions.
4. Run `bash ~/brat/experiments/verify_cursed_gaps.sh`. New failures
   are blockers unless intentional and called out in the commit body.
5. If the fix closes or surfaces a gap, follow the cross-repo doc
   sync section below to update brat's tracking docs in a separate
   commit in `~/brat`.
```

- [ ] **Step 2: Commit**

```bash
cd ~/cursed
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude): compiler/runtime fix protocol section

Mirrors the cursed-tdd Claude skill so Codex follows the same
checklist when fixing language behavior.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: `cross-repo-sync` skill (W3.2, part 1 of 3)

**Files:**
- Create: `~/.claude/skills/cross-repo-sync/SKILL.md`

- [ ] **Step 1: Author the skill**

```bash
mkdir -p ~/.claude/skills/cross-repo-sync
```

Create `~/.claude/skills/cross-repo-sync/SKILL.md`:

```markdown
---
name: cross-repo-sync
description: Use when a change in ~/cursed closes or surfaces a CURSED gap. Walks the four brat tracking files and prompts for required updates, then commits them in ~/brat separately from the cursed commit.
---

# Cross-Repo Doc Sync

Triggered when a `~/cursed` change moves the brat ↔ CURSED gap
picture. Walks the four tracking files in `~/brat` and asks "did this
change require an update?" Commits brat-doc updates separately from
the cursed commit (the cursed CLAUDE.md requires this).

## Files to consider

For each, decide *yes update* or *no, no change* and record the
reason in the brat commit body if you skip:

1. **`~/brat/UPSTREAM.md`** — issue/PR rows. Update status (e.g.,
   `Open` → `PR open` → `Merged`). Add a row if a new gap was
   surfaced.

2. **`~/brat/docs/cursed-subset.md`** — verified current behavior of
   `cursed-compiler --compile`. Update the bucket the primitive lives
   in (e.g., move from "blocked" to "works").

3. **`~/brat/docs/cursed-gaps.md`** — failure modes / blocked cases.
   If a gap closed, mark it accordingly. Keep the entry; do not
   delete history.

4. **`~/brat/docs/learnings.md`** — durable surprises only. Re-read
   the doc's own "When to update" section first. Load
   `~/tropes/tropes.md` before drafting (the brat CLAUDE.md flags
   "this changes everything"-style grandiosity, magic adverbs,
   `delve`/`tapestry`/`landscape`/`serves as`). Concrete and small.

## Commit shape

- Cursed commit lives on the cursed topic branch. No brat references
  required in its body.
- Brat doc-update commit lives in `~/brat` on `master`. Mention the
  cursed commit SHA so a later reader can bridge:

      docs: update cursed-subset for <primitive>

      Reflects ~/cursed <SHA> which now <behavior>.

      Co-authored-by: Claude <noreply@anthropic.com>

The brat post-commit hook auto-pushes to `origin/master`. Cursed
commits go to `origin/<topic-branch>`, never `upstream`.
```

- [ ] **Step 2: Verify file exists**

```bash
ls ~/.claude/skills/cross-repo-sync/SKILL.md
head -5 ~/.claude/skills/cross-repo-sync/SKILL.md
```

- [ ] **Step 3: No commit (user-level)**

---

## Task 11: Cross-repo discipline section in cursed CLAUDE.md (W3.2, part 2 of 3)

**Files:**
- Modify: `~/cursed/CLAUDE.md` — replace `## Cross-Repo Learnings` with `## Cross-Repo Doc Sync`

The `~/cursed/CLAUDE.md` already has a `## Cross-Repo Learnings` section that overlaps. We will replace it.

- [ ] **Step 1: Replace the existing `## Cross-Repo Learnings` section**

Find the existing `## Cross-Repo Learnings` heading in `~/cursed/CLAUDE.md`. Replace the entire section (heading through the next `##` heading, exclusive) with:

```markdown
## Cross-Repo Doc Sync

This section duplicates the `cross-repo-sync` Claude skill so Codex
follows the same protocol.

When a change in this repo closes or surfaces a CURSED gap, walk the
four brat tracking files and decide whether each needs an update:

- `~/brat/UPSTREAM.md` — issue/PR row updates or new rows
- `~/brat/docs/cursed-subset.md` — verified current behavior
- `~/brat/docs/cursed-gaps.md` — failure modes; mark closed gaps
- `~/brat/docs/learnings.md` — durable surprises only. Re-read the
  doc's own "When to update" section. Load `~/tropes/tropes.md`
  before drafting; avoid "this changes everything" grandiosity, magic
  adverbs, and `delve`/`tapestry`/`landscape`/`serves as`.

Commit the brat doc update in `~/brat` separately from the cursed
commit. Reference the cursed commit SHA in the brat commit body so a
later reader can bridge.
```

- [ ] **Step 2: Commit**

```bash
cd ~/cursed
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude): cross-repo doc sync section

Replaces "Cross-Repo Learnings" with a tighter section that mirrors
the cross-repo-sync Claude skill.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: Cross-repo paragraph in brat CLAUDE.md (W3.2, part 3 of 3)

**Files:**
- Modify: `~/brat/CLAUDE.md` — note the cursed-side obligation

- [ ] **Step 1: Add a short paragraph under "Files to keep current"**

In `~/brat/CLAUDE.md`, find the `## Files to keep current` section. Insert at the end of that section:

```markdown
**When the trigger is upstream work in `~/cursed`:** the cursed-side
CLAUDE.md describes the `cross-repo-sync` discipline that lands the
brat doc updates here. The Claude skill of the same name automates
the walk; without it, follow the cursed CLAUDE.md `## Cross-Repo Doc
Sync` section.
```

- [ ] **Step 2: Commit**

```bash
cd ~/brat
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude): point at cursed-side cross-repo-sync discipline

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: `upstream-sync.sh` — stub with dirty-tree refusal (W1.2, part 1 of 3)

**Files:**
- Create: `~/cursed/scripts/upstream-sync.sh`

This is a shell script with no native test framework. We test via run-with-expected-output. Build the script in two passes: stub that fails dirty-tree (this task), then full implementation (Task 14).

- [ ] **Step 1: Confirm `~/cursed/scripts/` exists**

```bash
ls -d ~/cursed/scripts
```

Expected: directory exists. (Already present per repo.)

- [ ] **Step 2: Write the stub**

Create `~/cursed/scripts/upstream-sync.sh`:

```bash
#!/bin/sh
# upstream-sync.sh — fast-forward zig from upstream, push origin, branch off
#
# Usage: scripts/upstream-sync.sh <topic-branch>
#
# Refuses to run with a dirty working tree.

set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 <topic-branch>" >&2
    exit 64
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "upstream-sync: working tree is dirty; commit or stash first" >&2
    exit 1
fi

echo "TODO: rest of sync"
exit 99
```

```bash
chmod +x ~/cursed/scripts/upstream-sync.sh
```

- [ ] **Step 3: Probe the dirty-tree refusal**

```bash
cd ~/cursed
echo "dirty" >> CLAUDE.md
./scripts/upstream-sync.sh foo
echo "exit=$?"
git checkout -- CLAUDE.md
```

Expected: stderr says `working tree is dirty`; exit code is 1. Then `git checkout` cleans up.

- [ ] **Step 4: Probe the usage refusal**

```bash
cd ~/cursed
./scripts/upstream-sync.sh
echo "exit=$?"
```

Expected: stderr says `usage: ... <topic-branch>`; exit code is 64.

- [ ] **Step 5: Probe the stub success path**

```bash
cd ~/cursed
./scripts/upstream-sync.sh some-branch
echo "exit=$?"
```

Expected: stdout `TODO: rest of sync`; exit code 99.

No commit yet — Task 14 finishes the implementation and commits both passes together.

---

## Task 14: `upstream-sync.sh` — full implementation (W1.2, part 2 of 3)

**Files:**
- Modify: `~/cursed/scripts/upstream-sync.sh`

- [ ] **Step 1: Replace the stub with the full sync**

Overwrite `~/cursed/scripts/upstream-sync.sh`:

```bash
#!/bin/sh
# upstream-sync.sh — fast-forward zig from upstream, push origin, branch off
#
# Usage: scripts/upstream-sync.sh <topic-branch>
#
# Refuses to run with a dirty working tree.
# Refuses non-fast-forward zig updates (lets git fail loudly).
# Pushes the freshly-merged zig to origin.
# Switches to the requested topic branch (creates it if needed).

set -eu

if [ "$#" -ne 1 ]; then
    echo "usage: $0 <topic-branch>" >&2
    exit 64
fi
topic="$1"

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "upstream-sync: working tree is dirty; commit or stash first" >&2
    exit 1
fi

echo "upstream-sync: fetching upstream..." >&2
git fetch upstream

echo "upstream-sync: switching to zig and fast-forwarding..." >&2
git switch zig
git merge --ff-only upstream/zig

echo "upstream-sync: pushing origin/zig..." >&2
git push origin zig

if git show-ref --verify --quiet "refs/heads/$topic"; then
    echo "upstream-sync: switching to existing topic branch $topic" >&2
    git switch "$topic"
else
    echo "upstream-sync: creating topic branch $topic" >&2
    git switch -c "$topic"
fi
```

- [ ] **Step 2: Probe dirty-tree path still rejects**

```bash
cd ~/cursed
echo "dirty" >> CLAUDE.md
./scripts/upstream-sync.sh foo
echo "exit=$?"
git checkout -- CLAUDE.md
```

Expected: stderr `working tree is dirty`; exit 1.

- [ ] **Step 3: Probe the happy path**

```bash
cd ~/cursed
git status
./scripts/upstream-sync.sh upstream-sync-test
git branch --show-current
git switch agent-setup
git branch -D upstream-sync-test
git push origin --delete upstream-sync-test 2>/dev/null || true
```

Expected: script runs cleanly; mid-run, `git branch --show-current` shows `upstream-sync-test`. Cleanup switches back to `agent-setup` and removes the test branch locally and (best-effort) on origin.

If `git push origin zig` failed, that means `zig` isn't tracking `origin/zig` correctly — investigate before continuing.

If the test branch was created on `agent-setup` rather than the freshly-merged `zig`, the script has a switch-order bug.

- [ ] **Step 4: Confirm we are back on `agent-setup`**

```bash
cd ~/cursed
git branch --show-current
```

Expected: `agent-setup`.

- [ ] **Step 5: Commit the script**

```bash
cd ~/cursed
git add scripts/upstream-sync.sh
git commit -m "$(cat <<'EOF'
chore: add scripts/upstream-sync.sh

Wraps the fork-update ritual so Claude and Codex leave identical
traces. Refuses dirty trees. Refuses non-FF zig updates (via git).

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 15: Point CLAUDE.md at `upstream-sync.sh` (W1.2, part 3 of 3)

**Files:**
- Modify: `~/cursed/CLAUDE.md` — replace inline `git fetch upstream / merge --ff-only` snippet with a script reference

- [ ] **Step 1: Find the existing snippet**

In `~/cursed/CLAUDE.md`, locate the bash block under `## Fork And Contribution Hygiene` that reads:

```bash
git fetch upstream
git switch zig
git merge --ff-only upstream/zig
git push origin zig
git switch -c <topic-branch>
```

- [ ] **Step 2: Replace with a script reference**

Replace the surrounding sentence ("Before starting upstreamable work:") and the bash block with:

```markdown
Before starting upstreamable work, run the sync script:

    scripts/upstream-sync.sh <topic-branch>

It fetches upstream, fast-forwards `zig`, pushes `origin/zig`, and
switches to the topic branch. It refuses to run with a dirty working
tree. Both Claude and Codex use the same script so traces line up.
```

- [ ] **Step 3: Commit**

```bash
cd ~/cursed
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs(claude): point fork-update ritual at scripts/upstream-sync.sh

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 16: brat `.claude/settings.json` allowlist (W2.1, part 1 of 2)

**Files:**
- Create: `~/brat/.claude/settings.json`

- [ ] **Step 1: Create directory**

```bash
mkdir -p ~/brat/.claude
```

- [ ] **Step 2: Run the `fewer-permission-prompts` skill in brat (preferred)**

In a Claude Code session with cwd = `~/brat`, invoke the
`fewer-permission-prompts` skill. Let it scan recent transcripts and
propose a narrow allowlist for `~/brat/.claude/settings.json`.

If running this plan inline (no fresh skill invocation possible),
hand-write the allowlist using Step 3.

- [ ] **Step 3: Hand-written fallback allowlist**

If the skill is not run, write `~/brat/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(pytest)",
      "Bash(pytest tests/*)",
      "Bash(pytest -k *)",
      "Bash(pytest -v)",
      "Bash(BRAT_UPDATE_GOLDENS=1 pytest tests/test_brat.py)",
      "Bash(./brat *)",
      "Bash(bash experiments/verify_cursed_gaps.sh)",
      "Bash(cz check *)",
      "Bash(git fetch upstream)",
      "Bash(xxd -p *)",
      "Bash(cursed-compiler *)"
    ]
  }
}
```

Narrow allowlists only — no `Bash(*)` wildcard.

- [ ] **Step 4: Verify**

```bash
python -c "import json; json.load(open('/home/ec2-user/brat/.claude/settings.json'))"
```

Expected: no output (no error).

- [ ] **Step 5: Commit**

```bash
cd ~/brat
git add .claude/settings.json
git commit -m "$(cat <<'EOF'
chore(claude): per-repo permission allowlist

Reduces prompt noise for the standard brat command set. Narrow
patterns only; no Bash(*) wildcard.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 17: cursed `.claude/settings.json` allowlist + SessionStart banner (W2.1 + W2.2)

**Files:**
- Create: `~/cursed/.claude/settings.json`

- [ ] **Step 1: Create directory**

```bash
mkdir -p ~/cursed/.claude
```

- [ ] **Step 2: Author settings with allowlist + SessionStart hook**

Write `~/cursed/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(zig build)",
      "Bash(zig build *)",
      "Bash(make build)",
      "Bash(make test)",
      "Bash(make probes)",
      "Bash(./zig-out/bin/cursed-compiler *)",
      "Bash(cursed-compiler *)",
      "Bash(pytest)",
      "Bash(pytest probes/*)",
      "Bash(pytest -v)",
      "Bash(bash ~/brat/experiments/verify_cursed_gaps.sh)",
      "Bash(cz check *)",
      "Bash(git fetch upstream)",
      "Bash(xxd -p *)",
      "Bash(scripts/upstream-sync.sh *)"
    ]
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "printf '\\nactive build target: src-zig/cursed_compiler_main.zig\\nactive runtime: src-zig/cursed_runtime.c\\nignore: advanced_*, *_fixed, *_complete, llvm_ir_pipeline_* unless wired in build.zig\\n\\n' 1>&2"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Verify JSON parses**

```bash
python -c "import json; print(json.load(open('/home/ec2-user/cursed/.claude/settings.json'))['hooks']['SessionStart'])"
```

Expected: prints the SessionStart hook structure without errors.

- [ ] **Step 4: Verify hook command runs cleanly when invoked manually**

```bash
sh -c "printf '\nactive build target: src-zig/cursed_compiler_main.zig\nactive runtime: src-zig/cursed_runtime.c\nignore: advanced_*, *_fixed, *_complete, llvm_ir_pipeline_* unless wired in build.zig\n\n' 1>&2"
```

Expected: the three-line banner prints to stderr.

- [ ] **Step 5: Test the banner end-to-end (manual)**

Open a new Claude Code session in `~/cursed`. The banner should appear in the session's startup context. If it does not, verify:

- The settings.json path is `~/cursed/.claude/settings.json` (not `~/.claude/settings.json`).
- The hook syntax matches the version of Claude Code in use (the `update-config` skill / Claude Code docs are authoritative).

If the hook syntax is wrong for the running version, treat that as a fix-needed rather than a stop — update settings.json and re-test.

- [ ] **Step 6: Commit**

```bash
cd ~/cursed
git add .claude/settings.json
git commit -m "$(cat <<'EOF'
chore(claude): per-repo allowlist + SessionStart active-path banner

Reduces prompt noise for the standard cursed command set. SessionStart
hook prints the active build target and runtime, and the parallel
src-zig directories to ignore unless wired in build.zig.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 18: Wire `verify_cursed_gaps.sh` into cursed `pre-push` (W4.2)

**Files:**
- Modify: `~/cursed/.githooks/pre-push`

- [ ] **Step 1: Read the existing hook**

```bash
cat ~/cursed/.githooks/pre-push
```

Note the current contents — the hook refuses pushes to `upstream` and
non-FF pushes to `zig`. We append the downstream check after these
existing checks.

- [ ] **Step 2: Append the downstream-check block**

At the end of `~/cursed/.githooks/pre-push`, before the final `exit 0`,
add:

```sh

# Downstream check: run brat's gap-verification probe set when the
# brat checkout is reachable. Non-blocking. Set
# CURSED_SKIP_DOWNSTREAM_CHECK=1 to disable.

if [ "${CURSED_SKIP_DOWNSTREAM_CHECK:-}" != "1" ] && [ -x "$HOME/brat/experiments/verify_cursed_gaps.sh" ]; then
    echo "pre-push: running ~/brat/experiments/verify_cursed_gaps.sh (non-blocking)" >&2
    if ! bash "$HOME/brat/experiments/verify_cursed_gaps.sh" >&2; then
        echo "pre-push: brat downstream check reported failures (push allowed; review the diff)" >&2
    fi
fi
```

If the existing hook ends with `exit 0`, place the new block just
before that line, not after.

- [ ] **Step 3: Test the hook with downstream check skipped**

```bash
cd ~/cursed
CURSED_SKIP_DOWNSTREAM_CHECK=1 git push origin agent-setup
echo "exit=$?"
```

Expected: push succeeds (or no-op if up to date); no `running ~/brat`
line in stderr.

- [ ] **Step 4: Test the hook with downstream check active**

```bash
cd ~/cursed
git commit --allow-empty -m "$(cat <<'EOF'
chore: empty commit to exercise pre-push hook

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
git push origin agent-setup
```

Expected: stderr shows `pre-push: running ~/brat/experiments/verify_cursed_gaps.sh (non-blocking)` followed by the script output. Push succeeds regardless of script result.

If the script fails for an unrelated reason (e.g., `cursed-compiler`
not in PATH for the hook environment), document the requirement in
the hook (e.g., set `PATH=$HOME/.local/bin:$PATH` at the top of the
hook block).

- [ ] **Step 5: Test the unreachable-brat path**

```bash
cd ~/cursed
mv ~/brat ~/brat.tmp
git commit --allow-empty -m "$(cat <<'EOF'
chore: empty commit to re-trigger pre-push (brat moved)

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
git push origin agent-setup
mv ~/brat.tmp ~/brat
```

Expected: push succeeds with no `running ~/brat` line. (The `-x` test
returns false when the script is missing.)

- [ ] **Step 6: Clean up the empty commits used as triggers**

```bash
cd ~/cursed
git reset --hard HEAD~2
git push --force-with-lease origin agent-setup
```

`--force-with-lease` is acceptable on a personal topic branch per the
cursed CLAUDE.md.

- [ ] **Step 7: Commit the hook change**

```bash
cd ~/cursed
git add .githooks/pre-push
git commit -m "$(cat <<'EOF'
chore(hooks): pre-push runs brat downstream gap check (non-blocking)

Picks up brat's verify_cursed_gaps.sh when the checkout is reachable.
Skips silently if brat is missing or CURSED_SKIP_DOWNSTREAM_CHECK=1.
Never blocks a push; the script output is informational.

Co-authored-by: Claude <noreply@anthropic.com>
EOF
)"
```

---

## Task 19: Final integration check

**Files:** none

- [ ] **Step 1: Both repos clean**

```bash
cd ~/brat && git status
cd ~/cursed && git status
```

Expected: both clean. If anything is untracked, audit each file before deciding what to commit.

- [ ] **Step 2: All commits visible**

```bash
cd ~/brat && git log --oneline -10
cd ~/cursed && git log --oneline origin/zig..agent-setup
```

Expected:
- brat shows several `docs(claude):` and `chore:` commits from this plan.
- cursed shows the topic-branch commits ahead of `origin/zig`.

- [ ] **Step 3: Sanity run the probe harness one more time**

```bash
cd ~/cursed && make probes
```

Expected: `1 passed`.

- [ ] **Step 4: Sanity run the brat test suite**

```bash
cd ~/brat && pytest -q
```

Expected: same pass count as before this plan started. If different, investigate before declaring done.

- [ ] **Step 5: Sanity check the symlinks**

```bash
ls -l ~/brat/tropes.md ~/cursed/tropes.md
```

Expected: both resolve to `/home/ec2-user/tropes/tropes.md`.

- [ ] **Step 6: Sanity check both `.claude/settings.json` files parse**

```bash
python -c "import json; json.load(open('/home/ec2-user/brat/.claude/settings.json'))"
python -c "import json; json.load(open('/home/ec2-user/cursed/.claude/settings.json'))"
```

Expected: no output (no error).

- [ ] **Step 7: Confirm both skill files exist**

```bash
ls ~/.claude/skills/cursed-tdd/SKILL.md ~/.claude/skills/cross-repo-sync/SKILL.md
```

Expected: both files listed.

- [ ] **Step 8: Push the cursed topic branch one final time**

```bash
cd ~/cursed
git push origin agent-setup
```

Expected: success. The pre-push downstream check runs again — that's fine.

The cursed `agent-setup` branch is left as-is on `origin`. Whether
to merge into `zig`, open a PR upstream, or sit on it for now is a
follow-up decision, not this plan's scope.

---

## Self-review reminder for the executor

Before marking this plan complete, verify:

- No `.💀` syntax was hand-rolled — every sample matches what the live
  compiler accepts (Task 6 Step 1).
- No skill or settings file accidentally references a tool the
  executing model does not have access to.
- Every commit body has a `Co-authored-by` trailer.
- No commit was pushed to `upstream` (cursed) at any point.
- The `agent-setup` branch in `~/cursed` was force-pushed only once
  (Task 18 Step 6) using `--force-with-lease` to clean up the trigger
  commits.
