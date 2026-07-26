# Examples and scenarios

Concrete goals, matched to the flag combination that answers them. Every
command below runs against your own `~/.claude/projects/`, nothing is
sample data.

## "What have I actually been using this month?"

```bash
cc-skill-usage --since 30d --show-context
```

The full leaderboard, one block per skill, with the message that triggered
its most recent use. This is the default starting point for a usage recap:
every skill you touched, most-used first, with enough context to remember
why.

## "Is this specific skill still worth keeping?"

```bash
cc-skill-usage flow-lean --show-context
```

Per-skill detail: total count, sessions, breakdown by project and by
argument (if the skill takes one, e.g. `lite`/`full`/`ultra`), a daily
histogram, and the last 20 invocations with their triggering context. If the
count is 0 or 1 over the window you care about, that is a real signal to
retire or merge the skill, not a fluke worth re-checking (see the
cross-verification note below if the number still surprises you).

## "How much of my skill usage is one specific repo, versus everything else?"

```bash
cc-skill-usage --since 30d --project myrepo --json > /tmp/repo.json
cc-skill-usage --since 30d --json > /tmp/global.json
```

Diff the two `skills[].invocations` arrays (by skill name) to get, per
skill, how much of its usage is that repo versus every other project
combined. `--project` catches every git worktree of that repo under one
needle, so a worktree-heavy setup does not undercount silently, see
[README](README.md#filtering-by-project-including-worktrees).

## "What did I just do, in order?"

```bash
cc-skill-usage --all recent 20 --show-context
```

The 20 most recent invocations across every project, newest first, each with
its session id and triggering message. Useful right after a working
session to reconstruct what actually got invoked and why, without digging
through the raw transcript.

## "I only care about the last week, on one project"

```bash
cc-skill-usage --since 7d --project myrepo --show-context
```

Combines a time window and a project filter. Good for a weekly team or
personal recap scoped to one codebase.

## "I want this in a script, a dashboard, or piped into something else"

```bash
cc-skill-usage --json
cc-skill-usage flow-lean --json
cc-skill-usage --all recent 50 --json
```

Every view supports `--json`. The detail view's JSON includes a `recent`
array (last 20 invocations with context) even without `--show-context`,
since the flag only changes text-output verbosity, not the JSON payload.

## "A number looks wrong, too low or too high"

This happened while building the tool itself: a skill believed to be used
constantly showed only 11 invocations over 30 days. Before assuming a bug,
cross-check independently of the tool:

```bash
# raw text mentions (name in prose, files, summaries: expect this to be much higher)
grep -rl 'your-skill-name' ~/.claude/projects --include="*.jsonl" | wc -l

# real invocations, built from scratch, independent of cc-skill-usage's own code
grep -rh '"name":"Skill"' ~/.claude/projects --include="*.jsonl" \
  | jq -r '.message.content[]? | select(.type=="tool_use" and .name=="Skill") | .input.skill' \
  | grep -c '^your-skill-name$'
```

If the two independent numbers (cc-skill-usage and this raw pipeline) match,
the count is correct and the surprise is about the invocation-vs-mention gap,
not a bug. That gap was measured at 212x on real data (2330 mentions, 11 real
invocations) during development. See [README](README.md#what-counts-as-an-invocation)
and [CLAUDE.md](CLAUDE.md) for the full story.

## "I just updated the tool and something looks off"

```bash
cc-skill-usage --rebuild
```

Forces every transcript to be re-parsed and rewrites the cache, without the
one-off overhead of `--no-cache` (which never touches the cache file at
all). Reach for this after a `cc-skill-usage` upgrade if a count still looks
stale, though the cache is schema-versioned and should invalidate itself
automatically in that case, see [CLAUDE.md](CLAUDE.md).

## "Include subagent work, not just the main session"

```bash
cc-skill-usage --include-subagents --since 30d
```

Off by default because subagent-driven invocations answer a different
question (what did the orchestration spawn versus what did I invoke
directly). Turn it on when auditing everything a multi-agent workflow
actually triggered under the hood.
