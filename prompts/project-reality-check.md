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

Work through the six phases below in order. Do not skip a phase because it
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

For each falsifiable claim, run the check and put it in a table:

| Claim | Where it appears | Measured | Verdict |
|---|---|---|---|

Verdict is one of: confirmed, wrong, unverifiable-here (say why). A claim
that is off by a factor you would notice is a finding. A claim off in the
third decimal is not, do not pad the report with it.

Pay particular attention to counts that were true when written and drift
silently afterward: number of tests, number of templates, number of tools,
number of supported providers. Count them yourself with a command, do not
trust the number in the prose.

## Phase 3 - Index sync

List every file in the repo that a human or an LLM is meant to find. Then
list every place that claims to index them: the README link list, llms.txt,
a docs nav, a CLAUDE.md layout block, a plugin manifest, a package
`files` field, an MCP tool list.

Report anything present in the repo and absent from an index, and anything
listed in an index and absent from the repo. Broken internal links count.

This is where recently-added files hide. Something shipped two commits ago
is exactly what nobody added to the index.

## Phase 4 - Leak and hygiene check

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

## Phase 5 - What the project cannot answer about itself

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

## Phase 6 - Report

Produce, in this order:

1. **What this project does**, in three sentences, written from what you
   observed running it, not from the README's own pitch.
2. **The claims table** from phase 2.
3. **Findings, ranked by whether they mislead a user.** A wrong number in
   the README outranks a missing index entry, which outranks a style nit.
   Every finding names a file and a line or a command, and carries a
   measured number. A finding without one of those does not go in the list.
4. **What you fixed, and what you deliberately left alone with the reason.**
   Illustrative examples that drift, historical changelog entries, and
   cosmetic inconsistencies are usually correct to leave. Say so rather
   than silently skipping them.
5. **What you could not verify**, and what would be needed to verify it.

## Rules

Do not write a finding you have not run a command to support.

Do not recommend adding tests, CI, or a linter as a finding unless you first
show a concrete bug that would have been caught. "No test suite" is a fact
about the repo, not a discovery.

Do not fix illustrative example output whose numbers drift with time. Say
that it drifts and move on.

If a claim in the docs turns out correct, say so explicitly. A report that
only lists problems hides the fact that most of the project holds up, and
that is information too.

When a limitation you found never actually fires on real data, measure how
often it fires, then decide where it belongs. A risk that never
materializes is maintainer context, not a user-facing caveat.
