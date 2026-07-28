# Reality check prompt

Paste into a fresh Claude Code session at the root of any repo. No prior
context needed. Works on a CLI, a library, an MCP server, a web app, or a
docs-only repo.

The point is not a code review. The point is to make the project produce
real numbers about itself, then check every number its own documentation
claims against the one it actually produces.

---

## Your job

Audit this repository by running it, not by reading it. A finding that came
from reading the source and reasoning about it is a hypothesis. A finding
backed by a command you ran and its output is a fact. Report facts, and
label hypotheses as hypotheses.

Work through phases 0 to 7 below in order. Do not skip a phase because it
"looks fine" from a file listing.

## Phase 0 - What is this thing, and what does running it mean

Identify the artifact type and the single command that exercises it end to
end. A CLI has an entry point to invoke. A library has a test suite or a
smallest useful call. An MCP server has a tool to list and one to call. A
web app has a dev server and a page to load. A docs-only repo has links to
resolve and code blocks to execute.

State that command explicitly before continuing. If you cannot find one,
that is itself the first finding: the project has no way to demonstrate
itself, and everything below becomes unverifiable.

Then record the state of the working tree, because it decides what your
measurements mean. Run `git status --short` and note the current HEAD. If
anything is uncommitted, say what and stop treating the tree as the
published state: you are auditing someone's work in progress, and a wrong
number you find may already be fixed on their disk.

Someone may keep editing while you measure. Note the modification time of
every file you draw a finding from, and re-check it before you write the
report. Any finding whose file changed under you gets marked as such, with
the timestamp, rather than silently dropped or silently kept. State your own
writes explicitly too, so nobody has to guess which changes were yours.

## Phase 1 - Run it and capture real output

Execute the command. Capture what it actually prints, including errors,
warnings, and how long it took. Run it a second time to see whether warm
behavior differs from cold (caches, indexes, compiled artifacts).

If the project needs input data, use real data available on this machine
rather than a synthetic fixture. Synthetic input hides the failure modes
that only show up at real scale.

Record: exit code, wall time cold, wall time warm, output size, anything
printed to stderr.

## Phase 2 - Test every falsifiable claim in the docs

Read the README, and any CHANGELOG, docs site, llms.txt, or CLAUDE.md.
Extract every claim that can be proven false. Those are the ones with a
number, a version, a flag, a platform, a guarantee, or a comparison.

Examples of falsifiable claims: "runs in under 200ms", "zero dependencies",
"Python 3.8+", "19 extractors", "supports X, Y and Z", "60-90% reduction",
"472 tests", "works without configuration".

Examples of claims to skip: "fast", "developer-friendly", "powerful". They
cannot be tested, and arguing about them wastes the pass.

For each falsifiable claim, run the check. Collect the results in a table
with exactly these three columns, kept short enough to survive an 80-column
terminal:

| Claim | Measured | Verdict |
|---|---|---|

The file and line where the claim appears belongs in the finding that cites
it, not in this table. A fourth column of long paths wraps and shreds the
whole table.

This table goes in an appendix at the end of the report, not before the
findings. On a large repo it runs to thirty rows and buries the one thing
the reader needed to see.

Verdict is one of: confirmed, wrong, unverifiable-here (say why). A claim
that is off by a factor you would notice is a finding. A claim off in the
third decimal is not, do not pad the report with it.

Pay particular attention to counts that were true when written and drift
silently afterward: number of tests, number of templates, number of tools,
number of supported providers. Count them yourself with a command, do not
trust the number in the prose.

### Run the checker the repo already ships

Before building your own measurement, look for a script in the repo that
already checks the thing you are about to check: a `sync`, `resync`,
`verify`, `validate`, `check`, `doctor`, or `--check` mode. Run it in its
read-only form and compare its output to yours.

Agreement between your method and one written by someone else, from a
different angle, turns a finding from an argument into a fact. On a real
run this is what settled the strongest finding of an audit: an index of
line references was measured stale independently by the auditor and by the
repo's own resync script, both deriving the same corrected line number, with
the repo's script reporting 89 of 472 references still valid.

Disagreement is worth as much. If the repo's own checker says a thing is
fine and your measurement says otherwise, one of you is wrong about the
project, and finding out which is more valuable than either verdict alone.

A shipped checker that has never been run, or that cannot fail, is itself a
finding. Check whether it is wired into CI, and whether it can actually
return non-zero.

## Phase 3 - Index sync

List every file in the repo that a human or an LLM is meant to find. Then
list every place that claims to index them: the README link list, llms.txt,
a docs nav, a CLAUDE.md layout block, a plugin manifest, a package
`files` field, an MCP tool list.

Report anything present in the repo and absent from an index, and anything
listed in an index and absent from the repo. Broken internal links count.

This is where recently-added files hide. Something shipped two commits ago
is exactly what nobody added to the index.

