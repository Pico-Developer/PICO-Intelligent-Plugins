#!/usr/bin/env python3
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

    def run_verifier(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(SCRIPT_PATH), str(self.module_dir)],
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


if __name__ == "__main__":
    unittest.main()
