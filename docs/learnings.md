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

### 2026-05-10 — the loop symlinked a fake home into my real one  `#agentic`

**What happened:** The remote history for
`jonathandeamer/old-quackdown-shakedown-etc` explains why a
`/home/ghuntley` directory existed on the earlier machine. In
commit `3f8656e`, `.agent/blockers.md` records that the CURSED
compiler shelled out to clang with a hardcoded runtime path:
`/home/ghuntley/cursed/src-zig/cursed_runtime.c`. The workaround
the loop applied was:

```bash
sudo ln -s /home/ec2-user /home/ghuntley
```

That made `~/cursed` visible at the path the compiler expected, but
it also made `/home/ghuntley/.ssh` point at the real
`/home/ec2-user/.ssh`. A month later, after the brat work made the
old `ghuntley` path look like stray user-state, deleting it as
cleanup broke SSH access. A plain `rm -rf /home/ghuntley` would
remove only the symlink on GNU `rm`; deleting with a trailing slash
or deleting children under it can follow the link and remove real
files.

**Why it's interesting:** A Ralph/Huntley loop running in yolo mode
can fix a blocked build by changing machine-level state, then leave
behind a path that looks like an unrelated user account. The action
was rational in the moment: one hardcoded compiler path, one symlink,
green trivial compile. The risk only showed up later, when the
workaround had lost its context. Narrower workaround next time:
create `/home/ghuntley` as a real directory and symlink only
`/home/ghuntley/cursed` to `/home/ec2-user/cursed`.

**Quote-worthy bit:** `sudo ln -s /home/ec2-user /home/ghuntley`

### 2026-05-10 — a sibling-repo loop left fingerprints in my audit  `#agentic` `#cursed`

**What happened:** The local-only commits that anchored the
original brat audit (`specs/current_llvm_subset.md`,
`test_suite/compiler_subset/`, `src-zig/supported_subset.zig`)
were authored 2026-04-11 17:26 UTC during a Huntley-loop attempt
at *snarkdown* — an earlier project that tried to port Markdown
to CURSED. Per
`~/old-quackdown-shakedown-etc/docs/project-history.md`, that loop
discovered CURSED was pre-alpha (no stdin, no file I/O, no
conditionals, no loops) and pivoted to DuckDB the same day.
Before pivoting, it went into the `~/cursed/` checkout, cloned
30 minutes earlier, and committed three files documenting and
gating CURSED's working surface. The commits never got pushed.

A month later (this brat session) I read those three files as
upstream sources of truth and anchored every gap section against
them. The directional conclusions held, but the failure-mode
evidence reflected the local validator's clean
`UnsupportedConstruct` rejections, not the silent miscompiles
upstream actually produces. The audit took two re-runs to
converge against clean upstream.

**Why it's interesting:** An autonomous loop in one project can
leave residue in a shared dependency that a later, less-
autonomous session in a different project unknowingly reads as
ambient truth. Nothing in this repo's git history mentioned
snarkdown, and the local `~/cursed/` files looked indistinguish-
able from upstream documentation. Worth a check before treating
a sibling repo's specs as authoritative: `git log @{u}.. <file>`
or `git diff @{u}` to see if the file is local-only.

### 2026-05-10 — the gated picture wasn't the upstream picture  `#cursed` `#agentic`

**What happened:** The original cursed-gaps audit ran against a
local CURSED checkout that had three unpushed commits adding a
subset validator, the `current_llvm_subset.md` doc, and a test
fixture suite. Those commits got reset away (see entry below). I
rebuilt the compiler against clean upstream and re-ran the
verifier script. Most of the "compile-time rejection" gaps weren't
gaps at all in upstream: argless void user-defined functions
work, integer arithmetic works, assignment works, non-stdlib
imports compile clean. What I found in their place was a more
hostile pattern: the compiler accepts these constructs and
*silently miscompiles* them. `ready` and `bestie` cause the whole
enclosing function to disappear from the captured-calls list; array
indexing always emits `spill_int(i64 1)` regardless of array or
index; UDF arguments lower to integer 0; member access produces
broken IR that clang refuses. Net for brat: 12 gaps where there
were 14, but with worse failure modes for most of them.

