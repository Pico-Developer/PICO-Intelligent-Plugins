## Constraints / pitfalls

- DO NOT port a single-Activity navigation model directly into multiple Spatial containers
- DO NOT assume mobile-style system Back behavior exists on the Spatial runtime
- DO NOT keep major UI ownership tightly coupled to Activity lifecycle code if the UI is being split across containers
- DO NOT hardcode the SDK version in multiple dependency locations; keep the verified artifact version in one variable
- DO NOT infer a Spatial SDK/BOM artifact version from the PICO OS generation
- DO NOT choose or change a Spatial BOM version without project, template, Maven, or PICO development knowledge evidence
- DO NOT add Compose exclusions unless dependency conflicts actually require them
- DO NOT call Spatial-only APIs on standard Android devices
- DO NOT treat the migration as only a rendering task; interaction and navigation changes are part of the port
- DO NOT add MR, tracking, or ML features before the basic launcher and navigation flow are stable
