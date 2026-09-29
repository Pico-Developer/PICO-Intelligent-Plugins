#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve().parent / "check_design_fidelity.py"


def sample_spec() -> dict[str, Any]:
    return {
        "initialStateId": "discover",
        "surfaces": [
            {
                "id": "store-wall",
                "type": "planar",
                "defaultSize": {"width": 1420, "height": 860, "unit": "dp"},
                "minSize": {"width": 980, "height": 700, "unit": "dp"},
                "maxSize": {"width": 1760, "height": 1040, "unit": "dp"},
                "rootNodeId": "app-shelf",
            }
        ],
        "nodes": [
            {
                "id": "app-shelf",
                "kind": "domain_visual",
                "rendererKey": "app-shelf",
                "purpose": "application shelf",
                "props": {"featuredCount": 1, "columns": 4},
                "layout": {
                    "mode": "grid",
                    "columns": 4,
                    "gapDp": 16,
                    "overflow": "hidden",
                },
            },
            {
                "id": "search",
                "kind": "spatialui",
                "component": "sui-search-field",
                "props": {"placeholder": "Search"},
            },
        ],
        "states": [{"id": "discover", "surfaceRoots": {"store-wall": "app-shelf"}}],
        "transitions": [],
        "actions": [],
        "responsiveRules": [
            {
                "id": "compact-shelf",
                "surfaceId": "store-wall",
                "when": {"maxWidthDp": 1120},
                "overrides": [
                    {
                        "nodeId": "app-shelf",
                        "layout": {
                            "mode": "grid",
                            "columns": 2,
                            "gapDp": 12,
                            "overflow": "scroll",
                        },
                    }
                ],
            }
        ],
        "dataCases": {"normal": {}, "fallback": {}, "error": {}},
        "assets": [],
    }


def implementation_contract(spec: dict[str, Any]) -> dict[str, Any]:
    def keyed(name: str, ignored: set[str] | None = None) -> dict[str, Any]:
        ignored = ignored or {"id"}
        return {
            item["id"]: {key: value for key, value in item.items() if key not in ignored}
            for item in spec[name]
        }

    return {
        "initialStateId": spec["initialStateId"],
        "surfaces": keyed("surfaces"),
        "nodes": keyed("nodes", {"id", "purpose"}),
        "states": keyed("states"),
        "transitions": keyed("transitions"),
        "actions": keyed("actions", {"id", "purpose"}),
        "responsiveRules": keyed("responsiveRules"),
        "dataCases": ["error", "fallback", "normal"],
        "assets": keyed("assets", {"id", "purpose"}),
    }


class CheckDesignFidelityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target = Path(self.temp_dir.name) / "app"
        self.scratch = self.target / ".scratch"
        self.source = self.target / "app/src/main/java/example/StoreScreen.kt"
        self.source.parent.mkdir(parents=True)
        self.source.write_text(
            "fun AppShelf() { WideAppGrid(); CompactAppGrid(); SearchField() }\n",
            encoding="utf-8",
        )
        self.spec = sample_spec()
        self.spec_path = self.target / "design-spec.json"
        self.write_spec()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_spec(self) -> None:
        self.spec_path.write_text(
            json.dumps(self.spec, ensure_ascii=False),
            encoding="utf-8",
        )

    def write_receipt(self, implementation: dict[str, Any] | None = None) -> None:
        implementation = implementation or implementation_contract(self.spec)
        refs = [
            "state-model:initial",
            "surface:store-wall",
            "node:app-shelf",
            "node:search",
            "state:discover",
            "responsive-rule:compact-shelf",
            "data-case:normal",
            "data-case:fallback",
            "data-case:error",
        ]
        receipt = {
            "schema_version": 1,
            "design_spec": {
                "path": "design-spec.json",
                "sha256": hashlib.sha256(self.spec_path.read_bytes()).hexdigest(),
            },
            "source_mappings": [
                {
                    "file": "app/src/main/java/example/StoreScreen.kt",
                    "symbols": ["AppShelf", "SearchField"],
                    "evidence": ["WideAppGrid", "CompactAppGrid"],
                    "design_refs": refs,
                }
            ],
            "implementation": implementation,
        }
        self.scratch.mkdir(parents=True, exist_ok=True)
        (self.scratch / "design_implementation_map.json").write_text(
            json.dumps(receipt, indent=2),
            encoding="utf-8",
        )

    def run_check(
        self,
        input_mode: str = "intent_only",
        visual_asset: str = "false",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--target",
                str(self.target),
                "--input-mode",
                input_mode,
                "--visual-asset",
                visual_asset,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def result(self) -> dict[str, Any]:
        return json.loads(
            (self.scratch / "design_fidelity_result.json").read_text(encoding="utf-8")
        )

    def test_matching_grid_and_responsive_contract_passes(self) -> None:
        self.write_receipt()

        completed = self.run_check()

        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertTrue(self.result()["passed"])
        self.assertEqual(9, self.result()["summary"]["mapped_refs"])

    def test_row_implementation_fails_against_grid_design(self) -> None:
        implementation = implementation_contract(self.spec)
        implementation["nodes"]["app-shelf"]["layout"]["mode"] = "row"
        self.write_receipt(implementation)

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertIn("/implementation/nodes/app-shelf/layout/mode", completed.stdout)
        self.assertIn("expected='grid' actual='row'", completed.stdout)

    def test_responsive_column_count_mismatch_fails(self) -> None:
        implementation = implementation_contract(self.spec)
        override = implementation["responsiveRules"]["compact-shelf"]["overrides"][0]
        override["layout"]["columns"] = 4
        self.write_receipt(implementation)

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertIn("responsiveRules/compact-shelf/overrides", completed.stdout)

    def test_component_and_initial_state_mismatches_fail(self) -> None:
        implementation = implementation_contract(self.spec)
        implementation["initialStateId"] = "details"
        implementation["nodes"]["search"]["component"] = "custom-search"
        self.write_receipt(implementation)

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertIn("/implementation/initialStateId", completed.stdout)
        self.assertIn("/implementation/nodes/search/component", completed.stdout)

    def test_missing_implementation_map_fails_when_spec_exists(self) -> None:
        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertIn("implementation map missing", completed.stdout)
        self.assertEqual(
            "missing_implementation_map",
            self.result()["errors"][0]["code"],
        )

    def test_non_object_design_spec_fails_without_traceback(self) -> None:
        self.spec_path.write_text("[]", encoding="utf-8")
        self.write_receipt()

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertNotIn("Traceback", completed.stdout)
        self.assertEqual("invalid_root", self.result()["errors"][0]["code"])
        self.assertEqual("/design_spec", self.result()["errors"][0]["path"])

    def test_non_object_implementation_map_fails_without_traceback(self) -> None:
        self.scratch.mkdir(parents=True, exist_ok=True)
        (self.scratch / "design_implementation_map.json").write_text(
            "[]",
            encoding="utf-8",
        )

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertNotIn("Traceback", completed.stdout)
        self.assertEqual("invalid_root", self.result()["errors"][0]["code"])
        self.assertEqual("/implementation_map", self.result()["errors"][0]["path"])

    def test_missing_node_source_mapping_fails(self) -> None:
        self.write_receipt()
        receipt_path = self.scratch / "design_implementation_map.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["source_mappings"][0]["design_refs"].remove("node:app-shelf")
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertIn("unmapped_design_ref", completed.stdout)
        self.assertIn("node:app-shelf", completed.stdout)

    def test_stale_design_hash_fails(self) -> None:
        self.write_receipt()
        self.spec["nodes"][0]["layout"]["columns"] = 3
        self.write_spec()

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertIn("stale_design_spec_hash", completed.stdout)

    def test_missing_spec_is_not_applicable_for_visual_reference(self) -> None:
        self.spec_path.unlink()

        completed = self.run_check("visual_reference")

        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertFalse(self.result()["applicable"])

    def test_missing_spec_is_not_applicable_for_visual_hybrid(self) -> None:
        self.spec_path.unlink()

        completed = self.run_check("hybrid", "true")

        self.assertEqual(0, completed.returncode, completed.stdout)
        self.assertFalse(self.result()["applicable"])

    def test_missing_spec_fails_for_no_visual_hybrid(self) -> None:
        self.spec_path.unlink()

        completed = self.run_check("hybrid")

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertTrue(self.result()["applicable"])

    def test_missing_spec_fails_for_designer_route(self) -> None:
        self.spec_path.unlink()

        completed = self.run_check()

        self.assertNotEqual(0, completed.returncode, completed.stdout)
        self.assertIn("required design-spec.json is missing", completed.stdout)


if __name__ == "__main__":
    unittest.main()
