#!/usr/bin/env python3
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "verify-design-style.sh"


class VerifyDesignStyleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.module_dir = Path(self.temp_dir.name) / "demo"
        self.src_dir = self.module_dir / "src/main/kotlin/com/example"
        self.src_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_ui(self, body: str) -> None:
        (self.src_dir / "Demo.kt").write_text(body, encoding="utf-8")

    def write_design_colors(self, overrides: list[dict[str, str]]) -> None:
        scratch_dir = self.module_dir / ".scratch"
        scratch_dir.mkdir()
        (scratch_dir / "evidence_packet.json").write_text(
            json.dumps(
                {
                    "facts": {
                        "visual_tokens": {
                            "theme_overrides": overrides,
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

    def write_design_spec(self, nodes: list[dict[str, object]]) -> Path:
        scratch_dir = self.module_dir / ".scratch"
        scratch_dir.mkdir(exist_ok=True)
        path = scratch_dir / "design-spec.json"
        path.write_text(json.dumps({"nodes": nodes}), encoding="utf-8")
        return path

    def run_verifier(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        args = ["bash", str(SCRIPT_PATH), str(self.module_dir), *extra_args]
        # A fixture with no evidence packet and no explicit --design-color is,
        # by definition, a caller with no authoritative design colors. The
        # verifier requires that to be stated rather than inferred, so declare
        # it here instead of letting R1b fail every unrelated rule's test.
        declares_colors = any(arg.startswith("--design-color") for arg in extra_args)
        has_evidence = (self.module_dir / ".scratch" / "evidence_packet.json").is_file()
        if not declares_colors and not has_evidence and "--no-design-colors" not in extra_args:
            args.append("--no-design-colors")
        return subprocess.run(
            args,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def test_clickable_without_explicit_indication_or_haptics_is_accepted(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.clickable
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo(go: () -> Unit) {
                PicoTheme {
                    Modifier.clickable { go() }
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_clickable_with_shared_haptic_feedback_is_accepted(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.clickable
            import androidx.compose.foundation.LocalIndication
            import androidx.compose.foundation.interaction.MutableInteractionSource
            import androidx.compose.runtime.remember
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.foundation.haptic.controllerHapticFeedback

            fun Demo() {
                PicoTheme {
                    val interactionSource = remember { MutableInteractionSource() }
                    Modifier
                        .clickable(
                            interactionSource = interactionSource,
                            indication = LocalIndication.current,
                        ) { }
                        .controllerHapticFeedback(interactionSource = interactionSource)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_direct_hoverable_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.hoverable
            import androidx.compose.foundation.interaction.MutableInteractionSource
            import androidx.compose.runtime.remember
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    val source = remember { MutableInteractionSource() }
                    Modifier.hoverable(source)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("R3 custom hover via hoverable()", result.stdout)

    def test_chained_hoverable_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.hoverable
            import androidx.compose.foundation.interaction.MutableInteractionSource
            import androidx.compose.foundation.layout.padding
            import androidx.compose.runtime.remember
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.unit.dp
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    val source = remember { MutableInteractionSource() }
                    Modifier.padding(4.dp).hoverable(source)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("R3 custom hover via hoverable()", result.stdout)

    def test_material_v1_component_import_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.material.Button
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    Button(onClick = {}) { }
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("Material (v1) component import", result.stdout)

    def test_material3_component_imports_are_rejected(self) -> None:
        for component in (
            "Card",
            "Surface",
            "Scaffold",
            "TopAppBar",
            "NavigationBar",
            "FloatingActionButton",
        ):
            with self.subTest(component=component):
                self.write_ui(
                    f"""
                    import androidx.compose.material3.{component}
                    import com.pico.spatial.ui.design.PicoTheme

                    fun Demo() {{
                        PicoTheme {{
                            {component} {{ }}
                        }}
                    }}
                    """,
                )

                result = self.run_verifier()

                self.assertNotEqual(0, result.returncode, result.stdout)
                self.assertIn("Material3 package import", result.stdout)

    def test_material_v1_card_surface_scaffold_imports_are_rejected(self) -> None:
        for component in ("Card", "Surface", "Scaffold"):
            with self.subTest(component=component):
                self.write_ui(
                    f"""
                    import androidx.compose.material.{component}
                    import com.pico.spatial.ui.design.PicoTheme

                    fun Demo() {{
                        PicoTheme {{
                            {component} {{ }}
                        }}
                    }}
                    """,
                )

                result = self.run_verifier()

                self.assertNotEqual(0, result.returncode, result.stdout)
                self.assertIn("Material package import", result.stdout)

    def test_material_icons_import_is_rejected_as_material_package(self) -> None:
        self.write_ui(
            """
            import androidx.compose.material.icons.Icons
            import androidx.compose.material.icons.filled.Add
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.Icon

            fun Demo() {
                PicoTheme {
                    Icon(imageVector = Icons.Filled.Add, contentDescription = null)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("Material package import", result.stdout)

    def test_design_colors_accept_plain_pico_theme_with_app_owned_token(self) -> None:
        self.write_design_colors([{"slot": "brandAccent", "hex": "#FF6B4A"}])
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme

            val BrandAccent = Color(0xFFFF6B4A) // design-style: fixed-figma-color brandAccent

            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_design_colors_reject_missing_exact_value(self) -> None:
        self.write_design_colors([{"slot": "brandAccent", "hex": "#FF6B4A"}])
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme

            val BrandAccent = Color(0xFF00AA00) // design-style: fixed-figma-color wrong value

            fun Demo() { PicoTheme { } }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("design color #FF6B4A", result.stdout)

    def test_design_colors_accept_exact_app_owned_tokens(self) -> None:
        self.write_design_colors(
            [
                {"slot": "brandAccent", "hex": "#FF6B4A"},
                {"slot": "successAccent", "hex": "#89E0B0"},
            ]
        )
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme

            val BrandAccent = Color(0xFFFF6B4A) // design-style: fixed-figma-color brandAccent
            val SuccessAccent = Color(0xFF89E0B0) // design-style: fixed-figma-color successAccent

            fun Demo() { PicoTheme { } }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_native_color_scheme_copy_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.systemColorScheme

            fun Demo() {
                val colors = systemColorScheme(context).copy(
                    interaction = Color(0xFFFF6B4A),
                )
                PicoTheme(colorScheme = colors) { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("modifies the native SpatialUI ColorScheme", result.stdout)

    def test_pico_theme_color_scheme_override_after_nested_call_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.layout.padding
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.unit.dp
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.systemColorScheme

            val customScheme = systemColorScheme()

            fun Demo() {
                PicoTheme(
                    modifier = Modifier.padding(8.dp),
                    colorScheme = customScheme,
                ) { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("modifies the native SpatialUI ColorScheme", result.stdout)

    def test_design_colors_ignore_commented_out_mapping(self) -> None:
        self.write_design_colors([{"slot": "brandAccent", "hex": "#FF6B4A"}])
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme

            // val BrandAccent = Color(0xFFFF6B4A)
            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("custom design color #FF6B4A", result.stdout)

    def test_design_color_cannot_use_native_role_name(self) -> None:
        self.write_design_colors([{"slot": "interaction", "hex": "#FF6B4A"}])
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme

            val Accent = Color(0xFFFF6B4A) // design-style: fixed-figma-color accent

            fun Demo() { PicoTheme { } }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("cannot be overridden", result.stdout)

    def test_cli_design_color_enforces_r1b_without_evidence_packet(self) -> None:
        # The code_only flow has no .scratch/evidence_packet.json at all. R1b
        # must still fire when the caller forwards the design colors directly.
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = self.run_verifier("--design-color", "brandAccent=#FF6B4A")

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("custom design color #FF6B4A", result.stdout)

    def test_cli_design_color_accepts_exact_app_owned_token(self) -> None:
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme

            val BrandAccent = Color(0xFFFF6B4A) // design-style: fixed-figma-color brandAccent

            fun Demo() { PicoTheme { } }
            """,
        )

        result = self.run_verifier("--design-color", "brandAccent=#FF6B4A")

        self.assertEqual(0, result.returncode, result.stdout)

    def test_cli_design_color_rejects_non_lower_camel_case_token_names(self) -> None:
        for token in ("", "lift-shadow", "lift_shadow", "LiftShadow", "_shadow", "9shadow"):
            with self.subTest(token=token):
                result = self.run_verifier(
                    "--design-color",
                    f"{token}=#00000066",
                )

                self.assertEqual(2, result.returncode, result.stdout)
                self.assertIn(
                    f"invalid --design-color token name '{token}'",
                    result.stdout,
                )
                self.assertIn("expected lowerCamelCase", result.stdout)
                self.assertNotIn("invalid --design-color color value", result.stdout)

    def test_cli_design_color_reports_invalid_color_value(self) -> None:
        for color in ("", "000000", "#000", "#0000000", "#GG0000", "#000000000"):
            with self.subTest(color=color):
                result = self.run_verifier(
                    "--design-color",
                    f"liftShadow={color}",
                )

                self.assertEqual(2, result.returncode, result.stdout)
                self.assertIn(
                    f"invalid --design-color color value '{color}' for token 'liftShadow'",
                    result.stdout,
                )
                self.assertIn("#RRGGBB or #AARRGGBB", result.stdout)
                self.assertNotIn("invalid --design-color token name", result.stdout)

    def test_cli_design_color_reports_missing_separator(self) -> None:
        result = self.run_verifier(
            "--design-color",
            "liftShadow#00000066",
        )

        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("missing '=' separator", result.stdout)

    def test_design_spec_requires_value_before_next_option(self) -> None:
        self.write_ui("fun Demo() { PicoTheme { } }")

        result = subprocess.run(
            [
                "bash",
                str(SCRIPT_PATH),
                str(self.module_dir),
                "--design-spec",
                "--no-design-colors",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("--design-spec needs a path", result.stdout)

    def test_missing_color_source_is_an_invocation_error(self) -> None:
        # Regression guard: before --design-color existed the verifier exited 0
        # when no evidence packet was found, which silently disabled R1b for any
        # flow that did not write one. Absence must now be stated explicitly.
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = subprocess.run(
            ["bash", str(SCRIPT_PATH), str(self.module_dir)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("--no-design-colors", result.stdout)

    def test_no_design_colors_flag_skips_r1b(self) -> None:
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = self.run_verifier("--no-design-colors")

        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("R1b skipped", result.stdout)

    def test_text_without_explicit_foreground_is_not_rejected(self) -> None:
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.Text

            fun Demo() {
                PicoTheme {
                    Text(
                        "Dark-surface title",
                        style = PicoTheme.typography.titleLarge,
                    )
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)
        self.assertNotIn("R9", result.stdout)

    def test_text_with_explicit_semantic_color_is_accepted(self) -> None:
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.Text

            fun Demo() {
                PicoTheme {
                    Text(
                        "Dark-surface title",
                        style = PicoTheme.typography.titleLarge,
                        color = PicoTheme.colorScheme.labelPrimary,
                    )
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_component_slot_inheritance_needs_no_annotation(self) -> None:
        self.write_ui(
            """
            import com.pico.spatial.ui.design.Button
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.Text

            fun Demo() {
                PicoTheme {
                    Button(onClick = {}) {
                        Text("Start")
                    }
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_conflicting_design_color_flags_are_rejected(self) -> None:
        self.write_ui("fun Demo() { PicoTheme { } }")

        result = self.run_verifier("--design-color", "interaction=#FF6B4A", "--no-design-colors")

        self.assertEqual(2, result.returncode, result.stdout)

    def test_material_with_rounded_border_but_no_clip_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.border
            import androidx.compose.foundation.shape.RoundedCornerShape
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.unit.dp
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.foundation.material.backgroundMaterial
            import com.pico.spatial.ui.platform.Material

            fun Demo() {
                PicoTheme {
                    Modifier
                        .backgroundMaterial(enable = true, style = Material.Regular)
                        .border(1.dp, PicoTheme.colorScheme.dividerLine, RoundedCornerShape(8.dp))
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("R4b", result.stdout)
        self.assertIn("must be preceded by .clip(shape)", result.stdout)

    def test_material_clipped_before_background_is_accepted(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.shape.RoundedCornerShape
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.draw.clip
            import androidx.compose.ui.unit.dp
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.foundation.material.backgroundMaterial
            import com.pico.spatial.ui.platform.Material

            fun Demo() {
                PicoTheme {
                    val shape = RoundedCornerShape(8.dp)
                    Modifier
                        .clip(shape)
                        .backgroundMaterial(enable = true, style = Material.Regular)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_app_authored_modifier_border_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.border
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.unit.dp
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    Modifier.border(1.dp, PicoTheme.colorScheme.dividerLine)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("R10", result.stdout)
        self.assertIn("Modifier.border", result.stdout)

    def test_app_authored_border_stroke_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.BorderStroke
            import androidx.compose.ui.unit.dp
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    BorderStroke(1.dp, PicoTheme.colorScheme.dividerLine)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("R10", result.stdout)
        self.assertIn("BorderStroke", result.stdout)

    def test_unmapped_background_is_rejected_when_design_spec_is_supplied(self) -> None:
        spec = self.write_design_spec(
            [
                {
                    "id": "detail-pane",
                    "kind": "text",
                    "appearance": {"fill": "fillSecondary"},
                }
            ]
        )
        self.write_ui(
            """
            import androidx.compose.foundation.background
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    Modifier.background(PicoTheme.colorScheme.fillSecondary)
                }
            }
            """,
        )

        result = self.run_verifier("--design-spec", str(spec))

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("R10", result.stdout)
        self.assertIn("has no nearby", result.stdout)

    def test_background_mapped_to_surface_owning_design_node_is_accepted(self) -> None:
        spec = self.write_design_spec(
            [
                {
                    "id": "detail-pane",
                    "kind": "text",
                    "appearance": {"fill": "fillSecondary"},
                }
            ]
        )
        self.write_ui(
            """
            import androidx.compose.foundation.background
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    Modifier
                        // design-style: design-surface detail-pane
                        .background(PicoTheme.colorScheme.fillSecondary)
                }
            }
            """,
        )

        result = self.run_verifier("--design-spec", str(spec))

        self.assertEqual(0, result.returncode, result.stdout)

    def test_duplicate_background_marker_is_rejected(self) -> None:
        spec = self.write_design_spec(
            [
                {
                    "id": "event-item",
                    "kind": "text",
                    "appearance": {"fill": "fillSecondary"},
                }
            ]
        )
        self.write_ui(
            """
            import androidx.compose.foundation.background
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    Modifier
                        // design-style: design-surface event-item
                        .background(PicoTheme.colorScheme.fillSecondary)
                    Modifier
                        // design-style: design-surface event-item
                        .background(PicoTheme.colorScheme.fillSecondary)
                }
            }
            """,
        )

        result = self.run_verifier("--design-spec", str(spec))

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("implemented by 2 background calls", result.stdout)

    def test_background_material_is_rejected_when_design_spec_is_supplied(self) -> None:
        spec = self.write_design_spec(
            [
                {
                    "id": "detail-pane",
                    "kind": "layout",
                    "appearance": {"fill": "fillSecondary"},
                }
            ]
        )
        self.write_ui(
            """
            import androidx.compose.foundation.shape.RoundedCornerShape
            import androidx.compose.ui.Modifier
            import androidx.compose.ui.draw.clip
            import androidx.compose.ui.unit.dp
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.foundation.material.backgroundMaterial
            import com.pico.spatial.ui.platform.Material

            fun Demo() {
                PicoTheme {
                    Modifier
                        .clip(RoundedCornerShape(8.dp))
                        // design-style: design-surface detail-pane
                        .backgroundMaterial(enable = true, style = Material.Regular)
                }
            }
            """,
        )

        result = self.run_verifier("--design-spec", str(spec))

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("backgroundMaterial is not allowed", result.stdout)

    def test_material_fields_in_design_spec_are_rejected(self) -> None:
        spec = self.write_design_spec(
            [
                {
                    "id": "detail-pane",
                    "kind": "layout",
                    "appearance": {"material": "none"},
                }
            ]
        )
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = self.run_verifier("--design-spec", str(spec))

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("declares material", result.stdout)

    def test_background_marker_for_transparent_node_is_rejected(self) -> None:
        spec = self.write_design_spec([{"id": "detail-pane", "kind": "layout"}])
        self.write_ui(
            """
            import androidx.compose.foundation.background
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    Modifier
                        // design-style: design-surface detail-pane
                        .background(PicoTheme.colorScheme.fillSecondary)
                }
            }
            """,
        )

        result = self.run_verifier("--design-spec", str(spec))

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("declares no fill", result.stdout)

    def test_structural_fill_node_is_rejected(self) -> None:
        spec = self.write_design_spec(
            [
                {
                    "id": "main-region",
                    "kind": "domain_visual",
                    "appearance": {"fill": "fillSecondary"},
                }
            ]
        )
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = self.run_verifier("--design-spec", str(spec))

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("structural regions must remain transparent", result.stdout)

    def test_unmapped_spatialui_card_is_rejected_when_design_spec_is_supplied(self) -> None:
        spec = self.write_design_spec([])
        self.write_ui(
            """
            import com.pico.spatial.ui.design.Card
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    Card(onClick = {}) { }
                }
            }
            """,
        )

        result = self.run_verifier("--design-spec", str(spec))

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("Card has no nearby", result.stdout)

    def test_explicit_rectangular_material_is_accepted(self) -> None:
        self.write_ui(
            """
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.foundation.material.backgroundMaterial
            import com.pico.spatial.ui.platform.Material

            fun Demo() {
                PicoTheme {
                    Modifier
                        // design-style: rectangular-material edge-to-edge status layer
                        .backgroundMaterial(enable = true, style = Material.Regular)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)


if __name__ == "__main__":
    unittest.main()
