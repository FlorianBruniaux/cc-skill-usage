# cc-skill-usage

<table>
  <tr>
    <td width="64">
      <a href="https://www.florian.bruniaux.com/about/?utm_source=github&amp;utm_medium=readme&amp;utm_campaign=cc-skill-usage"><img src="https://cc.bruniaux.com/author.png" width="56" height="56" alt="Florian Bruniaux" /></a>
    </td>
    <td>
      <strong><a href="https://www.florian.bruniaux.com/about/?utm_source=github&amp;utm_medium=readme&amp;utm_campaign=cc-skill-usage">Florian BRUNIAUX</a></strong> &middot; AI Founding Engineer @ <a href="https://methode-aristote.fr/">Méthode Aristote</a><br />
      13 years from developer to CTO / VP Eng &middot; <a href="https://www.florian.bruniaux.com/blog/?utm_source=github&amp;utm_medium=readme&amp;utm_campaign=cc-skill-usage">Blog &#8599;</a> &middot; <a href="https://www.florian.bruniaux.com/projects/?utm_source=github&amp;utm_medium=readme&amp;utm_campaign=cc-skill-usage">Projects &#8599;</a>
    </td>
  </tr>
</table>

Retroactive usage analytics for [Claude Code](https://claude.com/claude-code) Skills.

`cc-skill-usage` reads the JSONL transcripts Claude Code already writes to
`~/.claude/projects/` and tells you which Skills you actually invoke, how
often, when, in which project, and what prompted each call. There is nothing
to install ahead of time and no daemon to run. The history is already sitting
on disk, this tool just reads it.

```
$ cc-skill-usage
SKILL                                       INVOC  PROJ       FIRST        LAST
------------------------------------------  -----  ----  ----------  ----------
superpowers:brainstorming                      20    10  2026-06-25  2026-07-26
critique-plan                                  11     6  2026-06-29  2026-07-23
tdd                                            11     6  2026-07-03  2026-07-24
superpowers:systematic-debugging               11     5  2026-07-01  2026-07-17
plaud-summarize-exchange                       10     7  2026-06-16  2026-07-26
...

216 invocations across 70 skills.
```

## Why this exists

Claude Code has no built-in view of Skill usage. The only other dedicated
tool found in the ecosystem is hook-based, meaning it can only start counting
invocations from the moment you install it. It cannot see the history you
already have. `cc-skill-usage` is transcript-based instead, so it works
backward over everything Claude Code already recorded, no setup required
before the fact.

## What counts as an invocation

This is the part that took the most care to get right, so it deserves its
own section rather than a footnote.

A Skill is invoked when the model calls the `Skill` tool: a `tool_use` block
with `name == "Skill"` and the skill name in `input.skill`. That is the only
thing this tool counts. A skill merely named in a reply, quoted in a file, or
typed by a human in passing ("go read the flow-lean skill") is not an
invocation, and none of those are counted.

This distinction matters more than it sounds. Across real usage data checked
while building this tool, one skill showed 2330 raw text mentions of its name
across a project's transcripts, against 11 confirmed real invocations, a
212x gap. A naive `grep <skill-name>` on your transcripts will systematically
overcount by that kind of margin, sometimes by an order of magnitude,
sometimes by two. `cc-skill-usage` does not fall into that trap: every count
was cross-checked against an independent `grep`+`jq` pipeline built from
scratch, matching exactly, invocation for invocation.

## Install

Single file, Python 3.8+, standard library only, no dependencies.

```bash
curl -fsSL https://raw.githubusercontent.com/FlorianBruniaux/cc-skill-usage/main/cc-skill-usage \
  -o ~/.local/bin/cc-skill-usage
chmod +x ~/.local/bin/cc-skill-usage
```

Make sure `~/.local/bin` is on your `PATH`. To try it without installing
anything, clone the repo and run `./cc-skill-usage` directly.

## Usage

```bash
cc-skill-usage                      # leaderboard: every skill, counts, projects, first/last seen
cc-skill-usage flow-lean            # detail for one skill: by project, by argument, daily histogram
cc-skill-usage --all recent 20      # the 20 most recent invocations, newest first
cc-skill-usage --since 7d           # only the last 7 days (also 24h, 2w, or a YYYY-MM-DD date)
cc-skill-usage --project myrepo     # filter by project, catches every worktree of that repo too
cc-skill-usage --include-subagents  # also count invocations made inside subagents (off by default)
cc-skill-usage --show-context       # show what triggered each invocation
cc-skill-usage --json               # machine-readable output for any command above
```

See [EXAMPLES.md](EXAMPLES.md) for concrete scenarios (a monthly recap, one
repo versus everything else, scripting with `--json`, cross-checking a
count that looks wrong) matched to the exact command that answers them.

Ready-to-paste prompts for a fresh Claude Code session live in
[prompts/](prompts/). Two of them are about this tool:
[`scenario-tour.md`](prompts/scenario-tour.md) smoke-tests every scenario in
EXAMPLES.md against real data, and
[`deep-dive-report.md`](prompts/deep-dive-report.md) runs a multi-agent
audit crossing usage data with the `eval-skills` quality audit, producing a
report with quadrant tables and impact-ranked fixes.

The third, [`project-reality-check.md`](prompts/project-reality-check.md),
is project-agnostic: paste it at the root of any repo, in any language, and
it audits that repo by running it rather than reading it, then checks every
falsifiable claim in its docs against a measured number. It lives here
because this repo is where it was written, not because it needs
`cc-skill-usage` to work.

### Filtering by project, including worktrees

`--project` matches against both the session's cwd basename and the encoded
project directory Claude Code stores under `~/.claude/projects/`. That second
match matters if you work from git worktrees: each worktree's cwd basename is
its own branch name (`fix-issue-123`, `feature-x`, ...), never the repo name,
so a plain basename filter would only ever catch your main worktree. One
needle like `--project myrepo` catches every worktree of that repo instead.
Verified on a real 55-worktree repo: 1 matched project label before this,
17 after.

### The exhaustive per-skill recap

Add `--show-context` to the plain leaderboard for a one-shot table covering
every skill, including what last triggered each one:

```
$ cc-skill-usage --since 30d --show-context
critique-plan  (11 invocations, 6 projects, last 2026-07-23, in app)
  -> @"system-architect (agent)" @"backend-architect (agent)" /critique-plan
tdd  (11 invocations, 6 projects, last 2026-07-24, in app)
  -> Déjà le 2, les fix sécu
...
```

One block per skill, not a rigid table row: a skill name and a free-text
context vary too much in length to survive fixed-width columns without
truncating mid-word or wrapping badly. This layout adapts to your terminal
width instead of fighting it.

### Digging into one skill

```
$ cc-skill-usage flow-lean
flow-lean: 8 invocations across 8 sessions

By project:
     2  msds-claude-plugin
     2  app
     1  starmapper
     1  florian-portfolio
     1  simplitravaux
     1  claude-code-ultimate-guide

By day:
  2026-07-23    3  ###
  2026-07-25    4  ####
  2026-07-26    1  #
```

Add `--show-context` here too for the last 20 invocations of that one skill,
each with the session it happened in and the user message that preceded it.

## How it works

For every `*.jsonl` under `~/.claude/projects/`, each line is one transcript
record. The tool walks `record.message.content[]` and keeps the blocks where
`type == "tool_use"` and `name == "Skill"`. The skill name is `input.skill`
(sometimes namespaced, e.g. `cowork:update-releases`), the optional level or
argument is `input.args`, the timestamp is the record's own `timestamp`, and
the project is the basename of the record's `cwd`.

With `--show-context`, the tool also tracks the last `role: user` text
message seen before each invocation in the same transcript, to show what
prompted it. This required a real correction during development: tool
results (file reads, command output) are stored as `role: user` messages
too, and can be megabytes long. An early version fully parsed every one of
them looking for a short prompt that was never in there, and it got OOM-killed
scanning a large repo. Any `role: user` record over 20KB, or one carrying a
`tool_result` block, is now skipped before `json.loads` runs on it. Verified
on the repo that triggered the crash: peak memory went from an OOM kill to
about 70MB.

Results are cached in `~/.cache/cc-skill-usage/index.json`, keyed by file
mtime. The first run parses everything (a few seconds across roughly 2000
sessions on the machine this was built on), later runs reuse the cache and
land around 0.2s on that same set. Only changed transcripts get re-parsed,
so the warm number tracks how many sessions you have, not how much history
is in them. The cache carries a schema version, so an update that changes what
gets stored per event invalidates old cache entries automatically instead of
crashing on a missing field.

## Configuration

Environment variables, all optional:

| Variable | Default | Purpose |
|----------|---------|---------|
| `CC_PROJECTS_DIR` | `~/.claude/projects` | where transcripts live |
| `CC_SKILL_USAGE_CACHE` | `~/.cache/cc-skill-usage` | cache directory |
| `CC_SKILL_USAGE_TIMING` | unset | when set, print scan time to stderr |

Flags: `--no-cache` parses everything fresh and does not touch the cache;
`--rebuild` ignores the cache on read but rewrites it afterward.

## Known limitations

Worth stating plainly rather than discovering by surprise.

- **Slash-command invocations may leave a thinner trail.** A skill invoked by
  the model deciding to call the `Skill` tool always produces the exact
  signature this tool looks for. Typing a skill's slash command directly
  (`/critique-plan ...`) is comparatively rare in the data checked so far, and
  the one clean example available was contaminated by this very tool's own
  test runs quoting it back into its own transcript. If your workflow leans
  heavily on typed slash invocations rather than natural-language triggers,
  spot-check a skill you use that way against your own memory before trusting
  the count blindly.
- **Context capture has a size ceiling.** Any `role: user` record over 20KB,
  or one containing a `tool_result` block, is skipped when looking for the
  triggering prompt, by design, to avoid the OOM failure mode described
  above. The practical effect: `--show-context` occasionally reports
  "(no preceding user message found)" when the real preceding message was a
  large tool result rather than genuinely missing. The skill invocation
  itself is still counted correctly either way, only the context line is
  affected.
- **Scanning your own live session pollutes raw text-mention counts, not
  real ones.** If you grep your transcripts for a skill's name while a
  session discussing that skill is still open, your own command output gets
  written back into that session's transcript, and the next scan will find
  its own echo. This inflates naive substring counts (already an unreliable
  measure on their own, see above) but never affects the `tool_use`-based
  invocation count, which only matches a precise JSON shape that ordinary
  prose or command output does not reproduce.

## Contributing

Single file, no build step, no dependencies. Read `cc-skill-usage` top to
bottom, it is short enough to hold in your head in one sitting. Pull requests
that add a feature should include the real transcript pattern it relies on
and a way to verify the count against an independent method, in the same
spirit as the two checks above.

<!-- BEGIN GENERATED RELATED PROJECTS -->
<!-- Source: https://github.com/FlorianBruniaux/FlorianBruniaux/blob/main/ecosystem/projects.json; project: cc-skill-usage -->
## Explore the ecosystem

These projects extend the workflow without duplicating this tool:

- **Search with [CC-Sessions](https://github.com/FlorianBruniaux/cc-sessions)**: explore the sessions that contain the measured invocations.
- **Visualize with [CCBoard](https://github.com/FlorianBruniaux/ccboard)**: pair specialist CLI analysis with a broader session dashboard.
- **Validate with [flow-lean](https://github.com/FlorianBruniaux/flow-lean)**: verify empirically that the advertised skill is actually invoked.

[Browse the complete open-source galaxy](https://github.com/FlorianBruniaux#open-source-galaxy)
<!-- END GENERATED RELATED PROJECTS -->

## License

MIT. See [LICENSE](LICENSE).
