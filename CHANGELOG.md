# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project adheres to
semantic versioning.

## [0.2.0] - 2026-07-26

### Added
- `--show-context`: displays the last user message preceding each invocation,
  in the per-skill detail view and in `--all recent`. Answers "in what context
  was this skill actually used".

### Fixed
- `--project` now also matches the encoded project directory, not just the
  cwd basename. Repos worked from git worktrees (each worktree's cwd basename
  is its own branch name, e.g. `fix-issue-123`, never the repo name) were
  invisible to the old filter: only the main worktree ever matched. Verified
  on a real 55-worktree repo, going from 1 matched project label to 17.
- Fixed an OOM crash (SIGKILL, exit 137) triggered on large repos. Tool
  results (file reads, command output) are stored as `role: user` messages in
  the transcript, same as real prompts, and can be megabytes long; the
  context-capture code was fully `json.loads`-ing every one of them. Any
  `role: user` record over 20KB or carrying a `tool_result` block is now
  skipped before parsing. Verified: peak memory dropped from OOM to ~70MB on
  the same repo.
- Fixed a related `NameError` that could crash the parser entirely if a huge
  tool-result line happened to contain the literal substring `"type":"user"`
  without actually being a top-level user record.
- Tightened the Skill-invocation substring pre-filter from bare `"Skill"` to
  `"name":"Skill"`. The loose version matched prose mentioning the word
  "Skill" inside a large tool result (e.g. a file dump of a `SKILL.md`),
  defeating the size guard above on exactly the files most likely to need it.

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
