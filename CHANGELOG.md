# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project adheres to
semantic versioning.

## [0.1.0] - 2026-07-26

First release.

### Added
- Leaderboard view: every skill with invocation count, distinct projects, and
  first/last seen dates.
- Per-skill detail view: breakdown by project, by argument, and a daily
  histogram.
- `--all recent N`: the N most recent invocations, newest first.
- `--since` time filter (`7d`, `24h`, `2w`, or an ISO date).
- `--project` substring filter on the cwd basename.
- `--include-subagents` to also count subagent invocations (off by default).
- `--json` machine-readable output on every view.
- mtime-keyed cache in `~/.cache/cc-skill-usage/`, cold scan of ~2000 sessions
  in a few seconds, warm runs under 0.1s.

### Verified
- Invocation signature confirmed against real transcripts: a `tool_use` block
  with `name == "Skill"` and the skill in `input.skill`. Counts real
  invocations, never prose mentions.
