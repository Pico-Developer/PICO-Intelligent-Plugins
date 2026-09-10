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

    def test_clickable_without_haptic_feedback_is_rejected(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.clickable
            import androidx.compose.foundation.LocalIndication
            import androidx.compose.foundation.interaction.MutableInteractionSource
            import androidx.compose.runtime.remember
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme {
                    Modifier.clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = LocalIndication.current,
                    ) { }
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("controllerHapticFeedback", result.stdout)

    def test_clickable_trailing_lambda_without_haptic_feedback_is_rejected(self) -> None:
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

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("controllerHapticFeedback", result.stdout)

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

    def test_commented_haptic_feedback_does_not_satisfy_clickable_requirement(self) -> None:
        self.write_ui(
            """
            import androidx.compose.foundation.clickable
            import androidx.compose.foundation.LocalIndication
            import androidx.compose.foundation.interaction.MutableInteractionSource
            import androidx.compose.runtime.remember
            import androidx.compose.ui.Modifier
            import com.pico.spatial.ui.design.PicoTheme
            // import com.pico.spatial.ui.foundation.haptic.controllerHapticFeedback

            fun Demo() {
                PicoTheme {
                    val interactionSource = remember { MutableInteractionSource() }
                    Modifier.clickable(
                        interactionSource = interactionSource,
                        indication = LocalIndication.current,
                    ) { }
                    // .controllerHapticFeedback(interactionSource = interactionSource)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("controllerHapticFeedback", result.stdout)

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

    def test_design_colors_reject_plain_pico_theme(self) -> None:
        self.write_design_colors([{"slot": "interaction", "hex": "#FF6B4A"}])
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme

            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("no PicoTheme(colorScheme = ...) injection", result.stdout)
        self.assertIn("#FF6B4A", result.stdout)

    def test_design_colors_reject_missing_exact_value(self) -> None:
        self.write_design_colors([{"slot": "interaction", "hex": "#FF6B4A"}])
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.systemColorScheme

            fun Demo() {
                val colors = systemColorScheme(context).copy(
                    interaction = Color(0xFF00AA00), // design-style: fixed-figma-color wrong value
                )
                PicoTheme(colorScheme = colors) { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("design color #FF6B4A", result.stdout)

    def test_design_colors_accept_exact_custom_scheme_mapping(self) -> None:
        self.write_design_colors(
            [
                {"slot": "interaction", "hex": "#FF6B4A"},
                {"slot": "passable", "hex": "#89E0B0"},
            ]
        )
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.systemColorScheme

            fun Demo() {
                val system = systemColorScheme(context)
                val colors = system.copy(
                    fillPrimary = system.fillPrimary,
                    fillSecondary = system.fillSecondary,
                    fillTertiary = system.fillTertiary,
                    fillLight = system.fillLight,
                    labelPrimaryLight = system.labelPrimaryLight,
                    labelPrimary = system.labelPrimary,
                    labelSecondary = system.labelSecondary,
                    labelTertiary = system.labelTertiary,
                    labelQuaternary = system.labelQuaternary,
                    lightenHover = system.lightenHover,
                    lightenPressed = system.lightenPressed,
                    error = system.error,
                    alert = system.alert,
                    interaction = Color(0xFFFF6B4A), // design-style: fixed-figma-color primary
                    passable = Color(0xFF89E0B0), // design-style: fixed-figma-color success
                    dividerLine = system.dividerLine,
                )
                PicoTheme(colorScheme = colors) { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

    def test_design_colors_reject_partial_system_color_scheme(self) -> None:
        self.write_design_colors([{"slot": "interaction", "hex": "#FF6B4A"}])
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
        self.assertIn("define all 16 ColorScheme roles", result.stdout)
        self.assertIn("fillPrimary", result.stdout)

    def test_design_colors_ignore_commented_out_mapping(self) -> None:
        self.write_design_colors([{"slot": "interaction", "hex": "#FF6B4A"}])
        self.write_ui(
            """
            import com.pico.spatial.ui.design.PicoTheme

            // PicoTheme(colorScheme = colors) { }
            // interaction = Color(0xFFFF6B4A)
            fun Demo() {
                PicoTheme { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("no PicoTheme(colorScheme = ...) injection", result.stdout)
        self.assertIn("design color #FF6B4A", result.stdout)

    def test_design_color_must_bind_to_declared_theme_role(self) -> None:
        self.write_design_colors([{"slot": "interaction", "hex": "#FF6B4A"}])
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.systemColorScheme

            fun Demo() {
                val decorative = Color(0xFFFF6B4A) // design-style: fixed-figma-color decoration
                val colors = systemColorScheme(context).copy(
                    interaction = Color(0xFF00AA00), // design-style: fixed-figma-color wrong role value
                )
                PicoTheme(colorScheme = colors) { }
            }
            """,
        )

        result = self.run_verifier()

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("mapped exactly to ColorScheme.interaction", result.stdout)

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

        result = self.run_verifier("--design-color", "interaction=#FF6B4A")

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("no PicoTheme(colorScheme = ...) injection", result.stdout)

    def test_cli_design_color_accepts_exact_mapping(self) -> None:
        self.write_ui(
            """
            import androidx.compose.ui.graphics.Color
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.systemColorScheme

            fun Demo() {
                val system = systemColorScheme(context)
                val colors = system.copy(
                    fillPrimary = system.fillPrimary,
                    fillSecondary = system.fillSecondary,
                    fillTertiary = system.fillTertiary,
                    fillLight = system.fillLight,
                    labelPrimaryLight = system.labelPrimaryLight,
                    labelPrimary = system.labelPrimary,
                    labelSecondary = system.labelSecondary,
                    labelTertiary = system.labelTertiary,
                    labelQuaternary = system.labelQuaternary,
                    lightenHover = system.lightenHover,
                    lightenPressed = system.lightenPressed,
                    error = system.error,
                    alert = system.alert,
                    interaction = Color(0xFFFF6B4A), // design-style: fixed-figma-color primary
                    passable = system.passable,
                    dividerLine = system.dividerLine,
                )
                PicoTheme(colorScheme = colors) { }
            }
            """,
        )

        result = self.run_verifier("--design-color", "interaction=#FF6B4A")

        self.assertEqual(0, result.returncode, result.stdout)

    def test_missing_color_source_is_an_error_not_a_silent_pass(self) -> None:
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

        self.assertNotEqual(0, result.returncode, result.stdout)
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

    def test_text_without_resolved_foreground_is_rejected(self) -> None:
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

        self.assertNotEqual(0, result.returncode, result.stdout)
        self.assertIn("R9", result.stdout)
        self.assertIn("PicoTheme does not provide LocalContentColor", result.stdout)

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

    def test_text_with_documented_component_inheritance_is_accepted(self) -> None:
        self.write_ui(
            """
            import com.pico.spatial.ui.design.Button
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.Text

            fun Demo() {
                PicoTheme {
                    Button(onClick = {}) {
                        // design-style: inherited-content-color Button
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
            import androidx.compose.foundation.border
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
                        .border(1.dp, PicoTheme.colorScheme.dividerLine, shape)
                }
            }
            """,
        )

        result = self.run_verifier()

        self.assertEqual(0, result.returncode, result.stdout)

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
