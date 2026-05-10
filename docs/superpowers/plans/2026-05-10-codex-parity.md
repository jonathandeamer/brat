# Codex Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Codex the same durable project workflow guidance that the previous setup added for Claude, without trying to mirror Claude-only permission and hook features that do not map cleanly.

**Architecture:** Treat repo docs and executable scripts as the shared source of truth. Add Codex-local skill copies for the two project-specific Claude skills, then document the parity boundary in `CLAUDE.md`/`AGENTS.md` so future workers know which pieces are shared, duplicated, or intentionally Claude-only. Do not add Codex permission/hook scaffolding unless a real Codex-supported mechanism exists in this checkout.

**Tech Stack:** Markdown skills under `~/.codex/skills/`, existing `~/.codex/config.toml`, existing repo docs in `~/brat` and `~/cursed`, shell verification with `find`, `diff`, `python`, `git`, `make probes`, and `pytest`.

---

## File Structure

Files created or modified by this plan:

**`~/.codex/skills/`:**
- `cursed-tdd/SKILL.md` - new Codex-local copy of the project-specific compiler/runtime workflow skill
- `cross-repo-sync/SKILL.md` - new Codex-local copy of the project-specific cross-repo doc sync workflow skill

**`~/brat/`:**
- `CLAUDE.md` - modified; because `AGENTS.md` symlinks to this file, this is also Codex guidance

**`~/cursed/`:**
- `CLAUDE.md` - modified; because `AGENTS.md` symlinks to this file, this is also Codex guidance

No Codex permission allowlist or SessionStart hook file is planned. In this checkout, Codex trust and approvals live in `~/.codex/config.toml` plus the runtime sandbox approval model, and both project paths are already trusted.

---

## Task 0: Sanity Check Current Parity State

**Files:** none

- [ ] **Step 1: Verify both repos are clean**

```bash
cd ~/brat && git status --short
cd ~/cursed && git status --short
```

Expected: no output from either command. If either repo is dirty, stop and inspect the diff before continuing.

- [ ] **Step 2: Verify shared agent docs exist**

```bash
ls -l ~/brat/AGENTS.md ~/cursed/AGENTS.md
readlink ~/brat/AGENTS.md
readlink ~/cursed/AGENTS.md
```

Expected: both `AGENTS.md` files point to `CLAUDE.md`. This means Codex reads the same repo guidance as Claude.

- [ ] **Step 3: Verify Codex already trusts both repos and has Superpowers enabled**

```bash
sed -n '1,120p' ~/.codex/config.toml
```

Expected: entries for:

```toml
[projects."/home/ec2-user/brat"]
trust_level = "trusted"

[projects."/home/ec2-user/cursed"]
trust_level = "trusted"

[plugins."superpowers@openai-curated"]
enabled = true
```

If any entry is missing, add it before continuing and restart Codex after the plan is complete.

- [ ] **Step 4: Verify Claude-only project skills exist**

```bash
ls ~/.claude/skills/cursed-tdd/SKILL.md ~/.claude/skills/cross-repo-sync/SKILL.md
```

Expected: both files exist. If either is missing, stop; the Codex copies must be based on the current Claude skill content.

---

## Task 1: Install Codex Copy of `cursed-tdd`

**Files:**
- Create: `~/.codex/skills/cursed-tdd/SKILL.md`

- [ ] **Step 1: Create the Codex skill directory**

```bash
mkdir -p ~/.codex/skills/cursed-tdd
```

Expected: command exits 0.

- [ ] **Step 2: Copy the current Claude skill into Codex**

```bash
cp ~/.claude/skills/cursed-tdd/SKILL.md ~/.codex/skills/cursed-tdd/SKILL.md
```

Expected: command exits 0.

- [ ] **Step 3: Verify byte-for-byte parity**

```bash
diff -u ~/.claude/skills/cursed-tdd/SKILL.md ~/.codex/skills/cursed-tdd/SKILL.md
```

Expected: no output. If there is output, inspect it; the Codex copy should match the Claude skill at installation time.

- [ ] **Step 4: Verify frontmatter is readable**

```bash
head -5 ~/.codex/skills/cursed-tdd/SKILL.md
```

Expected:

```markdown
---
name: cursed-tdd
description: Use when fixing or extending CURSED compiler/runtime behavior in ~/cursed. Enforces minimal-reproducer-first TDD with bytes-and-exit verification, and re-runs the brat downstream probe set before claiming a fix is done.
---
```

No commit: this is user-level Codex configuration outside a repo.

---

## Task 2: Install Codex Copy of `cross-repo-sync`

**Files:**
- Create: `~/.codex/skills/cross-repo-sync/SKILL.md`

- [ ] **Step 1: Create the Codex skill directory**

```bash
mkdir -p ~/.codex/skills/cross-repo-sync
```

Expected: command exits 0.

- [ ] **Step 2: Copy the current Claude skill into Codex**

```bash
cp ~/.claude/skills/cross-repo-sync/SKILL.md ~/.codex/skills/cross-repo-sync/SKILL.md
```

Expected: command exits 0.

- [ ] **Step 3: Verify byte-for-byte parity**

```bash
diff -u ~/.claude/skills/cross-repo-sync/SKILL.md ~/.codex/skills/cross-repo-sync/SKILL.md
```

Expected: no output. If there is output, inspect it; the Codex copy should match the Claude skill at installation time.

- [ ] **Step 4: Verify frontmatter is readable**

```bash
head -5 ~/.codex/skills/cross-repo-sync/SKILL.md
```

