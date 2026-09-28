import argparse
import importlib.machinery
import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "cc-skill-usage"
LOADER = importlib.machinery.SourceFileLoader("cc_skill_usage", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
usage = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(usage)


class CrossClientUsageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "skills"
        self.skill = self.root / "common" / "flow-lean" / "SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.content = "---\nname: flow-lean\n---\n\n# Flow Lean\n"
        self.skill.write_text(self.content, encoding="utf-8")
        self.old_roots = os.environ.get("CC_SKILL_ROOTS")
        os.environ["CC_SKILL_ROOTS"] = str(self.root)
        usage.EVENT_LOG = Path(self.temp.name) / "state" / "events.jsonl"

    def tearDown(self):
        if self.old_roots is None:
            os.environ.pop("CC_SKILL_ROOTS", None)
        else:
            os.environ["CC_SKILL_ROOTS"] = self.old_roots
        self.temp.cleanup()

    def test_loader_prints_unchanged_content_and_appends_exact_event(self):
        args = argparse.Namespace(
            skill="flow-lean", path=str(self.skill), session_id="thread-1", subagent=False
        )
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(usage.load_skill_command(args), 0)
        self.assertEqual(output.getvalue(), self.content)
        event = json.loads(usage.EVENT_LOG.read_text(encoding="utf-8"))
        self.assertEqual(event["evidence"], "instrumented_invocation")
        self.assertEqual(event["host"], "codex")
        self.assertEqual(event["skill"], "flow-lean")
        self.assertEqual(event["session_id"], "thread-1")
        self.assertNotIn(str(self.skill), json.dumps(event))
        self.assertEqual(usage.EVENT_LOG.stat().st_mode & 0o777, 0o600)

    def test_loader_rejects_path_outside_allowlist_without_logging(self):
        outside = Path(self.temp.name) / "outside" / "SKILL.md"
        outside.parent.mkdir()
        outside.write_text(self.content, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "outside allowed"):
            usage.validated_skill(outside, "flow-lean")
        self.assertFalse(usage.EVENT_LOG.exists())

    def test_namespaced_runtime_name_may_match_declared_leaf(self):
        resolved, declared, content = usage.validated_skill(
            self.skill, "plugin:flow-lean"
        )
        self.assertEqual(resolved, self.skill.resolve())
        self.assertEqual(declared, "flow-lean")
        self.assertEqual(content, self.content)

    def test_instrumented_reader_skips_partial_tail(self):
        usage.EVENT_LOG.parent.mkdir(parents=True)
        good = {
            "schema": 1,
            "timestamp": "2026-09-04T06:00:00Z",
            "host": "codex",
            "session_id": "thread-1",
            "skill": "flow-lean",
            "evidence": "instrumented_invocation",
        }
        usage.EVENT_LOG.write_text(json.dumps(good) + "\n{", encoding="utf-8")
        events, malformed = usage.read_instrumented_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(malformed, 1)

    def test_unwritable_log_preserves_skill_access_without_exact_event(self):
        from contextlib import redirect_stderr
        usage.EVENT_LOG = Path(self.temp.name)
        args = argparse.Namespace(skill="flow-lean", path=str(self.skill),
                                  session_id="test", subagent=False)
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            result = usage.load_skill_command(args)
        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), self.content)
        self.assertIn("usage event recording unconfirmed", errors.getvalue())
        self.assertTrue(usage.EVENT_LOG.is_dir())

    def test_non_object_event_lines_are_skipped(self):
        usage.EVENT_LOG.parent.mkdir(parents=True)
        usage.EVENT_LOG.write_text('[]\nnull\n42\n', encoding="utf-8")
        events, malformed = usage.read_instrumented_events()
        self.assertEqual(events, [])
        self.assertEqual(malformed, 3)

    def test_leaderboard_keeps_exact_and_inferred_counts_separate(self):
        base = dict(skill="flow-lean", ts="2026-09-04T06:00:00Z",
                    project="fixture", session="test", args=None,
                    context=None, repo_hint="fixture", subagent=False)
        events = [dict(base, host="claude", evidence="native_invocation"),
                  dict(base, host="codex", evidence="instrumented_invocation"),
                  dict(base, host="codex", evidence="observed_load")]
        output = io.StringIO()
        with redirect_stdout(output):
            usage.view_leaderboard(events, as_json=True)
        result = json.loads(output.getvalue())
        self.assertEqual(result["total_invocations"], 2)
        self.assertEqual(result["total_observed_loads"], 1)
        self.assertEqual(len(result["skills"]), 3)
        inferred = next(row for row in result["skills"]
                        if row["evidence"] == "observed_load")
        self.assertEqual(inferred["invocations"], 0)

    def test_completed_codex_read_is_inferred_and_deduplicated(self):
        transcript = Path(self.temp.name) / "rollout.jsonl"
        session = {
            "type": "session_meta",
            "payload": {"id": "thread-1", "source": "cli"},
        }
        item = {
            "timestamp": "2026-09-04T06:00:00Z",
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "turn_id": "turn-1",
                "item": {
                    "type": "CommandExecution",
                    "status": "completed",
                    "exit_code": 0,
                    "cwd": Path(self.temp.name).as_uri(),
                    "parsed_cmd": [
                        {"type": "read", "path": str(self.skill), "name": "SKILL.md"},
                        {"type": "read", "path": str(self.skill), "name": "SKILL.md"},
                    ],
                },
            },
        }
        transcript.write_text(
            json.dumps(session) + "\n" + json.dumps(item) + "\n", encoding="utf-8"
        )
        events = list(usage.parse_codex_file(transcript))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["evidence"], "observed_load")
        self.assertEqual(events[0]["skill"], "flow-lean")

    def test_failed_codex_read_is_not_observed(self):
        transcript = Path(self.temp.name) / "rollout.jsonl"
        item = {
            "type": "event_msg",
            "payload": {
                "type": "item_completed",
                "turn_id": "turn-1",
                "item": {
                    "type": "CommandExecution",
                    "status": "failed",
                    "exit_code": 1,
                    "cwd": Path(self.temp.name).as_uri(),
                    "parsed_cmd": [{"type": "read", "path": str(self.skill)}],
                },
            },
        }
        transcript.write_text(json.dumps(item) + "\n", encoding="utf-8")
        self.assertEqual(list(usage.parse_codex_file(transcript)), [])


if __name__ == "__main__":
    unittest.main()