**Why it's interesting:** A validator that cleanly rejects
unsupported constructs is friendlier to write against than a
permissive parser that lets them through and miscompiles them.
The local gating layer existed for a good reason. The CLAUDE.md
rule about runtime-execution probes (added after the `vibez.spill`
IR finding) covers more than just stdout semantics — it applies to
every primitive in this codebase, since "compiles cleanly" tells
you almost nothing about whether the program will actually do what
it looks like it does.

**Quote-worthy bit:** `Generated dynamic LLVM IR with 0 strings,
0 variables, 0 calls` (the compile log for a function whose only
sin was containing a `ready`).

### 2026-05-10 — the subset gatekeeper was unpushed local work  `#workingoncursed` `#contributing` `#agentic`

**What happened:** Setting up the standard fork+remote layout for ~/cursed (origin = my fork, upstream = ghuntley/cursed). Local `zig` was 3 commits ahead, 0 behind upstream. I told the agent to "overwrite the local commits, pulling from remote," meaning take upstream's state. The agent confirmed once and ran `git reset --hard upstream/zig`. The three commits (`test(compiler): add focused llvm subset integration coverage`, `fix(compiler): fail hard outside the supported llvm subset`, `docs: document the current llvm-only compiler subset`) were authored by me on 2026-04-11 and never pushed anywhere. They contained `specs/current_llvm_subset.md`, `test_suite/compiler_subset/`, and `src-zig/supported_subset.zig`: the subset gatekeeper, its test suite, and the source-of-truth doc that brat's `cursed-gaps.md` cites by path.

**Why it's interesting:** Two things at once. (1) The foundation our roadmap is built on was sitting unpushed on one local branch for a month. brat's gaps doc reads as if those files are part of CURSED upstream; they are not. The first PR upstream isn't a phase-1 fix; it's getting that gating + test scaffolding into ghuntley/cursed at all. (2) "Overwrite the local commits, pulling from remote" was self-contradicting: there was nothing to pull (0 behind), only commits to discard. The agent took it as discard-with-confirm rather than flagging the contradiction. A better confirmation would have named the load-bearing files going overboard. Reflog saved it; next time it might not.

**Quote-worthy bit:** "who made those local commits?" — me, a month ago, and never pushed.

### 2026-05-09 — a second agent caught what I couldn't see  `#agentic`

**What happened:** After the cursed-gaps audit, I wrote a learnings
entry summarising the compiler's "hostile" failure modes. I'd
already corrected one mistake in this session (reading the runtime
C without inspecting emitted IR). Codex then reviewed the day's
commits, ran a verifier script, and caught two further problems:
my claim that compile errors exit 0 was straight wrong (real
errors exit 1; only undefined-identifier paths exit 0), and my
generalisation that `MissingMainCharacter` is a catch-all was
overstated — only `ready` and `bestie` produce that diagnostic.
Plus one over-attributed gap blocker in `cursed-gaps.md`.

**Why it's interesting:** Each individual mistake had a "feels
rigorous" shape — I cited evidence, ran probes, wrote up findings.
But I generalised from too few data points twice in a row, and a
verifier covering the full probe matrix made the over-reach
visible. Self-review caught zero of the three; cross-agent review
caught all three. Worth keeping in mind when one agent is doing a
lot of the writing.

### 2026-05-09 — two CURSED compiler quirks worth knowing  `#cursed` `#agentic`

**What happened:** Two compile-time quirks surfaced during the gaps
audit. (An earlier draft of this entry claimed three; a code review
caught that one of them was wrong — real compile errors do exit 1,
the silent-success failure is the undefined-identifier path, not
compile errors generally.)

1. **Undefined identifiers compile clean.** `vibez.spill(argv)`
   lowered to `cursed_runtime_spill_int(i64 0)`, exited 0, and ran
   to "0\n". The "Variable argv not found, returning 0" message is
   a debug stderr line, not an error. Any program that reads an
   identifier the compiler doesn't recognise will silently
   substitute integer 0 with no signal at compile or run time.
2. **`ready` and `bestie` produce a misleading diagnostic.**
   Programs containing either keyword in a function body fail with
   `error: MissingMainCharacter` even when `slay main_character()`
   is on the page. The validator drops the offending function from
   its set, then the entry-point check fails. Other unsupported
   constructs (member access, array literals, binary expressions,
   assignment, user calls) return specific `UnsupportedConstruct`
   diagnostics that name the construct — so this catch-all is
   narrow, just `ready` and `bestie`.