## Phase 4 - Inventory versus actual use

When a repo declares a fleet of anything (skills, agents, plugins,
templates, rules, hooks, MCP tools, npm scripts, feature flags, cron jobs),
counting it is the easy half and phase 2 already did it. The question that
decides whether the fleet is an asset or a tax is what share of it ever
runs.

For each fleet, ask how many members have actually fired, and where that
would be recorded. Usually not in the repo: execution history lives in
transcripts, logs, analytics, CI run history, or a registry's download
stats. If you can reach that source, measure the ratio and report it. If
you cannot, say so and name the source that would answer it. Never
substitute the inventory count for the usage count and move on, because a
fleet of 139 with a drift of 2 is a trivial problem while a fleet of 139
where 17 ever fire is the most expensive thing in the repo.

For a Claude Code repo specifically, Skill invocations are recorded in the
transcripts under `~/.claude/projects/`, not in the repo:
`cc-skill-usage --project <repo-name> --include-subagents`.

Then look for the same entity declared under two names. A half-finished
rename (`tech-pr-feedback` and `tech:pr-feedback`, `TDD` and `tdd`) leaves
both spellings alive and splits every counter between them. An inventory
count returns a clean number that hides it completely, so this only shows up
when you list usage by exact name.

## Phase 5 - Leak and hygiene check

Run `git status --short` and `git ls-files`. For each untracked path, decide
explicitly: should it be committed, ignored, or deleted. Never leave it
undecided.

Then check what is already committed for things that should not be public:
absolute paths containing a username, real client or employer names in
example output, API keys or tokens, personal data in a generated report or
fixture, an internal URL. Grep for the machine's own username and home
directory across tracked files.

If the project generates output into a directory, check whether that
directory is ignored. Generated output usually carries the real names of
whoever ran it.

## Phase 6 - What the project cannot answer about itself

This is the phase that finds the gaps, so do not rush it.

Ask what a user would reasonably want to know that this project currently
cannot tell them, and what a maintainer would need that is not written
down. Consider the failure modes: what happens on empty input, on
malformed input, at ten times the current scale, on a machine without the
optional dependency, on a fresh clone with no cache.

Try at least three of those cases for real. An empty directory, a
deliberately malformed input, and the largest real input available on this
machine. Report what happened, including if it was fine.

Then look for the undocumented tradeoff: a place in the code where an
obvious-looking improvement would break something non-obvious. Those are
the changes a future contributor makes confidently and regrets. If you find
one, measure how often the current approach actually fails before writing it
down, and put the measurement in the note.

## Phase 7 - Report

Produce, in this order:

1. **What this project does**, in three sentences, written from what you
   observed running it, not from the README's own pitch.
2. **Findings, ranked by whether they mislead a user.** A CI gate that
   cannot fail outranks a wrong version number, which outranks a missing
   index entry, which outranks a style nit. Every finding names a file and a
   line or a command, and carries a measured number. A finding without one
   of those does not go in the list.
3. **What you fixed, and what you deliberately left alone with the reason.**
   Illustrative examples that drift, historical changelog entries, and
   cosmetic inconsistencies are usually correct to leave. Say so rather
   than silently skipping them.
4. **What you could not verify**, and what would be needed to verify it.
   Include anything the working-tree state made unmeasurable.
5. **Appendix: the claims table** from phase 2.

If the tree was dirty or changed during the audit, that goes at the very
top, before point 1, in three lines: what was uncommitted, what changed
while you worked and when, and what you wrote yourself. A reader who does
not know the tree moved cannot tell a stale finding from a live one.

### Merge findings that share one root cause

Before ranking, group the findings by what actually has to change to fix
them. Five wrong counts in a README are not five findings, they are one:
the README hardcodes counts that drift. Report the root cause as a single
entry and list the instances under it.

Splitting one cause into five entries inflates the count and pushes the
finding that matters down the page. If the top item on your list is a stale
number while a CI gate silently passes on every run, the ranking failed.

## Rules

Do not write a finding you have not run a command to support.

Do not recommend adding tests, CI, or a linter as a finding unless you first
show a concrete bug that would have been caught. "No test suite" is a fact
about the repo, not a discovery.

Do not fix illustrative example output whose numbers drift with time. Say
that it drifts and move on.

One root cause is one finding, however many places it shows up. Count the
fixes needed, not the symptoms observed.

Prefer a second independent method over a second look at your own. Running
the repo's own checker, or a from-scratch pipeline built differently, beats
re-reading your first measurement.

If a claim in the docs turns out correct, say so explicitly. A report that
only lists problems hides the fact that most of the project holds up, and
that is information too.

When a limitation you found never actually fires on real data, measure how
often it fires, then decide where it belongs. A risk that never
materializes is maintainer context, not a user-facing caveat.
