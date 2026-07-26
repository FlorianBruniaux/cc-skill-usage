# Deep-dive skill usage + quality report

Paste this into a fresh Claude Code session for a thorough, multi-agent
report crossing Skill usage data with Skill quality data: what is used and
well-built, what is used but poorly built, what is well-built but rarely
triggered, and what should probably be retired or merged. Produces tables
and actionable, impact-ranked fixes. No prior context needed, this is
self-contained.

Use the Workflow tool to parallelize this: usage analysis across time
windows and projects can run concurrently with the quality audit, and every
finding that goes into the executive summary should survive an independent
verification pass before being reported as fact.

---

## Context

Two tools and one skill are already installed and available on this
machine:

- `cc-skill-usage` (CLI, on PATH): reads Claude Code's own JSONL transcripts
  under `~/.claude/projects/` and reports Skill invocation counts, timing,
  project breakdown, and triggering context. Source and full docs at
  `~/Sites/perso/cc-skill-usage/` (`README.md`, `EXAMPLES.md`, `CLAUDE.md`).
- `eval-skills` (a Skill, invoke via the Skill tool): audits every skill's
  frontmatter completeness, `effort` level appropriateness, `allowed-tools`
  scoping, and content structure, scoring each one out of 16.
- `skill-usage-report` (a Skill, invoke via the Skill tool): already knows
  how to run and interpret `cc-skill-usage` output correctly, including the
  mandatory cross-verification step for any invocation count that looks
  surprising. Use it instead of improvising `cc-skill-usage` invocations
  from scratch.

Skills live in `~/.claude/skills/` (global, loaded into every session) and
optionally in a repo's own `.claude/skills/` (project-local, only loaded
when working in that repo). Scope this report to the global set first. Only
widen to a specific project's local skills if the global report surfaces
something that clearly needs that extra scope to explain.

## Task

Run this as a workflow with at least these phases:

1. **Usage phase** (parallel across slices): gather usage data via
   `cc-skill-usage`, following `skill-usage-report`'s guidance on which
   command answers which question, for: all-time, the last 30 days, the
   last 90 days (if the transcript history goes back that far), and the 3
   to 4 most active projects individually (pick them from the all-time
   leaderboard's project breakdown, do not guess which ones matter).
2. **Quality phase** (parallel with phase 1): invoke `eval-skills` on
   `~/.claude/skills` for a full quality audit of every skill found there.
3. **Cross-reference phase**: join the two datasets by skill name. Handle
   name variants explicitly instead of silently merging or silently
   ignoring them: this tool's own transcripts have already shown
   near-duplicate names for what is clearly the same underlying skill (for
   example `TDD` next to `tdd`, `dispatching-parallel-agents` next to
   `superpowers:dispatching-parallel-agents`, several `tech:x` variants
   next to `tech-x`). Actively search the full skill set for this pattern,
   do not assume the examples just given are exhaustive or still current.
4. **Verify phase**: before any single number appears in the executive
   summary or drives a strong recommendation (a "never used" claim, a "used
   constantly" claim, a "retire this" call), run the independent
   cross-check `skill-usage-report` documents (a from-scratch `grep`+`jq`
   pipeline against the raw transcripts). Do not report an invocation count
   as fact without having run this.

## Deliverable

A written report with:

1. **Executive summary**, verdict first: how many skills were scanned, how
   many had at least one real invocation in the lookback window, the
   overall `eval-skills` pass rate, and the 3 highest-impact findings.
2. **Table**: top skills by usage, with each one's `eval-skills` score
   alongside, so usage and quality sit side by side.
3. **Table**: quadrant classification, one skill per row:
   - high usage + high quality: protect, keep well documented
   - high usage + low quality: fix first, the impact of a bad
     `when_to_use` or missing `effort` field is real here
   - low usage + high quality: well-built but rarely triggered, check
     whether its `when_to_use` is too narrow or overlaps with another skill
     that wins the dispatch
   - low or zero usage + low quality: retire candidates
4. **Table**: name-variant fragmentation actually found in the data, each
   row a cluster of literal names that are clearly the same conceptual
   skill, with a recommended single canonical name to consolidate on.
5. **Actionable tips**, each tied to one specific skill, one specific fix
   (add an `effort` field, tighten a `when_to_use`, merge two name variants,
   retire outright), and why it matters, ranked by usage impact: a fix to a
   heavily-used skill outranks the identical fix applied to a skill invoked
   once.

Do not pad the report with generic best-practice advice that is not tied to
an actual finding from this machine's real data. Every table row and every
tip should trace back to a number actually produced during this run, and,
wherever the task above calls for verification, actually verified rather
than assumed.
