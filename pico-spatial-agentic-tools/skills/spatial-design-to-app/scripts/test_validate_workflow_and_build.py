#!/usr/bin/env python3
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE_SCRIPT = Path(__file__).resolve().parent / "validate_workflow_and_build.sh"


class ValidateWorkflowAndBuildTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "skills"
        self.script_dir = self.root / "spatial-design-to-app/scripts"
        self.design_script_dir = self.root / "spatial-ui-design-style/scripts"
        self.script_dir.mkdir(parents=True)
        shutil.copy(SOURCE_SCRIPT, self.script_dir / "validate_workflow_and_build.sh")
        for name in (
            "check_handoff_receipts.py",
            "scan_implementation.py",
            "check_design_fidelity.py",
            "gradle_sync_check.sh",
            "smoke_build.sh",
            "runtime_launch_check.sh",
            "check_architecture.py",
            "run_unit_tests.sh",
        ):
            path = self.script_dir / name
            if name.endswith(".py"):
                path.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            else:
                path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            path.chmod(0o755)
        self.target = Path(self.temp_dir.name) / "target"
        (self.target / "src/main/java/com/example").mkdir(parents=True)
        (self.target / "src/main/java/com/example/Demo.kt").write_text(
            "fun Demo() {}\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_validate(self, *args: str) -> subprocess.CompletedProcess[str]:
        # --input-mode / --generation-mode are required; --no-design-colors keeps
        # R1b from failing these design-style-focused tests on a bare fixture.
        base = ["--input-mode", "visual_reference", "--generation-mode", "existing_module"]
        if (
            not any(a.startswith("--design-color") for a in args)
            and "--no-design-colors" not in args
        ):
            base.append("--no-design-colors")
        return subprocess.run(
            [
                "bash",
                str(self.script_dir / "validate_workflow_and_build.sh"),
                str(self.target),
                *base,
                *args,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def install_design_verifier(self, body: str = "#!/usr/bin/env bash\nexit 0\n") -> None:
        self.design_script_dir.mkdir(parents=True)
        path = self.design_script_dir / "verify-design-style.sh"
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)

    def write_design_spec(self, brand_colors: dict[str, str]) -> Path:
        scratch = self.target / ".scratch"
        scratch.mkdir(exist_ok=True)
        path = scratch / "design-spec.json"
        path.write_text(
            json.dumps({"theme": {"brandColors": brand_colors}, "nodes": []}),
            encoding="utf-8",
        )
        return path

    def test_design_fidelity_runs_before_gradle_and_is_mandatory(self) -> None:
        self.install_design_verifier()
        checker = self.script_dir / "check_design_fidelity.py"
        checker.write_text(
            '#!/usr/bin/env python3\nprint("[design-fidelity] forced failure")\nraise SystemExit(1)\n',
            encoding="utf-8",
        )

        result = self.run_validate()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("[3/9] design JSON to app fidelity", result.stdout)
        self.assertIn("[design-fidelity] forced failure", result.stdout)
        self.assertNotIn("[4/9] Gradle sync/project discovery", result.stdout)

    def test_failed_run_replaces_previous_clean_summary(self) -> None:
        self.install_design_verifier()

        successful = self.run_validate()

        self.assertEqual(0, successful.returncode, successful.stdout)
        summary_path = self.target / ".scratch/verification_summary.json"
        self.assertTrue(json.loads(summary_path.read_text(encoding="utf-8"))["clean"])

        checker = self.script_dir / "check_design_fidelity.py"
        checker.write_text("#!/usr/bin/env python3\nraise SystemExit(1)\n", encoding="utf-8")
        failed = self.run_validate()

        self.assertNotEqual(0, failed.returncode, failed.stdout)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertFalse(summary["passed"])
        self.assertFalse(summary["clean"])
        self.assertEqual("failed", summary["status"])
        self.assertEqual(failed.returncode, summary["exit_code"])

    def test_invocation_error_invalidates_previous_clean_summary(self) -> None:
        summary_path = self.target / ".scratch/verification_summary.json"
        summary_path.parent.mkdir(exist_ok=True)
        summary_path.write_text('{"passed": true, "clean": true}', encoding="utf-8")

        result = self.run_validate("--unknown-option")

        self.assertEqual(2, result.returncode, result.stdout)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertFalse(summary["passed"])
        self.assertFalse(summary["clean"])
        self.assertEqual("failed", summary["status"])
        self.assertEqual(2, summary["exit_code"])

    def test_disallowed_degraded_run_preserves_diagnostics(self) -> None:
        self.install_design_verifier()

        result = self.run_validate("--skip-gradle-sync")

        self.assertEqual(1, result.returncode, result.stdout)
        summary_path = self.target / ".scratch/verification_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertFalse(summary["passed"])
        self.assertFalse(summary["clean"])
        self.assertTrue(summary["operational"])
        self.assertEqual("failed", summary["status"])
        self.assertEqual(1, summary["exit_code"])
        self.assertFalse(summary["allow_degraded"])
        self.assertEqual(["gradle_sync"], summary["skips"])
        self.assertIn("--skip-gradle-sync supplied", summary["warnings"][0])

    def test_allowed_degraded_run_preserves_diagnostics(self) -> None:
        self.install_design_verifier()

        result = self.run_validate("--skip-gradle-sync", "--allow-degraded")

        self.assertEqual(0, result.returncode, result.stdout)
        summary_path = self.target / ".scratch/verification_summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertFalse(summary["passed"])
        self.assertFalse(summary["clean"])
        self.assertTrue(summary["operational"])
        self.assertEqual("degraded", summary["status"])
        self.assertNotIn("exit_code", summary)
        self.assertTrue(summary["allow_degraded"])
        self.assertEqual(["gradle_sync"], summary["skips"])
        self.assertIn("--skip-gradle-sync supplied", summary["warnings"][0])

    def test_design_fidelity_receives_workflow_design_spec_path(self) -> None:
        self.install_design_verifier()
        checker = self.script_dir / "check_design_fidelity.py"
        checker.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import json",
                    "import sys",
                    "from pathlib import Path",
                    "target = Path(sys.argv[sys.argv.index('--target') + 1])",
                    "out = target / '.scratch' / 'design_fidelity_args.json'",
                    "out.write_text(json.dumps(sys.argv), encoding='utf-8')",
                    "raise SystemExit(0)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        checker.chmod(0o755)

        result = self.run_validate()

        self.assertEqual(0, result.returncode, result.stdout)
        args = (self.target / ".scratch/design_fidelity_args.json").read_text(encoding="utf-8")
        self.assertIn("--design-spec", args)
        self.assertIn(str(self.target / ".scratch/design-spec.json"), args)

    def test_design_gate_result_is_forwarded_to_receipt_checker(self) -> None:
        self.install_design_verifier()
        checker = self.script_dir / "check_handoff_receipts.py"
        checker.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import json",
                    "import sys",
                    "from pathlib import Path",
                    "target = Path(sys.argv[sys.argv.index('--target') + 1])",
                    "out = target / '.scratch' / 'receipt_checker_args.json'",
                    "out.parent.mkdir(parents=True, exist_ok=True)",
                    "out.write_text(json.dumps(sys.argv), encoding='utf-8')",
                    "raise SystemExit(0)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        checker.chmod(0o755)

        result = self.run_validate(
            "--design-gate-result",
            "user_package_passed",
        )

        self.assertEqual(0, result.returncode, result.stdout)
        args = json.loads(
            (self.target / ".scratch/receipt_checker_args.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            "user_package_passed",
            args[args.index("--design-gate-result") + 1],
        )

    def test_skip_design_style_cannot_be_bypassed_by_allow_degraded(self) -> None:
        self.install_design_verifier()

        result = self.run_validate("--skip-design-style", "--allow-degraded")

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("design-style admission is mandatory", result.stdout)

    def test_missing_design_style_verifier_is_hard_failure(self) -> None:
        result = self.run_validate()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("spatial-ui-design-style verifier not found", result.stdout)

    def test_design_style_result_json_is_written_on_success(self) -> None:
        self.install_design_verifier("#!/usr/bin/env bash\necho design ok\nexit 0\n")

        result = self.run_validate()

        self.assertEqual(0, result.returncode, result.stdout)
        design_result = self.target / ".scratch/design_style_result.json"
        self.assertTrue(design_result.exists())
        self.assertIn('"passed": true', design_result.read_text(encoding="utf-8"))

    def test_design_style_receives_design_spec_when_present(self) -> None:
        design_spec = self.write_design_spec({})
        args_file = self.target / "design-style-args.txt"
        self.install_design_verifier(
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    f"printf '%s\\n' \"$@\" > {args_file!s}",
                    "exit 0",
                    "",
                ]
            )
        )

        result = self.run_validate()

        self.assertEqual(0, result.returncode, result.stdout)
        args = args_file.read_text(encoding="utf-8")
        self.assertIn("--design-spec", args)
        self.assertIn(str(design_spec), args)

    def test_missing_input_mode_is_an_invocation_error(self) -> None:
        self.install_design_verifier()

        result = subprocess.run(
            [
                "bash",
                str(self.script_dir / "validate_workflow_and_build.sh"),
                str(self.target),
                "--no-design-colors",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("--input-mode", result.stdout)

    def test_undeclared_design_colors_fail_instead_of_passing_silently(self) -> None:
        self.install_design_verifier()

        result = subprocess.run(
            [
                "bash",
                str(self.script_dir / "validate_workflow_and_build.sh"),
                str(self.target),
                "--input-mode",
                "visual_reference",
                "--generation-mode",
                "existing_module",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("[preflight] invocation and design-color contract", result.stdout)
        self.assertIn("custom design colors were not declared", result.stdout)
        self.assertNotIn("[1/9] intent brief and handoff receipts", result.stdout)

    def test_incomplete_design_color_coverage_fails_in_preflight(self) -> None:
        self.write_design_spec({"brandAccent": "#FF6B4A", "supportAccent": "#24A8FF"})
        self.install_design_verifier()

        result = self.run_validate("--design-color", "brandAccent=#FF6B4A")

        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("[preflight] invocation and design-color contract", result.stdout)
        self.assertIn("missing --design-color supportAccent=#24A8FF", result.stdout)
        self.assertNotIn("[1/9] intent brief and handoff receipts", result.stdout)
        summary = json.loads(
            (self.target / ".scratch/verification_summary.json").read_text(encoding="utf-8")
        )
        self.assertFalse(summary["clean"])
        self.assertEqual("failed", summary["status"])
        self.assertEqual(2, summary["exit_code"])

    def test_complete_design_color_coverage_passes_preflight(self) -> None:
        self.write_design_spec({"brandAccent": "#FF6B4A", "supportAccent": "#24A8FF"})
        self.install_design_verifier()

        result = self.run_validate(
            "--design-color",
            "brandAccent=#FF6B4A",
            "--design-color",
            "supportAccent=#24A8FF",
        )

        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("[preflight] invocation and design-color contract", result.stdout)
        self.assertIn("[1/9] intent brief and handoff receipts", result.stdout)

    def test_invalid_design_color_coverage_fails_in_preflight(self) -> None:
        self.write_design_spec({"brandAccent": "#FF6B4A", "supportAccent": "#24A8FF"})
        self.install_design_verifier()
        cases = [
            (
                (
                    "--design-color",
                    "brandAccent=#000000",
                    "--design-color",
                    "supportAccent=#24A8FF",
                ),
                "mismatched --design-color brandAccent",
            ),
            (
                (
                    "--design-color",
                    "brandAccent=#FF6B4A",
                    "--design-color",
                    "supportAccent=#24A8FF",
                    "--design-color",
                    "extraAccent=#FFFFFF",
                ),
                "unexpected --design-color extraAccent=#FFFFFF",
            ),
            (
                ("--no-design-colors",),
                "missing --design-color brandAccent=#FF6B4A",
            ),
            (
                (
                    "--design-color",
                    "brandAccent=#FF6B4A",
                    "--design-color",
                    "brandAccent=#FF6B4A",
                ),
                "duplicate --design-color token 'brandAccent'",
            ),
        ]

        for args, expected_error in cases:
            with self.subTest(expected_error=expected_error):
                result = self.run_validate(*args)
                self.assertEqual(2, result.returncode, result.stdout)
                self.assertIn(expected_error, result.stdout)
                self.assertNotIn("[1/9] intent brief and handoff receipts", result.stdout)

    def test_design_colors_are_forwarded_to_the_verifier(self) -> None:
        self.install_design_verifier('#!/usr/bin/env bash\necho "args: $*"\nexit 0\n')

        result = self.run_validate("--design-color", "brandAccent=#FF6B4A")

        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("--design-color brandAccent=#FF6B4A", result.stdout)


if __name__ == "__main__":
    unittest.main()
