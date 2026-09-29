#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "check_handoff_receipts.py"


def load_checker_module():
    spec = importlib.util.spec_from_file_location("check_handoff_receipts", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load checker module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALID_RECEIPT = {
    "schema_version": 1,
    "phase": "designer_gate",
    "input_mode": "intent_only",
    "visual_asset_present": False,
    "gate_required": True,
    "status": "designer_passed",
    "pre_gates": {
        "designDocComplete": True,
        "designSpecValid": True,
        "previewMatchesSpec": True,
        "postBuildVerdict": "pass",
    },
}

VALID_HANDOFF = {
    "schema_version": 1,
    "phase": "6_scaffold_handoff",
    "producer_skill": "spatial-app-onboarding",
    "consumer_skill": "spatial-design-to-app",
    "scaffold_only": True,
    "product_ui_implemented": False,
    "template": "planar",
    "package": "com.example.demo.p1234abcd",
    "package_source": "generated_default",
    "entry_points": ["com.example.demo.p1234abcd.Main"],
    "build_passed": True,
    "launch_checked": True,
    "resume_required": True,
    "resume_skill": "spatial-design-to-app",
}


class CheckHandoffReceiptsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name) / "generated-app"
        self.scratch_dir = self.target_dir / ".scratch"
        self.scratch_dir.mkdir(parents=True)
        (self.scratch_dir / "intent-brief.md").write_text(
            "# Intent Brief\n\nGoal: Build the requested app.\n",
            encoding="utf-8",
        )
        self.checker = load_checker_module()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write(self, name: str, payload: dict) -> None:
        (self.scratch_dir / name).write_text(json.dumps(payload), encoding="utf-8")

    def run_main(self, **kwargs) -> int:
        argv = [
            "--target",
            str(self.target_dir),
            "--input-mode",
            kwargs.get("input_mode", "intent_only"),
            "--generation-mode",
            kwargs.get("generation_mode", "existing_module"),
            "--visual-asset",
            kwargs.get("visual_asset", "false"),
            "--design-gate-result",
            kwargs.get("design_gate_result", "designer_passed"),
        ]
        return self.checker.main(argv)

    # ---- designer gate ----------------------------------------------------

    def test_intent_only_requires_an_intent_brief(self) -> None:
        (self.scratch_dir / "intent-brief.md").unlink()

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("intent-brief.md", str(ctx.exception))

    def test_intent_brief_must_be_non_empty(self) -> None:
        (self.scratch_dir / "intent-brief.md").write_text("\n", encoding="utf-8")

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("non-empty", str(ctx.exception))

    def test_non_intent_input_does_not_require_an_intent_brief(self) -> None:
        (self.scratch_dir / "intent-brief.md").unlink()

        self.assertEqual(
            0,
            self.run_main(input_mode="visual_reference", visual_asset="true"),
        )

    def test_no_visual_input_requires_a_receipt(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("design_escalation_receipt.json", str(ctx.exception))

    def test_designer_passed_receipt_is_accepted(self) -> None:
        self.write("design_escalation_receipt.json", VALID_RECEIPT)

        self.assertEqual(0, self.run_main(input_mode="intent_only"))

    def test_valid_user_package_does_not_require_designer_receipt(self) -> None:
        self.write("design-spec.json", {"schemaVersion": "1.0"})

        self.assertEqual(
            0,
            self.run_main(
                input_mode="product_doc",
                design_gate_result="user_package_passed",
            ),
        )

    def test_user_package_result_requires_design_spec(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.run_main(
                input_mode="product_doc",
                design_gate_result="user_package_passed",
            )

        self.assertIn("design-spec.json", str(ctx.exception))

    def test_user_package_result_requires_valid_json_object(self) -> None:
        (self.scratch_dir / "design-spec.json").write_text("{", encoding="utf-8")

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(
                input_mode="product_doc",
                design_gate_result="user_package_passed",
            )

        self.assertIn("Invalid JSON", str(ctx.exception))

    def test_user_package_result_rejects_intent_only_mode(self) -> None:
        self.write("design-spec.json", {"schemaVersion": "1.0"})

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(
                input_mode="intent_only",
                design_gate_result="user_package_passed",
            )

        self.assertIn("product_doc or hybrid", str(ctx.exception))

    def test_fallback_receipt_is_rejected(self) -> None:
        receipt = dict(VALID_RECEIPT, status="fallback_accepted")
        self.write("design_escalation_receipt.json", receipt)

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("fallback_accepted", str(ctx.exception))

    def test_incomplete_design_doc_is_rejected(self) -> None:
        receipt = json.loads(json.dumps(VALID_RECEIPT))
        receipt["pre_gates"]["designDocComplete"] = False
        self.write("design_escalation_receipt.json", receipt)

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("designDocComplete", str(ctx.exception))

    def test_failed_designer_critique_is_rejected(self) -> None:
        receipt = json.loads(json.dumps(VALID_RECEIPT))
        receipt["pre_gates"]["postBuildVerdict"] = "fail"
        self.write("design_escalation_receipt.json", receipt)

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("postBuildVerdict", str(ctx.exception))

    def test_invalid_design_spec_is_rejected(self) -> None:
        receipt = json.loads(json.dumps(VALID_RECEIPT))
        receipt["pre_gates"]["designSpecValid"] = False
        self.write("design_escalation_receipt.json", receipt)

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("designSpecValid", str(ctx.exception))

    def test_preview_spec_divergence_is_rejected(self) -> None:
        receipt = json.loads(json.dumps(VALID_RECEIPT))
        receipt["pre_gates"]["previewMatchesSpec"] = False
        self.write("design_escalation_receipt.json", receipt)

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("previewMatchesSpec", str(ctx.exception))

    def test_product_doc_also_requires_the_gate(self) -> None:
        with self.assertRaises(SystemExit):
            self.run_main(input_mode="product_doc")

    def test_hybrid_without_visual_asset_requires_the_gate(self) -> None:
        with self.assertRaises(SystemExit):
            self.run_main(input_mode="hybrid", visual_asset="false")

    def test_hybrid_with_visual_asset_skips_the_gate(self) -> None:
        self.assertEqual(0, self.run_main(input_mode="hybrid", visual_asset="true"))

    def test_visual_input_does_not_require_the_gate(self) -> None:
        self.assertEqual(0, self.run_main(input_mode="visual_reference", visual_asset="true"))

    def test_receipt_input_mode_must_match_the_run(self) -> None:
        receipt = dict(VALID_RECEIPT, input_mode="product_doc")
        self.write("design_escalation_receipt.json", receipt)

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only")

        self.assertIn("does not match", str(ctx.exception))

    # ---- onboarding handoff ----------------------------------------------

    def test_new_project_requires_onboarding_handoff(self) -> None:
        self.write("design_escalation_receipt.json", VALID_RECEIPT)

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only", generation_mode="new_project")

        self.assertIn("onboarding_handoff.json", str(ctx.exception))

    def test_scaffold_only_handoff_is_accepted(self) -> None:
        self.write("design_escalation_receipt.json", VALID_RECEIPT)
        self.write("onboarding_handoff.json", VALID_HANDOFF)

        self.assertEqual(0, self.run_main(input_mode="intent_only", generation_mode="new_project"))

    def test_rejects_handoff_that_implemented_product_ui(self) -> None:
        self.write("design_escalation_receipt.json", VALID_RECEIPT)
        self.write("onboarding_handoff.json", dict(VALID_HANDOFF, product_ui_implemented=True))

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only", generation_mode="new_project")

        self.assertIn("product_ui_implemented", str(ctx.exception))

    def test_rejects_handoff_with_failed_build(self) -> None:
        self.write("design_escalation_receipt.json", VALID_RECEIPT)
        self.write("onboarding_handoff.json", dict(VALID_HANDOFF, build_passed=False))

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only", generation_mode="new_project")

        self.assertIn("build_passed", str(ctx.exception))

    def test_explicit_pico_package_is_accepted(self) -> None:
        self.write("design_escalation_receipt.json", VALID_RECEIPT)
        self.write(
            "onboarding_handoff.json",
            dict(
                VALID_HANDOFF,
                package="com.pico.explicit",
                package_source="user_provided",
            ),
        )

        self.assertEqual(0, self.run_main(input_mode="intent_only", generation_mode="new_project"))

    def test_generated_package_must_use_safe_default_shape(self) -> None:
        self.write("design_escalation_receipt.json", VALID_RECEIPT)
        self.write(
            "onboarding_handoff.json",
            dict(VALID_HANDOFF, package="com.picoxr.generated"),
        )

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only", generation_mode="new_project")

        self.assertIn("Generated Onboarding Handoff.package", str(ctx.exception))

    def test_unchecked_launch_requires_a_note(self) -> None:
        self.write("design_escalation_receipt.json", VALID_RECEIPT)
        self.write("onboarding_handoff.json", dict(VALID_HANDOFF, launch_checked=False))

        with self.assertRaises(SystemExit) as ctx:
            self.run_main(input_mode="intent_only", generation_mode="new_project")

        self.assertIn("launch_check_note", str(ctx.exception))

    def test_existing_module_does_not_need_a_handoff(self) -> None:
        self.assertEqual(
            0,
            self.run_main(
                input_mode="visual_reference",
                generation_mode="existing_module",
                visual_asset="true",
            ),
        )

    def test_incremental_patch_needs_neither_receipt(self) -> None:
        self.assertEqual(
            0,
            self.run_main(
                input_mode="incremental_patch",
                generation_mode="new_project",
                visual_asset="true",
            ),
        )


if __name__ == "__main__":
    unittest.main()
