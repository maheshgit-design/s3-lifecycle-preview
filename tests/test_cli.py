import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from s3_lifecycle_preview.cli import main

ROOT = Path(__file__).resolve().parents[1]
ARGS = ["--policy", str(ROOT / "examples/policy.json"), "--inventory", str(ROOT / "examples/inventory.json"),
        "--as-of", "2026-04-01T00:00:00Z"]


class CliTests(unittest.TestCase):
    def invoke(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = main(args)
        return status, out.getvalue(), err.getvalue()

    def test_example_golden_and_no_network(self):
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            status, out, err = self.invoke(ARGS)
        self.assertEqual(status, 0)
        self.assertEqual(err, "")
        self.assertEqual(json.loads(out), json.loads((ROOT / "examples/expected-report.json").read_text()))

    def test_fail_on_eligible(self):
        self.assertEqual(self.invoke(ARGS + ["--fail-on-eligible"])[0], 1)

    def test_text(self):
        status, out, _ = self.invoke(ARGS + ["--format", "text"])
        self.assertEqual(status, 0)
        self.assertIn("snapshot eligibility", out)

    def test_invalid_json_and_duplicate_keys(self):
        for value in ('{', '{"Rules": [], "Rules": []}'):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.json"
                path.write_text(value)
                status, out, err = self.invoke(["--policy", str(path)] + ARGS[2:])
                self.assertEqual(status, 2)
                self.assertEqual(out, "")
                self.assertIn("error:", err)

    def test_missing_file(self):
        self.assertEqual(self.invoke(["--policy", "/nonexistent/policy.json"] + ARGS[2:])[0], 2)

    def test_module_entrypoint(self):
        result = subprocess.run([sys.executable, "-m", "s3_lifecycle_preview", "--version"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "0.1.0")