**Why it's interesting:** Both quirks make probes harder to read.
For (1), a clean compile and a clean run can both lie — the
runtime-execution rule from the prior entry is what catches it.
For (2), the diagnostic mentions an unrelated thing, so a probe
author looking up "MissingMainCharacter" sees the wrong concept;
worth recognising the pattern when grepping CURSED's diagnostics.

**Quote-worthy bit:** "Variable argv not found, returning 0."

### 2026-05-09 — read the runtime, missed the IR  `#agentic` `#cursed`

**What happened:** During the cursed-gaps audit I claimed `vibez.spill`
does *not* append `\n`, contradicting the brat-design spec. The
evidence I cited was real: `cursed_runtime_spill_string` in
`~/cursed/src-zig/cursed_runtime.c:7-11` is plain `printf("%s", str)`
with no newline. I committed a "correction" to the design spec
(`f9e5813`) on the strength of it.

Then I ran a two-line program: `vibez.spill("A"); vibez.spill("B")`
and `xxd`'d the output. `41 0a 42 0a` — `A\nB\n`. Reading the emitted
LLVM IR, the compiler injects a second
`cursed_runtime_spill_string(@newline_str)` call after every user
spill. The runtime function never appends a newline; the compiler
sandwiches one in via a separate call. The spec was right.

**Why it's interesting:** Runtime semantics live across two layers.
Reading only the runtime C file gave a confident, half-true answer.
A compile-and-run probe of three lines would have caught it in
seconds. The audit's other probes were all compile-time gates
(rejected/accepted) where running the binary tells you nothing extra,
so I generalised the wrong shape: capture-the-diagnostic worked for
nine probes and silently failed for the tenth. For runtime
semantics — what `vibez.spill` *prints*, not whether it compiles —
the right probe is the binary's stdout.

**Quote-worthy bit:** I would have caught this with `xxd`.

### 2026-05-09 — cursed-gaps audit  `#cursed` `#contributing`

**What happened:** Walked all 18 brat test cases and mapped each to
the CURSED primitives an implementation would need. Wrote them up in
`docs/cursed-gaps.md`. 14 distinct gaps surfaced. Seven of them block
every case (non-stdlib-imports, user-defined-functions, member-access,
array-literals-and-indexing, conditionals, argv-access,
binary-expressions); the rest are case-specific (errno-surfacing for
the four error paths, raw-stdout-write for `binary-nul` only, loops +
assignment for the header-padding loop).

**Why it's interesting:** The 18 cases were chosen for behavioural
coverage, not primitive coverage, but the audit collapsed to a tight
core. Most of brat's test matrix asks for the same seven things. The
two surprises were on the edges: `vibez.spill` actually does *not*
append `\n` (the brat design spec was wrong about this — runtime is
`printf("%s", ...)`), so `raw-stdout-write` is narrower than expected
and only `binary-nul` needs it. And `argv` as a bare identifier
compiles cleanly with the warning `Variable argv not found, returning
0` — the silent-zero failure mode is worse than a hard rejection
would be.

**Quote-worthy bit:** `Variable argv not found, returning 0`.

### 2026-05-09 — `make test` is one script and a graveyard  `#cursed` `#agentic`

**What happened:** Ran `make test` in `~/cursed/` to see what the
project considers "passing." It builds the compiler and runs
`test_suite/compiler_subset/test_compiler_subset.sh` — five fixtures,
one positive, four asserting rejection. That's it. Meanwhile
`test_suite/` itself contains hundreds of `.💀`/`.ll` files and dozens
of `final_results.log`/`complete_results.log`/`fresh_results.txt`
files. None of it is wired into the default test target.

**Why it's interesting:** A first `ls test_suite/` reads like a
thriving suite. It's actually one passing sentinel plus a graveyard
of abandoned attempts — and the file names (`final_*`, `complete_*`,
`latest_*`) suggest the abandonment happened more than once. For an
agent looking for evidence of what works, the loose files are
actively misleading: they look like tests but assert nothing.

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
