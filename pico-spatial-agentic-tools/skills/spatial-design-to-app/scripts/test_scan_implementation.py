#!/usr/bin/env python3
import importlib.util
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "scan_implementation.py"
SKILL_DIR = SCRIPT_PATH.parent.parent
WEB_TO_COMPOSE_PATH = SKILL_DIR / "references/spatialui-web-to-compose.md"
RESTORATION_ANTI_PATTERNS_PATH = SKILL_DIR / "references/restoration-anti-patterns.md"
DESIGNER_RUNTIME_PATH = (
    SKILL_DIR.parent / "pico-spatial-app-designer/design/design-reference/runtime/components.js"
)


def load_scanner_module():
    spec = importlib.util.spec_from_file_location("scan_implementation", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load scanner module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


WINDOW_MANIFEST = """
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <application>
    <activity android:name=".MainActivity">
      <meta-data android:name="pico.spatial.windowcontainer.id" android:value="demo" />
      <meta-data android:name="pico.spatial.windowcontainer.style" android:value="1" />
    </activity>
  </application>
</manifest>
"""

STAGE_MANIFEST = """
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <application>
    <activity android:name=".MainActivity">
      <meta-data android:name="pico.spatial.stage.id" android:value="demo" />
      <meta-data android:name="pico.spatial.stage.style" android:value="1" />
      <meta-data android:name="pico.spatial.stage.immersion" android:value="0" />
      <meta-data android:name="pico.spatial.stage.immersion_min" android:value="0" />
      <meta-data android:name="pico.spatial.stage.immersion_max" android:value="0" />
    </activity>
  </application>
</manifest>
"""


class ScanImplementationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = Path(self.temp_dir.name) / "generated-app"
        self.scratch_dir = self.target_dir / ".scratch"
        self.src_dir = self.target_dir / "src/main/java/com/example/app"
        self.scratch_dir.mkdir(parents=True)
        self.src_dir.mkdir(parents=True)
        (self.target_dir / "src/main").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_manifest(self, body: str = WINDOW_MANIFEST) -> None:
        (self.target_dir / "src/main/AndroidManifest.xml").write_text(body, encoding="utf-8")

    def write_kt(self, body: str, name: str = "Main.kt") -> None:
        (self.src_dir / name).write_text(body, encoding="utf-8")

    def sources(self, scanner):
        return [
            (p, scanner.read_text_safe(p)) for p in scanner.collect_kotlin_files(self.target_dir)
        ]

    # ---- component vocabulary -------------------------------------------

    def test_component_vocabulary_is_parsed_and_sane(self) -> None:
        """Sentinel: the vocabulary is parsed from the reference docs, so a
        parser or docs change that empties it would silently disable both the
        component floor and the invented-name check."""
        scanner = load_scanner_module()
        allowed, forbidden = scanner.load_component_vocabulary()

        for name in ("SideNavigation", "TabBar", "SearchField", "Button", "Subwindow"):
            self.assertIn(name, allowed, msg=f"{name} should be a known SpatialUI built-in")
        # Generic primitives must never count as SpatialUI-built-in evidence.
        for name in ("Box", "Column", "Row", "Text"):
            self.assertNotIn(name, allowed)
        for name in ("SpatialButton", "XRPanel"):
            self.assertIn(name, forbidden)
        # `Box` is the documented fallback, not a banned name.
        self.assertNotIn("Box", forbidden)

    def test_web_to_compose_mapping_covers_designer_catalog(self) -> None:
        scanner = load_scanner_module()
        allowed, _ = scanner.load_component_vocabulary()
        parity_text = DESIGNER_RUNTIME_PATH.read_text(encoding="utf-8")
        mapping_text = WEB_TO_COMPOSE_PATH.read_text(encoding="utf-8")

        runtime_tags = set(re.findall(r"(?:register|define)\('(sui-[^']+)'", parity_text))
        mapping_rows = re.findall(
            r"^\|\s*`(sui-[^`]+)`\s*\|\s*`([A-Z][A-Za-z0-9]*)`\s*\|",
            mapping_text,
            re.MULTILINE,
        )
        mapped_tags = {tag for tag, _ in mapping_rows}

        # Every mapped component must exist in the maintained runtime.
        # Runtime-only preview shells/helpers do not require native component mappings.
        native_only = {"sui-augment", "sui-stereo-image"}
        self.assertEqual(mapped_tags - runtime_tags, native_only)
        legal_components = allowed | scanner.GENERIC_PRIMITIVES
        for tag, component in mapping_rows:
            self.assertIn(
                component,
                legal_components,
                msg=f"{tag} maps to {component}, which is absent from the whitelist",
            )

    def test_clickable_list_item_mapping_preserves_list_item_root(self) -> None:
        mapping_text = WEB_TO_COMPOSE_PATH.read_text(encoding="utf-8")

        self.assertRegex(
            mapping_text,
            r"(?s)ListItem\(\s+modifier = Modifier.*?\.clickable\(",
        )
        self.assertIn("Do not convert it to `Button { ListItem(...) }`", mapping_text)
        self.assertIn("SpatialUI 6.1.9 `ListItem` already", mapping_text)

    def test_titlebar_and_button_semantics_are_documented(self) -> None:
        mapping_text = WEB_TO_COMPOSE_PATH.read_text(encoding="utf-8")
        anti_patterns = RESTORATION_ANTI_PATTERNS_PATH.read_text(encoding="utf-8")

        self.assertIn("titleAlignment = TitleAlignment.Center", mapping_text)
        self.assertIn("titleAlignment = TitleAlignment.CenterInBar", mapping_text)
        self.assertIn("Command buttons are not content containers", mapping_text)
        self.assertIn("Button used as a content container", anti_patterns)
        self.assertIn("spatialHoverEffect()", anti_patterns)

    def test_empty_vocabulary_fails_instead_of_passing_silently(self) -> None:
        scanner = load_scanner_module()
        scanner.load_component_vocabulary = lambda: (set(), set())

        result = scanner.check_spatialui_component_floor([], "default")

        self.assertFalse(result["passed"])
        self.assertIn("vocabulary", "\n".join(result["failures"]))

    # ---- container inference from manifest --------------------------------

    def test_container_inferred_from_manifest_style_values(self) -> None:
        scanner = load_scanner_module()
        cases = {
            ("pico.spatial.windowcontainer", "1"): "ON_PLAIN",
            ("pico.spatial.windowcontainer", "2"): "IN_VOLUME",
            ("pico.spatial.stage", "1"): "STAGE_MIXED",
            ("pico.spatial.stage", "2"): "STAGE_PROGRESSIVE",
            ("pico.spatial.stage", "3"): "STAGE_FULL",
        }
        for (prefix, style), expected in cases.items():
            with self.subTest(prefix=prefix, style=style):
                manifest = (
                    "<manifest><application>"
                    f'<meta-data android:name="{prefix}.id" android:value="demo" />'
                    f'<meta-data android:name="{prefix}.style" android:value="{style}" />'
                    "</application></manifest>"
                )
                container, evidence = scanner.infer_container(
                    [(Path("AndroidManifest.xml"), manifest)], []
                )
                self.assertEqual(expected, container)
                self.assertTrue(evidence)

    def test_container_falls_back_to_code_root_without_manifest(self) -> None:
        scanner = load_scanner_module()
        sources = [(Path("Main.kt"), "fun mainApp() { DefaultStage { Scene() } }")]

        container, _ = scanner.infer_container([], sources)

        self.assertEqual("STAGE_MIXED", container)

    # ---- root detection ---------------------------------------------------

    def test_allows_default_window_root_with_secondary_stage(self) -> None:
        """DefaultWindowContainer + Stage(id=...) is a valid single-root app
        (shared-space default + open immersive stage on demand), not an illegal
        mixed root. Verified against SpatialAppSample/stagerendering/Main.kt."""
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer {
                    ControlPanel(Modifier.windowConstraints(width = 400.dp, height = 350.dp))
                }
                Stage(id = MIXED_STAGE_ID) { MainScene() }
                Stage(id = FULL_STAGE_ID) { MainScene() }
            }
            """
        )

        sources = self.sources(scanner)
        detected, _ = scanner.detect_root_kind(sources)
        self.assertEqual(detected, "window")
        root_result = scanner.check_root_match("ON_PLAIN", sources)
        self.assertTrue(
            root_result["passed"],
            msg=f"expected valid single-root, got failures: {root_result['failures']}",
        )

    def test_rejects_two_default_roots_as_mixed(self) -> None:
        """Two coexisting DEFAULT roots (DefaultWindowContainer + DefaultStage)
        remain illegal — the only real mixed-root case."""
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer { MainPanel() }
                DefaultStage { ImmersiveScene() }
            }
            """
        )

        sources = self.sources(scanner)
        detected, _ = scanner.detect_root_kind(sources)
        self.assertEqual(detected, "mixed")
        root_result = scanner.check_root_match("ON_PLAIN", sources)
        self.assertFalse(root_result["passed"])
        self.assertIn("only one default root", "\n".join(root_result["failures"]))

    def test_reports_code_root_that_contradicts_manifest(self) -> None:
        scanner = load_scanner_module()
        self.write_kt("fun mainApp() { DefaultStage { Scene() } }")

        result = scanner.check_root_match("ON_PLAIN", self.sources(scanner))

        self.assertFalse(result["passed"])
        self.assertIn("code root is stage", "\n".join(result["failures"]))

    # ---- stage API legality ----------------------------------------------

    def test_stage_api_in_secondary_stage_warns_not_fails(self) -> None:
        """Stage-only APIs in a window-default app do NOT hard-fail when a
        secondary Stage(id=...) exists; they degrade to a scope-verify warning."""
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer { ControlPanel() }
                Stage(id = SCAN_STAGE_ID) {
                    val mgr = WorldTrackingManager()
                    scene.rayCast(ray)
                }
            }
            """
        )

        result = scanner.check_stage_api_legality("ON_PLAIN", self.sources(scanner))

        self.assertTrue(result["passed"])
        self.assertTrue(result["warnings"])

    def test_stage_api_without_any_stage_still_fails(self) -> None:
        """A pure window app using Stage-only APIs with NO stage block still fails."""
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer {
                    val mgr = WorldTrackingManager()
                }
            }
            """
        )

        result = scanner.check_stage_api_legality("ON_PLAIN", self.sources(scanner))

        self.assertFalse(result["passed"])
        self.assertIn("no secondary", "\n".join(result["failures"]))

    def test_stage_api_is_legal_in_a_stage_container(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest(STAGE_MANIFEST)
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultStage { val mgr = WorldTrackingManager() }
            }
            """
        )

        summary = scanner.scan(self.target_dir)

        self.assertEqual("STAGE_MIXED", summary["container"])
        self.assertTrue(summary["checks"]["stage_api_legality"]["passed"])

    # ---- SpatialUI component usage ---------------------------------------

    def test_warns_when_product_ui_avoids_spatialui_builtins(self) -> None:
        """Hand-rolled Box + Text + clickable instead of SpatialUI built-ins.
        Warns rather than fails: the floor is a heuristic."""
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            import com.pico.spatial.ui.design.PicoTheme
            import com.pico.spatial.ui.design.Text

            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer {
                    PicoTheme {
                        Column {
                            Row(Modifier.clickable { }) { Text("Home") }
                            Text("Launch")
                        }
                    }
                }
            }
            """
        )

        summary = scanner.scan(self.target_dir)

        self.assertTrue(summary["passed"])
        warnings = "\n".join(summary["warnings_or_explicit_none"])
        self.assertIn("spatialui_component_floor", warnings)

    def test_accepts_ui_built_from_spatialui_components(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()
        (self.scratch_dir / "design-spec.json").write_text('{"nodes": []}', encoding="utf-8")
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer { PicoTheme { Screen() } }
            }

            @Composable
            private fun Screen() {
                SideNavigation {
                    SideNavigationItem(selected = true, modifier = Modifier.heightIn(min = 48.dp)) { Text("Home") }
                }
                SearchField(value = "", onValueChange = {})
                Button(onClick = {}) { Text("Start") }
            }
            """
        )

        summary = scanner.scan(self.target_dir)

        self.assertEqual("none", summary["warnings_or_explicit_none"])
        self.assertTrue(summary["passed"])

    def test_patch_profile_lowers_the_component_floor(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            @Composable
            private fun Patched() {
                SearchField(value = "", onValueChange = {})
            }
            """
        )

        default_run = scanner.check_spatialui_component_floor(self.sources(scanner), "default")
        patch_run = scanner.check_spatialui_component_floor(self.sources(scanner), "patch")

        self.assertTrue(default_run["warnings"])
        self.assertFalse(patch_run["warnings"])

    def test_rejects_invented_sdk_component_names(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer {
                    PicoTheme { SpatialButton(onClick = {}) { Text("Go") } }
                }
            }
            """
        )

        summary = scanner.scan(self.target_dir)

        self.assertFalse(summary["passed"])
        self.assertIn("SpatialButton", "\n".join(summary["failures_or_explicit_none"]))

    def test_composable_named_screen_is_not_an_invented_component(self) -> None:
        """`Screen` is banned as a Spatial container type, but HomeScreen()-style
        composables are ordinary and must not be flagged."""
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer { PicoTheme { HomeScreen() } }
            }

            @Composable
            private fun HomeScreen() { Button(onClick = {}) { Text("Go") } }
            """
        )

        result = scanner.check_invented_component_names(self.sources(scanner))

        self.assertTrue(result["passed"], msg=result["failures"])

    def test_accepts_center_in_bar_for_title_only(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Header() {
                TitleBar(
                    titleAlignment = TitleAlignment.CenterInBar,
                    title = { Text("Store") },
                )
            }
            """
        )

        result = scanner.check_titlebar_alignment(self.sources(scanner))

        self.assertTrue(result["passed"])
        self.assertFalse(result["warnings"])

    def test_warns_for_center_title_only(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Header() {
                TitleBar(
                    titleAlignment = TitleAlignment.Center,
                    title = { Text("Store") },
                )
            }
            """
        )

        result = scanner.check_titlebar_alignment(self.sources(scanner))

        self.assertTrue(result["passed"])
        self.assertFalse(result["failures"])
        self.assertIn("TitleAlignment.CenterInBar", "\n".join(result["warnings"]))

    def test_existing_module_warns_for_center_title_only_without_blocking(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Header() {
                TitleBar(
                    titleAlignment = TitleAlignment.Center,
                    title = { Text("Existing") },
                )
            }
            """
        )

        result = scanner.check_titlebar_alignment(
            self.sources(scanner), generation_mode="existing_module"
        )

        self.assertTrue(result["passed"])
        self.assertFalse(result["failures"])
        self.assertIn("existing-module", "\n".join(result["warnings"]))

    def test_alignment_distinguishes_search_from_title_only_in_same_file(self) -> None:
        scanner = load_scanner_module()
        self.write_kt("""
            @Composable fun Header() {
                TitleBar(titleAlignment = TitleAlignment.CenterInBar,
                         title = { Column { Text("Title"); Text("Subtitle") } })
                TitleBar(titleAlignment = TitleAlignment.Center,
                         title = { Row { Text("Store"); SearchField(value = "") } })
                TitleBar(titleAlignment = TitleAlignment.CenterInBar,
                         title = { Row { Text("Store"); SearchField(value = "") } })
                TitleBar(titleAlignment = TitleAlignment.CenterInBar,
                         title = { CustomHeader() })
            }
        """)
        result = scanner.check_titlebar_alignment(self.sources(scanner))
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("search-containing", result["warnings"][0])
        self.assertEqual(len(result["evidence"]["compositions"]), 3)

    def test_titlebar_alignment_ignores_search_names_in_text_and_comments(self) -> None:
        scanner = load_scanner_module()
        self.write_kt("""
            @Composable fun Header() {
                TitleBar(titleAlignment = TitleAlignment.CenterInBar,
                    title = { Text("SearchField()", maxLines = 1) /* SearchField() */ })
                TitleBar(title = { Text("Title") })
            }
        """)
        result = scanner.check_titlebar_alignment(self.sources(scanner))
        self.assertTrue(result["passed"])
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("implicit or dynamic", result["warnings"][0])
        self.assertEqual(
            [item["expected"] for item in result["evidence"]["compositions"]],
            ["CenterInBar", "CenterInBar"],
        )

    def test_titlebar_actions_use_remaining_space_alignment(self) -> None:
        scanner = load_scanner_module()
        for slot in ("leadingActions", "trailingActions"):
            for alignment in ("Center", "CenterInBar"):
                with self.subTest(slot=slot, alignment=alignment):
                    self.write_kt(f"""
                        @Composable fun Header() {{
                            TitleBar(titleAlignment = TitleAlignment.{alignment},
                                title = {{ Text("Month") }},
                                {slot} = {{ Button(onClick = {{}}) {{ Text("Next") }} }})
                        }}
                    """)
                    result = scanner.check_titlebar_alignment(self.sources(scanner))
                    self.assertEqual(result["evidence"]["compositions"][0]["expected"], "Center")
                    self.assertEqual(len(result["warnings"]), int(alignment == "CenterInBar"))

    def test_titlebar_empty_actions_keep_text_only_alignment(self) -> None:
        scanner = load_scanner_module()
        self.write_kt("""
            @Composable fun Header() {
                TitleBar(titleAlignment = TitleAlignment.CenterInBar,
                    title = { Text("Month") },
                    leadingActions = {}, trailingActions = { /* empty */ })
            }
        """)
        result = scanner.check_titlebar_alignment(self.sources(scanner))
        self.assertFalse(result["warnings"])
        self.assertEqual(result["evidence"]["compositions"][0]["expected"], "CenterInBar")

    def test_titlebar_compound_title_uses_center(self) -> None:
        scanner = load_scanner_module()
        self.write_kt("""
            @Composable fun Header() {
                TitleBar(titleAlignment = TitleAlignment.Center,
                    title = { Row { Icon(imageVector = icon); Text("Month") } })
            }
        """)
        result = scanner.check_titlebar_alignment(self.sources(scanner))
        self.assertFalse(result["warnings"])
        self.assertEqual(result["evidence"]["compositions"][0]["expected"], "Center")

    def test_warns_when_titlebar_search_omits_weighted_space(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Header() {
                TitleBar(
                    title = {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(24.dp),
                        ) {
                            Text("Store")
                            SearchField(value = "", onValueChange = {})
                        }
                    },
                )
            }
            """
        )

        result = scanner.check_titlebar_search_layout(self.sources(scanner))

        self.assertTrue(result["passed"])
        self.assertIn("Spacer(Modifier.weight(1f))", "\n".join(result["warnings"]))

    def test_accepts_canonical_titlebar_search_layout(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Header() {
                TitleBar(
                    title = {
                        Row(modifier = Modifier.fillMaxWidth()) {
                            Text("Store")
                            Spacer(modifier = Modifier.weight(1f))
                            SearchField(value = "", onValueChange = {})
                        }
                    },
                )
            }
            """
        )

        result = scanner.check_titlebar_search_layout(self.sources(scanner))

        self.assertTrue(result["passed"])
        self.assertFalse(result["warnings"])

    def test_warns_when_titlebar_weighted_search_keeps_fixed_spacing(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Header() {
                TitleBar(
                    title = {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(24.dp),
                        ) {
                            Text("Store")
                            Spacer(modifier = Modifier.weight(1f))
                            SearchField(value = "", onValueChange = {})
                        }
                    },
                )
            }
            """
        )

        result = scanner.check_titlebar_search_layout(self.sources(scanner))

        self.assertTrue(result["passed"])
        self.assertIn("explicitly requires it", "\n".join(result["warnings"]))

    def test_rejects_button_wrapping_a_column(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun AppTile(onSelect: () -> Unit) {
                Button(
                    onClick = onSelect,
                    modifier = Modifier.height(150.dp),
                ) {
                    Column {
                        Text("App")
                        Text("Version 2.0")
                        Text("120 MB")
                    }
                }
            }
            """
        )

        result = scanner.check_button_container_semantics(self.sources(scanner))

        self.assertFalse(result["passed"])
        self.assertIn("wraps a Column", "\n".join(result["failures"]))

    def test_rejects_disabled_button_as_read_only_surface(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Detail() {
                Button(
                    onClick = {},
                    enabled = false,
                ) {
                    DetailContent()
                }
            }
            """
        )

        result = scanner.check_button_container_semantics(self.sources(scanner))

        self.assertFalse(result["passed"])
        self.assertIn("disabled with an empty onClick", "\n".join(result["failures"]))

    def test_accepts_concise_command_button(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Install(onInstall: () -> Unit) {
                Button(onClick = onInstall) {
                    Icon(painter = installIcon, contentDescription = null)
                    Text("Install")
                }
            }
            """
        )

        result = scanner.check_button_container_semantics(self.sources(scanner))

        self.assertFalse(result["warnings"])
        self.assertTrue(result["passed"])
        self.assertFalse(result["failures"])

    def test_legacy_rich_button_marker_cannot_suppress_failure(self) -> None:
        scanner = load_scanner_module()
        self.write_kt(
            """
            @Composable
            private fun Command(onRun: () -> Unit) {
                // spatial-ui: intentional-rich-button compact two-line command
                Button(onClick = onRun) {
                    Column {
                        Text("Run")
                        Text("Uses current settings")
                    }
                }
            }
            """
        )

        result = scanner.check_button_container_semantics(self.sources(scanner))

        self.assertFalse(result["passed"])
        self.assertIn("wraps a Column", "\n".join(result["failures"]))
        self.assertFalse(result["warnings"])
        summary = scanner.scan(self.target_dir, self.scratch_dir)
        self.assertFalse(summary["passed"])
        self.assertTrue(
            any(
                "[button_container_semantics]" in failure
                for failure in summary["failures_or_explicit_none"]
            )
        )

    # ---- window chrome ----------------------------------------------------

    def test_warns_on_hand_rolled_edge_chrome(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer {
                    Box(Modifier.fillMaxSize()) {
                        MainPage()
                        Box(Modifier.align(Alignment.CenterStart)) {
                            Column { IconButton(onClick = {}) { } }
                        }
                    }
                }
            }
            """
        )

        result = scanner.check_window_chrome_ornaments(self.sources(scanner))

        self.assertTrue(result["passed"])
        self.assertIn("window-level fittings", "\n".join(result["warnings"]))

    def test_intentional_overlay_marker_suppresses_chrome_warning(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer {
                    Box(Modifier.fillMaxSize()) {
                        MainPage()
                        // spatial-ui: intentional-in-page-overlay transient hint bubble
                        Box(Modifier.align(Alignment.CenterStart)) {
                            Column { IconButton(onClick = {}) { } }
                        }
                    }
                }
            }
            """
        )

        result = scanner.check_window_chrome_ornaments(self.sources(scanner))

        self.assertFalse(result["warnings"])

    def test_tabbar_usage_is_not_flagged_as_hand_rolled(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt(
            """
            fun mainApp(scope: SpatialAppScope) = with(scope) {
                DefaultWindowContainer {
                    TabBar(placement = TabBarPlacement.Start) { item(text = "Home") }
                    Box(Modifier.align(Alignment.CenterStart)) {
                        Column { IconButton(onClick = {}) { } }
                    }
                }
            }
            """
        )

        result = scanner.check_window_chrome_ornaments(self.sources(scanner))

        self.assertFalse(result["warnings"])

    # ---- root change guard ------------------------------------------------

    def _git(self, *args: str) -> None:
        subprocess.run(
            ["git", *args],
            cwd=self.target_dir,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def test_root_change_guard_flags_silent_window_to_stage_switch(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest(WINDOW_MANIFEST)
        self.write_kt("fun mainApp() { DefaultWindowContainer { Panel() } }")
        self._git("init")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "test")
        self._git("add", "-A")
        self._git("commit", "-m", "baseline")

        self.write_manifest(STAGE_MANIFEST)

        result = scanner.check_root_change_guard(self.target_dir, "existing_module")

        self.assertFalse(result["passed"])
        self.assertIn("root architecture changed", "\n".join(result["failures"]))

    def test_root_change_guard_skips_outside_git(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()

        result = scanner.check_root_change_guard(self.target_dir, "existing_module")

        self.assertTrue(result["passed"])
        self.assertTrue(result["warnings"])

    def test_root_change_guard_not_applicable_to_new_project(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()

        result = scanner.check_root_change_guard(self.target_dir, "new_project")

        self.assertTrue(result["passed"])
        self.assertFalse(result.get("failures"))

    # ---- entry + manifest -------------------------------------------------

    def test_missing_main_app_entry_fails(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt("fun somethingElse() { DefaultWindowContainer { } }")

        result = scanner.check_entry_wired(self.sources(scanner))

        self.assertFalse(result["passed"])

    def test_in_volume_requires_style_two(self) -> None:
        scanner = load_scanner_module()
        manifest = (
            "<manifest><application>"
            '<meta-data android:name="pico.spatial.windowcontainer.id" android:value="demo" />'
            "</application></manifest>"
        )

        result = scanner.check_manifest_consistency(
            "IN_VOLUME", [(Path("AndroidManifest.xml"), manifest)]
        )

        self.assertFalse(result["passed"])
        self.assertIn("style=2", "\n".join(result["failures"]))

    def test_scan_writes_result_artifact(self) -> None:
        scanner = load_scanner_module()
        self.write_manifest()
        self.write_kt("fun mainApp() { DefaultWindowContainer { Button(onClick={}){} } }")

        scanner.scan(self.target_dir)

        self.assertTrue((self.scratch_dir / "implementation_scan_result.json").is_file())


if __name__ == "__main__":
    unittest.main()
