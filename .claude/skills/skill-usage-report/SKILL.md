---
name: skill-usage-report
description: >
  Analyzes Claude Code Skill invocation history via cc-skill-usage: leaderboards,
  per-skill drilldowns, project and time filters, triggering context, and a
  mandatory cross-verification step whenever a count looks surprising.
when_to_use: >
  Use when the user asks which Skills they use most, how often a specific
  skill fires, usage over a time window or scoped to one project, wants a
  recap or report of Skill invocations, or is suspicious that a count from
  cc-skill-usage looks too low or too high.
argument-hint: "[skill-name] [--since 30d] [--project name]"
license: MIT
allowed-tools: Bash
effort: medium
---

# Skill Usage Report

Runs and interprets `cc-skill-usage` (this repo's own CLI) to answer
questions about Skill usage. Read `README.md` and `EXAMPLES.md` in this repo
first if either is unfamiliar, they hold the full flag reference and the
scenario-to-command mapping this skill draws from.

## Picking the right command

Match the question to the scenario in `EXAMPLES.md` rather than improvising
flags: a monthly recap is `--since 30d --show-context`, a single skill's
health check is `<skill-name> --show-context`, a repo-versus-everything-else
comparison needs two `--json` runs diffed by skill name, and so on. Default
to `--show-context` whenever the user's question includes "why", "when", or
"in what context": counts alone rarely answer that.

## The one non-negotiable step: verify before reporting a surprising number

If a count is unexpectedly low, unexpectedly high, or contradicts the user's
own memory of how much they used something, do not report it as-is. Cross-
check it independently before presenting a verdict:

```bash
# raw mentions (expect this far higher, it includes prose, files, summaries)
grep -rl 'skill-name' ~/.claude/projects --include="*.jsonl" | wc -l

# real invocations, independent of cc-skill-usage's own parsing code
grep -rh '"name":"Skill"' ~/.claude/projects --include="*.jsonl" \
  | jq -r '.message.content[]? | select(.type=="tool_use" and .name=="Skill") | .input.skill' \
  | grep -c '^skill-name$'
```

If the independent pipeline matches `cc-skill-usage`'s own count, the tool is
right and the surprise is the invocation-vs-mention gap (measured at 212x on
real data during this tool's own development, see `README.md`), not a bug.
State that plainly, with both numbers, rather than either blindly trusting
or blindly doubting the first result.

## Known blind spots to disclose, not paper over

State these when relevant instead of letting a report imply more precision
than the data supports:

- Typed slash-command invocations may be under-represented versus
  natural-language-triggered ones; the invocation signature this tool
  matches is a `Skill` tool call, and that path is well verified, but a
  purely-typed `/skill-name` path has fewer confirmed clean examples.
- `--show-context` occasionally reports "(no preceding user message found)"
  when the real preceding message was a large tool result, skipped by design
  to avoid an OOM failure mode. That gap affects the context line only,
  never the invocation count itself.
- Scanning a live session's own transcript while investigating a skill can
  make raw text-mention counts (never real invocation counts) pick up an
  echo of your own prior grep output.

## Output shape

Lead with the verdict (the number, and whether it was cross-checked), then
the supporting breakdown (by project, by day, sample context), matching the
density expected for a factual/debug answer: direct, no hedging once
verified, but never state a surprising number as fact without having run the
verification step above.
