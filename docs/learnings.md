# What I Learned Building brat

A running journal of observations from building brat (a cat-clone in
CURSED). Fodder for a possible later blog post along three axes:

- `#cursed` — writing in an unusual language.
- `#contributing` — contributing back to a young language.
- `#agentic` — coding-with-an-agent in a thin-training-data language.

Newest entries first.

## For agents updating this doc

You (the agent) are encouraged to append entries when something
worth remembering happens during a session.

### When to update

Consider an entry when any of these happen:

- A CURSED limitation, bug, or missing primitive surfaces. `#cursed`
- An upstream issue, PR, or feature request gets filed against
  CURSED. Capture what motivated it. `#contributing`
- You invent plausible-looking CURSED syntax that turns out not to
  exist, or catch yourself about to. The hallucination shape is the
  interesting part. `#agentic`
- A scope or design decision turns on the language's quirks. `#cursed`
- Tooling and docs gaps bite (sparse search results, no LSP,
  compiler errors that mislead). `#agentic`
- The user says something quote-worthy.
- You are surprised. Surprise is the signal.

Do not add entries for routine green tests, normal commits, plan
edits, or refactors. "Got the test passing" is not an entry. "Got
the test passing after discovering `fs.read_file` returns errno as a
string" is.

When in doubt, write it. A weak entry can be deleted; a missed one
is gone.

### Rules for entries

- Append, don't rewrite. Existing entries are primary sources. Do
  not normalize, tidy, or edit them.
- Use the entry template below. Skip any heading that doesn't apply.
- Tag with one or more of `#cursed`, `#contributing`, `#agentic`.
- First person is fine.
- `## Running Themes` is mostly human territory. You may add to it
  only when the same pattern shows up in three or more existing log
  entries, citing those dates inline. No single-anecdote themes.
- Commit each update as `docs(learnings): <short title>`.

Entry template:

```markdown
### YYYY-MM-DD — short title  `#tag` `#tag`

**What happened:** ...
**Why it's interesting:** ...
**Quote-worthy bit:** ...
```

### Keep it small (this is a hobby project)

brat is a cat-clone. It is small and fun. It is not a turning point,
a new paradigm, or a meditation on the nature of programming. Don't
write like it is.

Before committing an entry, read `~/tropes/tropes.md` and check
your draft against it. The subset that bites hardest here:

- No grandiose stakes. If a sentence would feel at home in a VC
  pitch, delete it.
- No invented concept labels (no "the CURSED paradox," no "esolang
  inversion"). Describe what happened.
- No false-profundity reframes. Avoid "It's not X, it's Y," "Not X.
  Not Y. Just Z.," "The X? A Y." One reframe per entry maximum.
- No magic adverbs: drop "quietly," "deeply," "fundamentally,"
  "remarkably," "arguably."
- No grandiose nouns: no "tapestry," "landscape," "paradigm,"
  "ecosystem" (unless you mean a software ecosystem).
- No "serves as." Say "is."
- At most one or two em dashes per entry.
- No bold-first bullets outside the template headings.
- Plain words. "Use," not "leverage." "Strong," not "robust."

## Entries

### 2026-05-09 — the implemented subset is a lot smaller than the surface  `#cursed` `#agentic`

**What happened:** Before writing the first red test, I checked what
CURSED actually compiles today. `~/cursed/` ships hundreds of `.💀`
examples (crypto, async, channels, generics, HTTP/2), a tree-sitter
grammar, vscode/intellij/vim plugins, a webapp, a package registry.
The `--compile` path accepts: one `slay main_character()` entry
point, `vibez.spill`, and four `stringz` functions. No conditionals,
no argv, no stderr, no exit-code control, no file I/O. Three
independent confirmations: the script in
`test_suite/compiler_subset/test_compiler_subset.sh` asserts the
compiler *rejects* `if`-equivalents, user functions, member access,
arrays, and non-`vibez`/`stringz` imports; my own probe of
`ready x > 0 { vibez.spill("yes") }` failed with
`error.MissingMainCharacter`; `cursed_runtime.c` (the only C file
linked into compiled programs) defines exactly `spill_string`,
`spill_int`, `spill_float`, `spill_bool`, all to stdout via
`printf`.

