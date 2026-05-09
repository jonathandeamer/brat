# learnings doc — design

**Status:** approved (brainstorming, 2026-05-09)
**Next step:** implementation plan via writing-plans skill.

## 1. Overview

A running journal at `docs/learnings.md` that captures observations
from building brat, intended as fodder for a later blog post. Three
axes of interest:

1. Writing in an unusual language (CURSED).
2. Contributing back to a young/new language.
3. Agentic coding in a thin-training-data language space.

The doc is append-only by design. The agent is allowed and encouraged
to add entries during sessions, with explicit guardrails about what to
write, when to write it, and how not to oversell a small hobby project.

## 2. Scope

### In scope

- A single file: `docs/learnings.md`.
- Light per-entry template (What happened / Why it's interesting /
  Quote-worthy bit), all headings optional.
- A `## Running Themes` appendix for periodic synthesis.
- Agent-update guidance section at the top of the file.
- Five seed entries backfilled from the existing project history.
- Committed to git like any other doc.

### Out of scope

- No automation, no hooks, no CI checks on entries.
- No tag taxonomy beyond `#cursed`, `#contributing`, `#agentic`.
- No separate per-theme files.
- No formal review process for entries.

## 3. File location and structure

Path: `/home/ec2-user/brat/docs/learnings.md` (sibling to
`docs/superpowers/`).

Top-level layout:

```
# What I Learned Building brat

(intro paragraph: what this doc is, three axes, tags)

## For agents updating this doc
  ### When to update
  ### Rules for entries
  ### Keep it small (this is a hobby project)

## Entries
  (newest on top, dated YYYY-MM-DD, one h3 per entry)

## Running Themes
  (appendix, mostly human-maintained)
```

## 4. Entry template

```markdown
### YYYY-MM-DD — short title  `#tag` `#tag`

**What happened:** ...
**Why it's interesting:** ...
**Quote-worthy bit:** ...
```

Any of the three headings can be skipped. Free-form prose or bullets
under each is fine. First person is fine, including from the agent.

Tags are drawn from a fixed set of three:

- `#cursed` — writing in the language itself.
- `#contributing` — interactions with CURSED-the-project.
- `#agentic` — coding-with-an-agent in this language space.

An entry can carry more than one tag.

## 5. Agent-update guidance

This section lives at the top of `learnings.md` so the agent reads it
before appending. It has three parts.

### 5.1 When to update

The agent should consider writing an entry when any of these happen
in a session:

- A CURSED limitation, bug, or missing primitive surfaces (anything
  that forces a workaround). `#cursed`
- An upstream issue, PR, or feature request gets filed against
  CURSED — capture what motivated it. `#contributing`
- The agent invents plausible-looking CURSED syntax that turns out
  not to exist, or catches itself about to. The hallucination shape
  is the interesting part. `#agentic`
- A scope or design decision turns on the language's quirks. `#cursed`
- Tooling and docs gaps bite (sparse search results, no LSP, compiler
  errors that mislead). `#agentic`
- The user says something quote-worthy: a sharp framing, a joke that
  lands, a design constraint phrased memorably.
- The agent is surprised. Surprise is the signal.

Do not add entries for routine green tests, normal commits, plan
edits, or refactors. "Got the test passing" is not an entry. "Got
the test passing after discovering `fs.read_file` returns errno as
a string" is.

When in doubt, write it. A weak entry can be deleted; a missed one
is gone.

### 5.2 Rules for entries

- Append, don't rewrite. Existing entries are primary sources; do
  not normalize, tidy, or edit them.
- Use the entry template. Skip any heading that doesn't apply.
- Tag with one or more of `#cursed`, `#contributing`, `#agentic`.
- First person is fine.
- `## Running Themes` is mostly human territory. The agent may add
  to it only when the same pattern shows up in three or more
  existing log entries, and only by citing those entry dates inline.
  Single-anecdote themes are not allowed.
- Commit each update as `docs(learnings): <short title>`.

### 5.3 Keep it small (this is a hobby project)

brat is a cat-clone. It is a small, fun project. It is not a turning
point, a new paradigm, or a meditation on the nature of programming.
The doc should not read like it is.

Before committing an entry, read `~/tropes/tropes.md` and check the
draft against it. The list below is the subset that bites hardest
for a journal like this one:

- No grandiose stakes. Cut anything that sounds like a VC pitch.
- No invented concept labels (no "the CURSED paradox," no "esolang
  inversion"). Describe what happened.
- No false-profundity reframes. Avoid "It's not X, it's Y," "Not X.
  Not Y. Just Z.," and "The X? A Y." One reframe per entry maximum,
  and only if it earns it.
- No magic adverbs: drop "quietly," "deeply," "fundamentally,"
  "remarkably," "arguably."
- No grandiose nouns: no "tapestry," "landscape," "paradigm,"
  "ecosystem" (unless you mean a software ecosystem).
- No "serves as." Just say "is."
- Em dashes: at most one or two per entry. Not a default punctuation.
- No bold-first bullets outside the entry template headings.
- Plain words. "Use," not "leverage" or "utilize." "Strong," not
  "robust."

## 6. Seed content

Five backfilled entries, dated 2026-05-09, drawn from the existing
project history. The agent writing the doc may adjust wording but
should keep the substance below.

1. **Why CURSED at all** — the pitch is the combination, not any
   single layer: a real Unix utility, written in an esolang, that
   motivates real file I/O upstream, with a brat-album aesthetic.
   Tags: `#cursed #contributing`.

2. **Scope as aesthetic** — "no flags. brat doesn't speak." Cutting
   scope is a design constraint that doubles as a joke. Helpful when
   the language is half-baked: less surface area, fewer unknowns.
   Tags: `#cursed`.

3. **Golden ambiguities** — the TDD addendum pinned six behaviors the
   spec did not pin. In a young language, specs have more holes than
   usual; tests are how you nail jelly to the wall.
   Tags: `#cursed #agentic`.

4. **python3 vs python, and the unauthorized symlink** — a small
   agentic-coding cautionary tale. The agent created a symlink to
   work around a `python` vs `python3` issue; that got reverted, and
   the plan was fixed properly. The shortcut and the revert are both
   the lesson.
   Tags: `#agentic`.

5. **Bratism as error-message constraint** — "bestie you have to give
   me a file" is a UX spec, not flavor. Error copy is normally an
   afterthought; here it is load-bearing.
   Tags: `#cursed`.

The `## Running Themes` appendix starts empty.

## 7. Open questions

None at design time. Any future ambiguity (e.g. whether a fourth tag
is warranted, whether to split the file once it's long) gets resolved
by editing this spec or writing a follow-up.
