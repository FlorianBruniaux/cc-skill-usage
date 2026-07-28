# Changelog

`cc-skill-usage` is a single-file CLI that reads Claude Code's own JSONL
transcripts under `~/.claude/projects/` and reports which Skills you actually
invoked: counts, timing, projects, and (with `--show-context`) the message
that triggered each one. All notable changes are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/), and the project
adheres to semantic versioning.

## [Unreleased]

### Added
- `prompts/scenario-tour.md`: a ready-to-paste prompt that smoke-tests every
  scenario in `EXAMPLES.md` against real data and flags any drift between
  documented and actual behavior.
- `prompts/deep-dive-report.md`: a ready-to-paste prompt for a multi-agent
  session that crosses `cc-skill-usage` usage data with the `eval-skills`
  quality audit, producing quadrant tables (high/low usage x high/low
  quality) and impact-ranked, verified fixes.

### Fixed
- `llms.txt` and the repository layout in `CLAUDE.md` both still listed only
  the four original files. `EXAMPLES.md`, `prompts/`, and the bundled
  `skill-usage-report` Skill had shipped without being added to either index.
  `llms.txt` exists specifically to be a complete index for an LLM reading
  the repo, so missing two documents was a defect in the file's only job.
  Both updated, and `CLAUDE.md` now states the three-index rule so the next
  doc addition does not drift the same way.
- README claimed warm runs finish "well under a tenth of a second". Measured
  on the machine the claim came from, the real figure is about 0.18s across
  roughly 2000 sessions, since a warm run still stats every transcript to
  check its mtime. Corrected to ~0.2s with the reason stated.
- `.gitignore` covered neither `.idea/` (JetBrains project files) nor
  `reports/`, the output directory `prompts/deep-dive-report.md` writes into.
  A generated report carries the real project and skill names of whoever ran
  it, so committing one publishes someone's private workflow inventory.
  Both ignored.

## [0.2.3] - 2026-07-26

### Added
- `EXAMPLES.md`: scenarios matched to the exact command that answers them
  (monthly recap, one repo versus everything else, scripting with `--json`,
  cross-checking a count that looks wrong), linked from the README.
- `.claude/skills/skill-usage-report/`: a Skill that runs and interprets
  `cc-skill-usage` output, including the cross-verification step against an
  independent `grep`+`jq` pipeline whenever a count looks off, and the known
  blind spots to disclose rather than paper over.

### Fixed
- `--help` for `--show-context` still described the old fixed-width table
  layout ("an extra column on the leaderboard") after it was replaced by a
  block-per-skill layout in 0.2.2. Wording corrected to match the actual
  output.

## [0.2.2] - 2026-07-26

### Fixed
- The `--show-context` leaderboard was unreadable in a real terminal: skill
  name, counts, a project name, and a free-text context crammed into one
  fixed-width table row either truncated the context mid-word or wrapped
  unpredictably depending on terminal width, confirmed against real output
  during use. Replaced with a block-per-skill layout (one stats line, one
  indented context line) that adapts to the actual terminal width via
  `shutil.get_terminal_size()` instead of assuming a fixed one.

## [0.2.1] - 2026-07-26

### Fixed
- `KeyError: 'context'` crash for anyone with a cache built by 0.1.x. The
  event dict grew `context` and `repo_hint` fields in 0.2.0 but the cache
  schema version was never bumped, so an existing `~/.cache/cc-skill-usage/`
  from before the update kept getting reused as-is (still keyed only by file
  mtime, which hadn't changed) and crashed on the missing keys the moment
  `--show-context` touched them. `CACHE_SCHEMA` bumped to 2 so any pre-0.2.0
  cache is discarded and rebuilt on the next run instead of crashing.
- `--show-context` was silently ignored on the plain leaderboard view (no
  skill argument, no `--all`): the flag only reached `view_detail` and
  `view_recent`, so running `cc-skill-usage --since 30d --show-context` printed
  the exact same table as without the flag, no error, no hint. Now the
  leaderboard itself grows a `LAST CONTEXT` column (and `PROJECT`) showing the
  most recent invocation's preceding user message for every skill in one
  table, so a full exhaustive per-skill context recap no longer requires
  querying each skill one at a time via the detail view.

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