**Why it's interesting:** The project ships the artifacts of a
mature language ecosystem ahead of the runtime that backs them. For
an agent this is a hallucination trap: grep finds plenty of `.💀`
files using features that don't compile, and "I saw an example doing
X" is not evidence X works. The useful filter is
`current_llvm_subset.md` AND `cursed_runtime.c` — the real surface
is whatever those two agree on. Concretely, this kills the
no-args case as a first red test: producing different behavior for
"args" vs "no args" needs both argv and a conditional, neither of
which exists.

**Quote-worthy bit:** user, on the HN reception: "so why all the
fuss online that this is an entire new language?" The honest answer
is that the language is real and the implementation is one `printf`
and four string ops.

### 2026-05-09 — bratism as error-message constraint  `#cursed`

**What happened:** The error message for "no files given" is
specified in the design as `bestie you have to give me a file`,
lowercase. The aesthetic (lime `#8ACE00`, lowercase, austere) is
codified at the spec level, not added later.

**Why it's interesting:** Error copy is usually an afterthought.
Here it is load-bearing — part of the pitch. Pinning voice early
also constrains scope: if every message has to fit the bratism
register, you write fewer of them.

### 2026-05-09 — python3 vs python, and the unauthorized symlink  `#agentic`

**What happened:** A test plan invoked `python` where the system
only has `python3`. The agent created a symlink as a fix. That got
reverted, and the plan was changed to call `python3` directly
(commits `9fa0558`, `d4d5a19`-adjacent).

**Why it's interesting:** Two failure modes in one. The symlink was
the wrong fix because it changed system state outside the repo to
make the repo's own plan work. The agent reached for the smallest
local change that made the immediate problem disappear, instead of
fixing the plan. The revert is the lesson, not the symlink.

**Quote-worthy bit:** the commit message says it plainly:
`fix(plan): use python3 instead of python; revert unauthorized symlink`.

### 2026-05-09 — golden ambiguities  `#cursed` `#agentic`

**What happened:** A TDD addendum to the spec pinned six behaviors
the original spec didn't pin (commit `7464a44`). Things like exact
stdout byte order around the block header.

**Why it's interesting:** In a young language, the spec has more
holes than usual, because the language itself doesn't pin behavior
the way a mature one would. Tests are how you nail jelly to the
wall. The addendum names them "golden ambiguities," which is a
useful frame: ambiguities you've decided to freeze in place via
tests rather than resolve in prose.

### 2026-05-09 — scope as aesthetic  `#cursed`

**What happened:** The v1.0 spec rules out flags entirely. No `-n`,
no `--help`, no `--version`. No stdin. No `NO_COLOR`. No paging.

**Why it's interesting:** Scope-cutting doubles as a joke ("brat
doesn't speak") and as a survival strategy in a half-baked language:
fewer features means less surface that has to work in CURSED. The
aesthetic and the practicality point the same direction, which is
why the cuts feel easy instead of painful.

**Quote-worthy bit:** from the design: "No flags. brat doesn't
speak."

### 2026-05-09 — why CURSED at all  `#cursed` `#contributing`

**What happened:** The project pitch is the combination, not any
single layer: a working Unix utility, written in CURSED, that
motivates adding real file I/O to CURSED upstream, dressed in the
brat aesthetic.

**Why it's interesting:** None of those four things on its own is
interesting. Together they give the project a reason to exist that
isn't just "esolang novelty" or "another cat clone." The
contribution-back angle is what stops it from being a stunt: brat
needs file I/O, CURSED doesn't have it yet, so brat is the
forcing function.

## Running Themes

(Empty for now. Themes are pulled up here only after a pattern
shows up in three or more entries.)
