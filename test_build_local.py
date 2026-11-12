import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class BuildLocalTest(unittest.TestCase):
    def test_builds_all_targets_and_reports_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy(Path(__file__).with_name("build-local.py"), root)
            (root / "build.yaml").write_text(
                "include:\n  - board: board1\n    shield: good\n"
                "  - board: board2\n    shield: bad\n"
            )
            west = root / "west"
            west.write_text('#!/bin/sh\ncase "$*" in *-DSHIELD=bad*) exit 1;; esac\n')
            west.chmod(0o755)
            env = dict(os.environ, PATH=f"{root}{os.pathsep}{os.environ['PATH']}")
            result = subprocess.run(
                [sys.executable, str(root / "build-local.py")],
                env=env, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("OK good-board1", result.stdout)
            self.assertIn("FAILED bad-board2", result.stdout)
            self.assertTrue((root / "build/good-board1.log").exists())
            self.assertTrue((root / "build/bad-board2.log").exists())

    def test_rejects_unsupported_matrix_options(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy(Path(__file__).with_name("build-local.py"), root)
            (root / "build.yaml").write_text(
                "include:\n  - board: board1\n    shield: good\n    snippet: example\n"
            )
            result = subprocess.run(
                [sys.executable, str(root / "build-local.py")], capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("only supports", result.stderr)


if __name__ == "__main__":
    unittest.main()
