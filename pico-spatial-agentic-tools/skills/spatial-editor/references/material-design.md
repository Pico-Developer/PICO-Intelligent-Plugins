# Proactive Scene Material Design

Plan material behavior before submitting SceneSpec. Revisit it after live entity
bindings are available. Use this rule for creative scene authoring; preserve the
explicitly limited appearance of a scaffold, blockout, flat-color or diagnostic task.

## Design Before Choosing an Implementation

1. List each distinct visible surface, its semantic role, prominence and scene style.
   Start from the user goal and reference images, including surfaces whose exact
   appearance was delegated to the agent.
2. Describe the observable behavior that makes each important surface recognizable.
   Distinguish user requirements, bounded agent design choices and optional polish.
   Do not infer new gameplay, simulation, audio or lighting requirements.
3. Select a material route for that behavior. Treat a basic-geometry restriction as
   a geometry constraint; a Cube or Plane can still use Shader Graph.
4. Preserve that description in SceneSpec materials and supported effects fields.
   Record agent-chosen defaults as design choices, with their reason and priority.
   Never reduce the description to RGB to fit the current authoring path.
5. Check execution readiness separately: discover actual tools, required graph
   features, validation, preview, binding and saving in the managed workflow.
   Honor its live schema and mutation boundary.

Keep the least complex route that realizes the selected appearance. A default PBR
material that already produces the needed behavior can be preserved. Shader Graph
is preferred when the selected behavior needs shader computation or controls that
the admitted default-material path cannot author. Unknown capability alone is not
a confirmed gap.

## Surfaces That Require an Explicit Route Decision

Evaluate these surfaces even when the user does not name a shader. These are
design prompts, not mandatory feature bundles or fixed physical simulations.

| Surface in a creative scene                                             | Bounded appearance to consider                                                                             | Route decision                                                                                                                                                     |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Water, moat, pond or fountain surface                                   | Gentle ripple variation and a view-dependent surface highlight suited to the style; depth tint when useful | Prefer Shader Graph if these behaviors are selected and the default path cannot realize them; do not demand transparency, caustics or scene reflections by default |
| Glass, crystal or ice                                                   | A readable translucent or reflective appearance when the design calls for it                               | Assess existing bindings and supported blend/refraction controls; a low alpha value is insufficient evidence                                                       |
| Luminous signs, magic or holograms                                      | Emission and any requested pulse or view-dependent treatment                                               | Assess Shader Graph; separate particle generation and actual light entities                                                                                        |
| Metal, wet stone or textured wood                                       | Surface response or pattern needed for material identity                                                   | Preserve a suitable existing material; assess Graph when the required controls or textures cannot be authored through the default path                             |
| Ordinary painted walls, solid blocks or deliberately flat illustrations | Opaque color and the existing surface response                                                             | Prefer default PBR; do not add Shader Graph without a visible reason                                                                                               |

For a fairytale castle with a moat, plan the water as a distinct material before
SceneSpec. A restrained stylized ripple/highlight treatment is a reasonable agent
design choice. Keep walls on default PBR when their selected appearance is solid
color. Fireworks remain particle work. Do not infer accurate reflections of
fireworks or illumination of the castle from water shading.

For an explicitly flat-color castle blockout, keep a static blue moat on default
PBR and record the user's simplification as the reason. Do not override it with
animated water.

## Preserve the Decision When Execution Is Unavailable

Record both the desired route and actual execution status. A verified RGBA-only
default path cannot establish ripples, controlled reflection, refraction or emission.

- For a confirmed gap, retain the Shader Graph requirement in the material report
  and mark execution unavailable when the current workflow cannot create/bind it.
- For a selected design choice whose capabilities are unresolved, retain it as a
  candidate and name the next focused check. Do not claim Graph readiness.
- For a required behavior, report the blocker through the live workflow. Never
  silently relabel the user requirement as optional.
- For an optional agent design choice, use the workflow's supported fallback and
  report the omitted behavior. Optional unavailability does not justify blocking
  unrelated work.
- Never bypass managed authoring or invent a shader tool to execute the choice.

Use the live reporting schema. When it cannot encode desired route and blocked
status together, retain the desired Shader Graph route in the reason/limitations
and use the valid blocked execution form. Do not invent new enum values.

## Completion Check

Before concluding that no Shader Graph is needed:

- Cover every distinct visible material and every effect-bearing surface above.
- Check the original scene goal as well as the agent-authored SceneSpec. A simplified
  SceneSpec is not independent proof that material design was complete.
- Give a positive reason for each default-PBR choice: an explicit simple style,
  a verified existing appearance, or a selected behavior that the route supports.
  "The user did not say shader" and "the workflow only supports RGBA" are insufficient.
- Retain unresolved candidates and unavailable selected Graph effects in the report.
  Report them as unimplemented; do not convert them into "no matches".
- For motion, transparency or emission claims, use rendered evidence appropriate
  to the claim and verify binding/persistence through supported operations.
