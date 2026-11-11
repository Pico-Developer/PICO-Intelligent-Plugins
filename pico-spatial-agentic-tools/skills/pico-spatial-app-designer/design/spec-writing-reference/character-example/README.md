# Character scene: Preview to Spec

Open [Preview](preview.html) and compare [Spec](design-spec.json). Plan authors should first read [3D Preview authoring](../../design-reference/3d-preview.md).

The SVG is a simplified placeholder for a future 3D character. Blue jacket and stylized appearance are confirmed; face details are not. Rotate changes the placeholder orientation, Reset restores it, and Greet displays an example-only status message. Actual waving is intentionally not simulated. Header/footer text explains the example and is not product UI.

The glass AttachmentPanel stays fixed when the character rotates. Both scene-design-notes entries are preserved verbatim in the matching Spec nodes' designNotes. The shared `sui-volume` shell declares a 900 × 600 × 400 dp Volume. Its actual Web bounds are 900 × 600 CSS pixels. The faint background, inset wireframe and size caption are Preview aids, not native surfaces. The depth is a declared design dimension; the projection is schematic. Exact model/panel scene offsets remain unspecified. Native SDK unit conversion is resolved during implementation.

The pending character is not listed in assets with a fake file. The SVG's individual paths are rendering mechanics, not prescribed native mesh parts. This is a design-reference example, not evidence of a delivered model or a working native animation.

Run `python3 scripts/check_design_spec.py spec-writing-reference/character-example/design-spec.json` from the skill directory. Browser audit should find no mismatches but still report unverified native behavior and geometry.
