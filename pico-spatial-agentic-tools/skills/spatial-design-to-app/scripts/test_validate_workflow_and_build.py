#!/usr/bin/env python3
import json
import os
import shlex
import signal
import time
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SOURCE_SCRIPT = Path(__file__).resolve().parent / "validate_workflow_and_build.sh"
SOURCE_EXPERIMENTAL_API_CHECKER = (
    Path(__file__).resolve().parents[2]
    / "spatial-sdk-guideline/scripts/check_experimental_api_opt_in.py"
)


class ValidateWorkflowAndBuildTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "skills"
        self.script_dir = self.root / "spatial-design-to-app/scripts"
        self.design_script_dir = self.root / "spatial-ui-design-style/scripts"
        self.designer_script_dir = self.root / "pico-spatial-app-designer/design/scripts"
        self.experimental_api_script_dir = self.root / "spatial-sdk-guideline/scripts"
        self.script_dir.mkdir(parents=True)
        self.experimental_api_script_dir.mkdir(parents=True)
        shutil.copy(SOURCE_SCRIPT, self.script_dir / "validate_workflow_and_build.sh")
        shutil.copy(
            SOURCE_SCRIPT.parent / "verification-summary.mjs",
            self.script_dir / "verification-summary.mjs",
        )
        shutil.copy(
            SOURCE_EXPERIMENTAL_API_CHECKER,
            self.experimental_api_script_dir / "check_experimental_api_opt_in.py",
        )
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
        self.target = Path(self.temp_dir.name) / "target with spaces"
        (self.target / "src/main/java/com/example").mkdir(parents=True)
        (self.target / "src/main/java/com/example/Demo.kt").write_text(
            "fun Demo() {}\n", encoding="utf-8"
        )
        self.install_design_spec_checker()

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
            timeout=30,
        )

    def install_design_verifier(self, body: str = "#!/usr/bin/env bash\nexit 0\n") -> None:
        self.design_script_dir.mkdir(parents=True)
        path = self.design_script_dir / "verify-design-style.sh"
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)

    def install_design_spec_checker(self, exit_code: int = 0) -> None:
        self.designer_script_dir.mkdir(parents=True, exist_ok=True)
        path = self.designer_script_dir / "check_design_spec.py"
        path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import json",
                    "import sys",
                    "from pathlib import Path",
                    "spec = Path(sys.argv[1])",
                    "out = spec.parent / 'design-spec-checker-args.json'",
                    "out.write_text(json.dumps(sys.argv[1:]), encoding='utf-8')",
                    "print('[design-spec-check] fixture invoked')",
                    f"raise SystemExit({exit_code})",
                    "",
                ]
            ),
            encoding="utf-8",
        )

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

    def test_success_receipt_identifies_current_inputs_and_required_checks(self) -> None:
        self.install_design_verifier()
        result = self.run_validate()
        self.assertEqual(0, result.returncode, result.stdout)
        summary = json.loads((self.target / ".scratch/verification_summary.json").read_text())
        self.assertEqual("spatialcraft.compose-verification/v1", summary["schemaVersion"])
        self.assertEqual(str(self.target.resolve()), summary["inputs"]["target"])
        self.assertEqual(64, len(summary["inputs"]["sourceDigest"]))
        self.assertTrue(summary["invocationId"])
        self.assertEqual(10, len(summary["checks"]))
        self.assertEqual({"passed"}, set(summary["checks"].values()))

    def test_source_change_during_checks_cannot_leave_a_clean_summary(self) -> None:
        self.install_design_verifier()
        source = self.target / "src/main/java/com/example/Demo.kt"
        (self.script_dir / "smoke_build.sh").write_text(
            f"#!/usr/bin/env bash\necho changed >> '{source}'\nexit 0\n", encoding="utf-8"
        )
        result = self.run_validate()
        self.assertEqual(1, result.returncode, result.stdout)
        summary = json.loads((self.target / ".scratch/verification_summary.json").read_text())
        self.assertFalse(summary["clean"])
        self.assertEqual("failed", summary["status"])
        self.assertTrue(summary["stale"])
        self.assertIn("Validation inputs changed while checks were running.", summary["warnings"])

    @unittest.skipIf(os.name == "nt", "POSIX process-group signals")
    def test_interruption_cannot_restore_a_previous_clean_summary(self) -> None:
        self.install_design_verifier()
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=signum):
                ready = self.target / ".scratch/ready"
                ready.parent.mkdir(exist_ok=True)
                ready.unlink(missing_ok=True)
                summary_path = self.target / ".scratch/verification_summary.json"
                summary_path.write_text('{"clean":true,"passed":true}')
                (self.script_dir / "smoke_build.sh").write_text(
                    f"#!/usr/bin/env bash\ntouch '{ready}'\nsleep 180\n", encoding="utf-8"
                )
                child = subprocess.Popen(
                    [
                        "bash",
                        str(self.script_dir / "validate_workflow_and_build.sh"),
                        str(self.target),
                        "--input-mode",
                        "visual_reference",
                        "--generation-mode",
                        "existing_module",
                        "--no-design-colors",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    start_new_session=True,
                )
                try:
                    deadline = time.monotonic() + 5
                    while (
                        not ready.exists() and child.poll() is None and time.monotonic() < deadline
                    ):
                        time.sleep(0.02)
                    self.assertTrue(
                        ready.exists(), "Validator did not reach the controlled child boundary"
                    )
                    os.killpg(child.pid, signum)
                    stdout, _ = child.communicate(timeout=5)
                    self.assertIn(child.returncode, (-signum, 128 + signum), stdout)
                    self.assertFalse(json.loads(summary_path.read_text())["clean"])
                finally:
                    if child.poll() is None:
                        os.killpg(child.pid, signal.SIGKILL)
                        child.communicate(timeout=5)

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
        args = json.loads(
            (self.target / ".scratch/design_fidelity_args.json").read_text(encoding="utf-8")
        )
        self.assertIn("--design-spec", args)
        self.assertEqual(
            (self.target / ".scratch/design-spec.json").resolve(),
            Path(args[args.index("--design-spec") + 1]).resolve(),
        )

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

    def test_missing_experimental_api_checker_is_invocation_error(self) -> None:
        self.install_design_verifier()
        (self.experimental_api_script_dir / "check_experimental_api_opt_in.py").unlink()

        result = self.run_validate()

        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("required script not found", result.stdout)
        self.assertIn("check_experimental_api_opt_in.py", result.stdout)
        self.assertNotIn("[preflight] invocation and design-color contract", result.stdout)

    def test_design_style_result_json_is_written_on_success(self) -> None:
        self.install_design_verifier("#!/usr/bin/env bash\necho design ok\nexit 0\n")

        result = self.run_validate()

        self.assertEqual(0, result.returncode, result.stdout)
        design_result = self.target / ".scratch/design_style_result.json"
        self.assertTrue(design_result.exists())
        self.assertIn('"passed": true', design_result.read_text(encoding="utf-8"))

    def test_design_style_receives_design_spec_when_present(self) -> None:
        design_spec = self.write_design_spec({})
        args_file = self.target / ".scratch/design-style-args.txt"
        self.install_design_verifier(
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    f"printf '%s\\n' \"$@\" > {shlex.quote(args_file.as_posix())}",
                    "exit 0",
                    "",
                ]
            )
        )

        result = self.run_validate()

        self.assertEqual(0, result.returncode, result.stdout)
        args = args_file.read_text(encoding="utf-8").splitlines()
        self.assertIn("--design-spec", args)
        self.assertEqual(
            design_spec.resolve(), Path(args[args.index("--design-spec") + 1]).resolve()
        )

    def test_design_spec_checker_receives_spec_before_source_admission(self) -> None:
        design_spec = self.write_design_spec({})
        self.install_design_verifier()

        result = self.run_validate()

        self.assertEqual(0, result.returncode, result.stdout)
        args = json.loads(
            (design_spec.parent / "design-spec-checker-args.json").read_text(encoding="utf-8")
        )
        self.assertEqual(1, len(args))
        self.assertEqual(design_spec.resolve(), Path(args[0]).resolve())
        self.assertLess(
            result.stdout.index("[design-spec-check] fixture invoked"),
            result.stdout.index("[1/9] intent brief and handoff receipts"),
        )

    def test_design_spec_checker_failure_cannot_be_bypassed_by_allow_degraded(self) -> None:
        self.write_design_spec({})
        self.install_design_verifier()
        self.install_design_spec_checker(exit_code=7)

        result = self.run_validate("--allow-degraded")

        self.assertEqual(7, result.returncode, result.stdout)
        self.assertIn("[design-spec-check] fixture invoked", result.stdout)
        self.assertNotIn("[1/9] intent brief and handoff receipts", result.stdout)
        summary = json.loads(
            (self.target / ".scratch/verification_summary.json").read_text(encoding="utf-8")
        )
        self.assertFalse(summary["passed"])
        self.assertEqual("failed", summary["status"])
        self.assertEqual(7, summary["exit_code"])

    def test_design_spec_checker_is_skipped_when_spec_absent(self) -> None:
        self.install_design_verifier()

        result = self.run_validate()

        self.assertEqual(0, result.returncode, result.stdout)
        self.assertNotIn("[design-spec-check] fixture invoked", result.stdout)
        self.assertFalse((self.target / ".scratch/design-spec-checker-args.json").exists())

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
            timeout=30,
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
            timeout=30,
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
