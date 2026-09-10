# Primitive Scene Resources

Read this reference when a code-owned scene creates repeated primitives,
materials, or other runtime resources.

## Why Scene-Owned Reuse Matters

Mesh and material construction can perform native allocation, upload, or shader
work. Repeating that work for every Entity increases startup latency and memory
pressure, and rebuilding resources from `SpatialView.update` or Compose
recomposition can turn ordinary lifecycle events into duplicate allocation.

Treat an Entity as a placed instance and a mesh or material as a reusable
resource definition. Two Entities that share geometry and appearance can still
have independent transforms, hierarchy, and behavior.

## Use a Scene-Lifetime Resource Owner

Keep one resource registry or factory for the same lifetime as the scene root:

```text
SceneState
├── placementOwner
├── fittedSceneRoot
├── entitiesById
└── resources
    ├── meshesByGeometrySpec
    └── materialsByDefinition
```

- Key meshes by the complete geometry specification that affects their vertex
  data, such as primitive type, dimensions, or subdivisions. A unit primitive
  plus uniform Entity scale is also valid when it preserves the intended shape.
- Key materials by immutable visual parameters that affect the material
  resource. Do not create a nominally new material for every repeated Entity.
- Create or load each distinct resource during intentional scene construction,
  then create Entities that reference it.
- Retain the registry while any Entity may use its resources. When the scene is
  destroyed, clear retained Entity and resource references according to the
  host project's accepted lifecycle pattern.

The exact mesh, material, and cleanup APIs are SDK-version-sensitive. Follow the
host project's verified resource APIs or consult `spatial-sdk-guideline`; do not
invent a disposal call that the installed SDK does not expose.

## Keep Construction Out of Update Loops

Use `SpatialView.initial`, an owning controller, or another accepted one-shot
scene-construction path to allocate the hierarchy and resources. Use
`SpatialView.update` for deliberate size/revision-dependent transforms, not as
an unconditional scene factory. Make recomposition idempotent by retaining the
scene state and a construction or revision key.

For a large programmatic scene, avoid one unbounded burst of main-thread
resource construction. Use the asynchronous or staged loading pattern already
accepted by the project, attach only complete usable batches, and expose an
explicit ready state before measuring bounds. Do not impose a universal object
count threshold: actual cost depends on geometry, material, device, and SDK.

## Acceptance Checks

Before completion, verify that:

- repeated geometry specifications reuse the same mesh resource;
- repeated material definitions reuse the same material resource;
- unrelated recomposition or `SpatialView.update` does not create more
  Entities or resources;
- leaving and returning to the screen follows one deliberate destroy-or-retain
  policy and does not duplicate the scene;
- the final cold launch has no app ANR, fatal exception, or resource-load
  failure.
