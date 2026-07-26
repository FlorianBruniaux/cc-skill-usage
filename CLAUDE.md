# cc-skill-usage - Project Context

## What this is

A single-file Python CLI. It reads Claude Code's own JSONL transcripts under
`~/.claude/projects/` and reports Skill invocation analytics: counts, timing,
project breakdown, and the message that triggered each call. Retroactive by
design, it reads history already on disk instead of requiring a hook
installed ahead of time.

## Repository layout

```
cc-skill-usage    # the entire tool, one file, no package, no build step
README.md         # usage reference for humans
CHANGELOG.md      # every fix/feature with the bug it addressed and the verification
llms.txt          # compact index for LLM consumption (llmstxt.org format)
LICENSE           # MIT
```

There is no `src/`, no test suite directory, no CI config. Keep it that way
unless a real need forces otherwise: the entire value of this tool is that it
is one file you can `curl` and run.

## The one invariant that matters more than any feature

A Skill is invoked only when a transcript record's
`message.content[]` contains a block with `type == "tool_use"` and
`name == "Skill"`. The skill name lives in `input.skill`. Nothing else counts,
not a mention in prose, not a file path, not a human typing the skill's name
in a sentence.

This was verified twice, independently, in the same session that built this
tool: once by the Python parser, once by a from-scratch `grep '"name":"Skill"'
| jq '.message.content[]? | select(...) | .input.skill'` pipeline. Both
returned identical counts on the same data. If you touch the parsing logic in
`cc-skill-usage`, re-run that same cross-check before trusting a new number.
Do not assume a plausible-looking count is correct just because the code ran
without error.

## Hard-won lessons already baked into the code

- **`role: user` messages are not all human prompts.** Tool results (file
  reads, command output) are stored as `role: user` records too, and can be
  megabytes long. An early version of the context-capture feature fully
  `json.loads`-ed every one of them looking for a short prompt, and it OOM
  crashed scanning a large repo (SIGKILL, exit 137). Fixed by skipping any
  `role: user` record over 20KB or containing a `tool_result` block before
  parsing. If you touch `parse_file()`, keep that guard, and test against the
  largest real repo you can find, not a small synthetic one.
- **A loose substring pre-filter defeats its own size guard.** The original
  fast-path check for `"Skill"` anywhere in a line matched prose mentioning
  the word inside a large tool result (a file dump of a `SKILL.md`, for
  instance), which is exactly the kind of line the size guard above exists to
  skip. Tightened to `"name":"Skill"`, the actual JSON shape of a real
  invocation. Keep pre-filters anchored to real structure, not to a word that
  can appear in prose.
- **`cwd` basename is not a stable project identifier under git worktrees.**
  Each worktree's cwd basename is its own branch name
  (`fix-issue-123`, `feature-x`), never the repo name. `--project` matches
  against both that basename and the encoded top-level directory name under
  `~/.claude/projects/` (which does stay tied to the repo), so one needle
  catches every worktree. Verified on a real 55-worktree repo: 1 matched
  label before the fix, 17 after.
- **Cache entries need a schema version, not just an mtime key.** The event
  dict grew fields (`context`, `repo_hint`) after the first release, but the
  cache schema constant was not bumped at the same time, so an existing cache
  built by an older version kept being reused as-is and crashed on the
  missing keys the first time a newer code path read them. `CACHE_SCHEMA` in
  the source exists specifically so a shape change invalidates old cache
  entries instead of crashing on them. Bump it whenever the event dict shape
  changes, not just when you feel like it might matter.
- **A free-text field does not survive a fixed-width table column.** The
  `--show-context` leaderboard was first built as one strict table row per
  skill; a context string's length varies too much to fit any fixed column
  width, so it either truncated mid-word or wrapped badly depending on the
  terminal. Replaced with a block-per-skill layout (a stats line, then an
  indented context line), sized to the real terminal width via
  `shutil.get_terminal_size()`. If you add another free-text field to a
  table-style view, expect the same failure and reach for a block layout
  before a table.

## Conventions

- English throughout: code, comments, README, CHANGELOG, commit messages.
  This is a small public tool meant to be read by anyone, not a private repo.
- No em dash in any prose (commit messages, README, CHANGELOG). Comma,
  parenthesis, or restructure the sentence instead.
- No new dependency, ever, without a very good reason stated in the commit
  message. The entire pitch of this tool is "one file, `curl` it, run it".
  Standard library only.
- Every fix in CHANGELOG.md states the concrete bug, not just "improved X":
  what broke, why, and how it was verified after the fix. Keep that bar.
- Commits are created only when explicitly asked; this repo has no remote
  configured yet, so nothing gets pushed without an explicit request either.
