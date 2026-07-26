# cc-skill-usage

Retroactive usage analytics for [Claude Code](https://claude.com/claude-code) Skills.

It reads the JSONL transcripts Claude Code already writes under
`~/.claude/projects/` and tells you which Skills you actually invoke, how often,
when, and in which project. No hook to install ahead of time, no daemon. The
history is already on disk, this tool just reads it.

## Why

Claude Code has no built-in view of Skill usage. The only other dedicated tool
is hook-based, so it can only count invocations from the moment you install it,
never the history you already have. `cc-skill-usage` is transcript-based, so it
works backward over everything already recorded.

It counts **real invocations only**: a `tool_use` block whose `name == "Skill"`.
A skill merely named in a reply is not an invocation and is never counted. A
naive `grep` on a skill name overcounts by an order of magnitude (mentions in
prose, summaries, file paths). This tool does not fall for that.

## Install

Single file, Python 3.8+, standard library only. No dependencies.

```bash
curl -fsSL https://raw.githubusercontent.com/FlorianBruniaux/cc-skill-usage/main/cc-skill-usage \
  -o ~/.local/bin/cc-skill-usage
chmod +x ~/.local/bin/cc-skill-usage
```

Make sure `~/.local/bin` is on your `PATH`.

## Usage

```bash
cc-skill-usage                     # leaderboard: every skill, counts, projects, first/last seen
cc-skill-usage flow-lean           # detail for one skill: by project, by argument, daily histogram
cc-skill-usage --all recent 20     # the 20 most recent invocations, newest first
cc-skill-usage --since 7d          # only the last 7 days (also 24h, 2w, or a YYYY-MM-DD date)
cc-skill-usage --project myrepo    # filter by project: matches every worktree of that repo too
cc-skill-usage --include-subagents # also count invocations made inside subagents (off by default)
cc-skill-usage --show-context      # show the user message that preceded each invocation
cc-skill-usage --json              # machine-readable output for any command above
```

`--project` matches against both the session's cwd basename and the encoded
project directory, so one needle (e.g. `--project myrepo`) catches every
worktree of that repo, even though each worktree's cwd basename is its own
branch name (`fix-issue-123`, `feature-x`, ...) rather than the repo name.

### Example

```
$ cc-skill-usage
SKILL                              INVOC  PROJ       FIRST        LAST
---------------------------------  -----  ----  ----------  ----------
superpowers:brainstorming             18     8  2026-06-25  2026-07-22
tdd                                   11     6  2026-07-03  2026-07-24
flow-lean                              7     5  2026-07-23  2026-07-25
...

211 invocations across 69 skills.
```

Add `--show-context` to the leaderboard for a one-shot, every-skill recap that
also shows the last thing that triggered each skill:

```
$ cc-skill-usage --since 30d --show-context
SKILL                              INVOC  PROJ        LAST  PROJECT     LAST CONTEXT
----------------------------------  -----  ----  ----------  ----------  ----------------------------------------
critique-plan                          11     6  2026-07-23  app         @"system-architect" @"backend-architect"...
tdd                                    11     6  2026-07-24  app         Déjà le 2, les fix sécu
...
```

```
$ cc-skill-usage flow-lean
flow-lean: 7 invocations across 7 sessions

By project:
     2  msds-claude-plugin
     2  app
     1  starmapper
     1  florian-portfolio
     1  claude-code-ultimate-guide

By day:
  2026-07-23    3  ###
  2026-07-25    4  ####
```

## How it works

For every `*.jsonl` under `~/.claude/projects/`, each line is one transcript
record. The tool walks `record.message.content[]` and keeps the blocks where
`type == "tool_use"` and `name == "Skill"`. The skill name is `input.skill`
(sometimes namespaced, e.g. `cowork:update-releases`), the optional level is
`input.args`, the timestamp is the record `timestamp`, and the project is the
basename of the record `cwd`.

With `--show-context`, the tool also tracks the last `role: user` text message
seen before each invocation in the same transcript, to show what prompted it.
Tool results (file reads, command output) are stored as `role: user` messages
too and can be megabytes long, so any such record longer than 20KB or carrying
a `tool_result` block is skipped without full parsing rather than risking a
slow, memory-heavy scan on a large repo's transcripts.

Results are cached in `~/.cache/cc-skill-usage/index.json`, keyed by file mtime.
The first run parses everything (a few seconds for ~2000 sessions), later runs
reuse the cache and finish in well under a second. Only changed transcripts are
re-parsed.

## Configuration

Environment variables, all optional:

| Variable | Default | Purpose |
|----------|---------|---------|
| `CC_PROJECTS_DIR` | `~/.claude/projects` | where transcripts live |
| `CC_SKILL_USAGE_CACHE` | `~/.cache/cc-skill-usage` | cache directory |
| `CC_SKILL_USAGE_TIMING` | unset | when set, print scan time to stderr |

Flags: `--no-cache` (parse fresh, do not touch the cache), `--rebuild` (ignore
the cache on read but rewrite it).

## Schema note

The invocation signature (`tool_use` / `name == "Skill"` / `input.skill`) was
verified against real transcripts across several Claude Code versions. If a
future version changes it, the counts drop to zero rather than lie. Open an
issue if that happens.

## License

MIT. See [LICENSE](LICENSE).
