# Scenario tour prompt

Paste this into a fresh Claude Code session to smoke-test every documented
scenario of `cc-skill-usage` against real data on the machine it runs on,
and catch any drift between what the docs say and what the tool actually
does. No prior context needed, this is self-contained.

---

You are validating `cc-skill-usage`, a standalone CLI installed at
`~/.local/bin/cc-skill-usage` (source and docs at
`~/Sites/perso/cc-skill-usage/`, or
https://github.com/FlorianBruniaux/cc-skill-usage). It reads Claude Code's
own JSONL transcripts under `~/.claude/projects/` and reports Skill
invocation analytics: counts, timing, project breakdown, triggering context.

## Task

1. Read `~/Sites/perso/cc-skill-usage/EXAMPLES.md` in full.
2. For every scenario in that file, run the exact command(s) shown, against
   real data on this machine. Do not simulate or describe expected output,
   actually run each one.
3. For each scenario, check:
   - it does not crash or print a traceback
   - the output shape matches what the scenario describes (a leaderboard, a
     per-skill detail block, a chronological list, valid JSON, etc.)
   - numbers are internally consistent. For the "a number looks wrong"
     scenario specifically, actually run both sides of the cross-check
     pipeline it describes and confirm they match, do not just assume they
     will.
4. Run `cc-skill-usage --help` and check every flag's help text still
   describes what the tool actually outputs when you run it. Flag any
   mismatch. This has happened before: a flag's help text described an old
   table layout after the underlying code moved to a different one, and it
   went unnoticed until a human spotted the stale wording.
5. Try at least three deliberately broken inputs: a skill name that has
   never been invoked (expect a clean "no invocations" message, not a
   crash), an invalid `--since` value like `--since banana`, and
   `--all badmode 5`. Confirm the tool fails clearly and says why, rather
   than silently returning something misleading.

## Output

A table: one row per scenario from EXAMPLES.md, plus one row for the
`--help` check, plus one row per broken-input check. Columns: `Scenario`,
`Command`, `PASS/FAIL`, `Note`. For any FAIL or any drift found between docs
and behavior, include the exact command and the relevant output snippet as
evidence, not just a description of the problem. End with a one-line verdict:
does the tool currently hold every promise its own docs make, yes or no.