Expected:

```markdown
---
name: cross-repo-sync
description: Use when a change in ~/cursed closes or surfaces a CURSED gap. Walks the four brat tracking files and prompts for required updates, then commits them in ~/brat separately from the cursed commit.
---
```

No commit: this is user-level Codex configuration outside a repo.

---

## Task 3: Document Codex Parity Boundary in `~/brat`

**Files:**
- Modify: `~/brat/CLAUDE.md`

- [ ] **Step 1: Add a Codex parity paragraph**

In `~/brat/CLAUDE.md`, under the existing `## Workflow` section, after the bullet named `Name Claude-only tools when they drove a decision`, add:

```markdown
- **Keep project skills paired across agents.** The project-specific
  skills `cursed-tdd` and `cross-repo-sync` should exist in both
  `~/.claude/skills/` and `~/.codex/skills/`. They intentionally
  duplicate the same checklist text so either agent can replay the
  same workflow. After editing one copy, update the other and verify
  with `diff -u`.
```

- [ ] **Step 2: Verify the text is present through the Codex entrypoint**

```bash
grep -n "Keep project skills paired across agents" ~/brat/AGENTS.md
grep -n "~/.codex/skills" ~/brat/AGENTS.md
```

Expected: both commands print matching lines from `CLAUDE.md` through the `AGENTS.md` symlink.

- [ ] **Step 3: Commit**

```bash
cd ~/brat
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs: document Codex project skill parity

Records that cursed-tdd and cross-repo-sync are paired user-level
skills under both ~/.claude/skills and ~/.codex/skills.

Co-authored-by: Codex <codex@openai.com>
EOF
)"
```

Expected: commit-msg hook passes. The brat post-commit hook may auto-push `master`; that is expected in this repo.

---

## Task 4: Document Codex Parity Boundary in `~/cursed`

**Files:**
- Modify: `~/cursed/CLAUDE.md`

- [ ] **Step 1: Add a Codex parity paragraph**

In `~/cursed/CLAUDE.md`, under `## Agent Attribution`, after the existing paragraph beginning `Claude has skills, slash commands`, add:

```markdown
Project-specific skills are paired across agents when possible:
`cursed-tdd` and `cross-repo-sync` should exist in both
`~/.claude/skills/` and `~/.codex/skills/`. If one copy changes, update
the other and verify with `diff -u`. Claude-only permission allowlists
and `SessionStart` hooks do not have a direct Codex equivalent here;
Codex uses `~/.codex/config.toml`, project trust entries, and runtime
sandbox approvals instead.
```

- [ ] **Step 2: Verify the text is present through the Codex entrypoint**

```bash
grep -n "Project-specific skills are paired across agents" ~/cursed/AGENTS.md
grep -n "~/.codex/config.toml" ~/cursed/AGENTS.md
```

Expected: both commands print matching lines from `CLAUDE.md` through the `AGENTS.md` symlink.

- [ ] **Step 3: Commit**

```bash
cd ~/cursed
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs: document Codex project skill parity

Records which project workflow scaffolding is duplicated for Codex and
which Claude-only settings intentionally do not map.

Co-authored-by: Codex <codex@openai.com>
EOF
)"
```

Expected: commit-msg hook passes. The cursed post-commit hook may skip auto-push if the branch has no upstream.

---

## Task 5: Final Verification

**Files:** none

- [ ] **Step 1: Verify Codex skill files exist**

```bash
ls ~/.codex/skills/cursed-tdd/SKILL.md ~/.codex/skills/cross-repo-sync/SKILL.md
```

Expected: both files are listed.

- [ ] **Step 2: Verify Claude/Codex project skill copies still match**

```bash
diff -u ~/.claude/skills/cursed-tdd/SKILL.md ~/.codex/skills/cursed-tdd/SKILL.md
diff -u ~/.claude/skills/cross-repo-sync/SKILL.md ~/.codex/skills/cross-repo-sync/SKILL.md
```

Expected: no output from either command.

- [ ] **Step 3: Verify repo docs mention the parity boundary**

```bash
grep -n "~/.codex/skills" ~/brat/AGENTS.md ~/cursed/AGENTS.md
grep -n "SessionStart" ~/cursed/AGENTS.md
```

Expected: the first command finds skill parity guidance in both repos; the second finds the note that Claude `SessionStart` hooks do not directly map to Codex.

- [ ] **Step 4: Verify `~/cursed` probes still pass**

```bash
cd ~/cursed
make probes
```

Expected: `1 passed`.

- [ ] **Step 5: Verify brat non-binary tests still pass**

The full brat suite requires a real `./brat` binary. Until that binary exists, run the tests that do not depend on it:

```bash
cd ~/brat
pytest tests/test_header.py tests/test_harness_smoke.py -q
```

Expected: all selected tests pass.

- [ ] **Step 6: Verify both repos are clean**

```bash
cd ~/brat && git status --short
cd ~/cursed && git status --short
```

Expected: no output from either command.

- [ ] **Step 7: Restart Codex**

Restart the Codex session so the newly installed `~/.codex/skills/` entries are discovered and included in the available skills list.

Expected after restart: the available skills include `cursed-tdd` and `cross-repo-sync` as local Codex skills.

---

## Self-Review

- Spec coverage: covers skills, shared docs, Codex config/trust, and the non-equivalence of Claude settings/hooks.
- Placeholder scan: no TBD/TODO/fill-in steps.
- Scope control: intentionally excludes new Codex permission or hook machinery because no direct equivalent is present in this checkout.
