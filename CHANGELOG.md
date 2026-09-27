# Changelog

`cc-skill-usage` is a single-file CLI that reads Claude Code's own JSONL
transcripts under `~/.claude/projects/` and reports which Skills you actually
invoked: counts, timing, projects, and (with `--show-context`) the message
that triggered each one. All notable changes are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/), and the project
adheres to semantic versioning.

## [Unreleased]

### Added
- Codex skill loading through `load --skill NAME --path PATH`, with local
  instrumented events kept separate from native Claude invocations and
  optional inferred Codex reads. Reports support `--host claude|codex|all`.

### Fixed
- The loader accepts project skills from the current Git checkout, including
  linked worktrees, and installed plugin caches. It still rejects sibling
  repositories and symlinks escaping the checkout; `CC_SKILL_ROOTS` remains
  an exclusive override. Sixteen isolated tests cover loading and evidence
  boundaries, including eight project-root regressions. Valid JSON lines that are not
  objects are skipped instead of crashing the instrumented-event reader.


### Added
- `prompts/scenario-tour.md`: a ready-to-paste prompt that smoke-tests every
  scenario in `EXAMPLES.md` against real data and flags any drift between
  documented and actual behavior.
- `prompts/deep-dive-report.md`: a ready-to-paste prompt for a multi-agent
  session that crosses `cc-skill-usage` usage data with the `eval-skills`
  quality audit, producing quadrant tables (high/low usage x high/low
  quality) and impact-ranked, verified fixes.
- `prompts/project-reality-check.md`: a project-agnostic audit prompt, the
  only file here that has nothing to do with `cc-skill-usage`. Paste it at
  the root of any repo, in any language, and it audits that repo by running
  it rather than reading it: extract every falsifiable claim from the docs
  and measure it, check that every file is reachable from every index, look
  for leaked personal data in tracked files, and probe what the project
  cannot answer about itself (empty input, malformed input, largest real
  input). Written while auditing this repo, where it caught a wrong perf
  figure, two stale indexes, and an ignorable-looking directory holding real
  project names.

### Changed
- `prompts/project-reality-check.md` revised after its first run on an
  outside repo (a Next.js monolith with 1213 test files and a 139-skill
  fleet). Three defects showed up in the report it produced, all fixed in
  the prompt rather than worked around by hand.

  The claims table came before the findings and ran to 35 rows, burying the
  single finding that mattered (a CI gate that could not fail, since a
  `require()` in an ESM package threw, got caught, and exited 0 with a green
  check). The table now goes in an appendix, and drops from four columns to
  three: the file and line move into the finding that cites them, since a
  column of long paths wraps and shreds the table on an 80-column terminal.
  That is the same failure the `--show-context` leaderboard hit in 0.2.2.

  Twelve findings were reported where six root causes existed: five separate
  entries for wrong counts in a README are one entry, "the README hardcodes
  counts that drift". A merge rule now runs before ranking, and the rules
  section states it as "one root cause is one finding, however many places
  it shows up".

  A new phase 4 separates inventory from actual use. The report counted a
  139-skill fleet and flagged that the number had drifted by 2, never asking
  how many of the 139 ever fire. Measured with this tool on the same repo:
  102 invocations across 41 distinct skills, of which 17 look project-local.
  A fleet of 139 with a drift of 2 is trivial; a fleet of 139 where 17 fire
  is the most expensive thing in the repo. The phase also asks for the same
  entity declared under two names, since a half-finished rename
  (`tech-pr-feedback` and `tech:pr-feedback`, `TDD` and `tdd`, both found in
  that data) splits every counter while an inventory count still returns a
  clean number.

  Revised again after a second run, on a documentation corpus shipping an
  MCP server to npm. Two behaviors the auditor produced on its own, worth
  making mandatory rather than leaving to luck.

  Phase 0 now records the working tree state. That run measured a repo
  someone else was editing live: four files changed mid-audit and two
  findings were fixed under it. It handled that by opening with a timestamped
  caveat and marking the affected findings, which is the only reason its
  numbers stayed interpretable. The prompt now requires the `git status`
  check up front, a re-check of every file a finding rests on before writing
  the report, and an explicit list of the auditor's own writes. A dirty-tree
  note goes above everything else in the report, since a reader who does not
  know the tree moved cannot tell a stale finding from a live one.

  Phase 2 now requires running the checker the repo already ships before
  building your own. That run's strongest finding, an index of line
  references stale enough that the published npm package returned unrelated
  prose for a documented lookup, was settled because the auditor's own
  matching and the repo's `resync-reference-yaml.py` derived the same
  corrected line number from different angles, the repo's script reporting 89
  of 472 references still valid. Agreement across two independent methods is
  the same discipline this tool applies to its own counts. Disagreement is
  called out as equally informative, and a shipped checker that cannot fail
  or was never wired into CI is named as a finding in its own right.

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
