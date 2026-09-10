# Grab & Drag (object pick-up & drag)

## Tool

`pico_xr_grab` — actions: `enable` / `disable` / `status` / `make_grabbable`

Trigger words: pick up / grab / grasp / drag / grabbable / pickup / interactable.

> **Why one tool owns both halves.** XRI object grabbing only works when BOTH
> sides of the interaction pair are wired up, and either half alone is inert:
>
> - **Interactor side** — the hand/controller must carry an interactor that can
>   initiate a grab, and the scene must contain an `XRInteractionManager` that
>   brokers interactor↔interactable handshakes. **Grab does NOT create the
>   interactor itself** — the interactor lives on whichever input block the user
>   enabled (`pico_xr_controller` for controllers, `pico_xr_hand` for hands).
> - **Interactable side** — the target object must carry a Collider + Rigidbody +
>   `XRGrabInteractable` so it can be selected and follow the interactor.
>
> Enabling just one side "works" (no error) but produces nothing grabbable, so
> this block owns the parts NOT owned by an input block: `enable` guarantees the
> shared `XRInteractionManager` exists, and `make_grabbable` upgrades a target
> object into a grabbable.

> **Grab is DECOUPLED from hand vs controller.** Grab does not decide — and must
> not change — which input source (hand or controller) is visible. "Controller grab"
> (grab with a controller) means the user enables `pico_xr_controller` and then
> grab; "Hand grab" (grab with a hand) means the user enables `pico_xr_hand` and
> then grab. Grab itself is source-agnostic: `enable` no longer re-shows the
> controller module or adds interactors to controller nodes. The guarantee that
> **a visible controller uses the PICO prefab (not the generic Starter Assets
> model)** is owned SOLELY by `pico_xr_controller enable`, which mounts
> `LeftControllerModel.prefab` / `RightControllerModel.prefab` and hides the
> Starter Assets visual.

## Dependency

- XR Origin present
- Package `com.unity.xr.interaction.toolkit` + Sample `Starter Assets` (same as
  every XRI block — the `XRInteractionManager` and the `XRGrabInteractable` type
  both come from XRI).
- An enabled input block that supplies the interactor: `pico_xr_controller`
  (controller path) or `pico_xr_hand` (hand path). Grab itself adds NO
  interactor — it only guarantees the shared `XRInteractionManager` and upgrades
  target objects. Without an interactor there is nothing to initiate the grab at
  runtime.
- No extra package install beyond XRI, and no domain reload — this block only
  adds/removes an interaction-manager host + interactable components; it does NOT
  copy any `.cs` driver.

## Cheatsheet

### Enable Grab (interaction broker)

- Pre: XR Origin (via orchestration step B.1 — XRI package + Starter Assets).
- Call: `pico_xr_grab(action=enable)`.
- Guarantees an `XRInteractionManager` exists in the scene (creates an
  agent-owned host `[PICO_MCP] XR Interaction Manager` ONLY when the scene has
  none — R2: never touches a foreign manager) and drops the idempotency marker
  `[PICO_MCP] Grab Marker` under the XR Origin.
- **DECOUPLED**: `enable` no longer re-shows the controller module and no longer
  adds interactors to controller nodes. Whether a hand or controller is visible
  (and that a controller uses the PICO prefab) is owned by `pico_xr_controller`
  / `pico_xr_hand`. Enable grab AND the matching input block for a working setup.
- Enabling the broker alone makes nothing grabbable yet — follow with
  `make_grabbable` on the object(s) the user wants to pick up.

### Make an object grabbable (interactable side)

- Pre: XRI available (Starter Assets imported). `enable` should already have run
  so an interactor + manager exist, otherwise the object is grabbable but there
  is nothing to grab it.
- Call: `pico_xr_grab(action=make_grabbable, target="<object name or path>")`.
  - `target` accepts a plain object name or a full hierarchy path
    (`Parent/Child`). It resolves against the ACTIVE scene (including inactive
    objects).
  - Leave `target` EMPTY to spawn an agent-owned sample cube
    (`[PICO_MCP] Grabbable Sample`) ~1.5 m in front of the Main Camera for quick
    validation.
- Adds a `BoxCollider` if the target has no Collider, a **kinematic**
  `Rigidbody` (`useGravity = false`, `isKinematic = true`) if it has none, and an
  `XRGrabInteractable`. The kinematic-Rigidbody promise is deliberate: a plain
  `useGravity = true` body makes the object **fall to the floor** the instant
  `make_grabbable` runs, before the user ever grabs it. Freezing gravity +
  kinematic keeps the object parked in place; `XRGrabInteractable` drives its
  motion while held and (per its `forceGravityOnDetach` default) leaves it where
  released. Idempotent: a target that already has a Rigidbody is left as-is —
  existing physics settings are NOT overwritten (so a user object that is
  _meant_ to fall keeps falling).
- If the C# layer returns `error` about the target not being found or
  `XRGrabInteractable` being unavailable, relay it — either the object name is
  wrong or XRI/Starter Assets is not imported.

### Disable Grab

- No deps to check.
- Call: `pico_xr_grab(action=disable)`.
- Removes the agent-owned objects only (R2): the `[PICO_MCP] Grab Marker`, the
  `[PICO_MCP] XR Interaction Manager` host (if WE created it), and the
  `[PICO_MCP] Grabbable Sample`. **User-authored grabbables are left intact** —
  the block does NOT strip `XRGrabInteractable` from objects the user targeted,
  because it does not track which ones were upgraded. To un-grab a specific
  user object, remove its `XRGrabInteractable` manually.

### Status

- Call: `pico_xr_grab(action=status)`.
- `installed` is true when the `[PICO_MCP] Grab Marker` is present (the
  interaction broker is ready). If the marker exists but no `XRInteractionManager`
  is in the scene, `reason` warns that interactions will be inert until one exists.
- A `true` here does NOT imply an interactor exists. Whether grab actually works
  at runtime also requires an enabled input block (`pico_xr_controller` /
  `pico_xr_hand`) to supply the interactor.

## Typical pipeline — controller grab + a specific object

```
pico_xr_status()                                   → xr_origin=ok, grab=off
pico_xr_controller(action=enable)                  → ok   (PICO controller prefab + interactor)
pico_xr_grab(action=enable)                        → ok   (interaction broker ready)
pico_xr_grab(action=make_grabbable, target="Cube") → ok   (Cube is now grabbable)
pico_xr_status()                                   → grab=on   (internal verify)
Save Scene                                         → ok
```

### Typical pipeline — hand grab

```
pico_xr_hand(action=enable)                → ok   (PICO hands + OpenXR HandInteractionProfile)
pico_xr_grab(action=enable)                → ok   (interaction broker ready)
pico_xr_grab(action=make_grabbable)        → ok   (spawns [PICO_MCP] Grabbable Sample)
pico_xr_status()                           → grab=on
Save Scene                                 → ok
```

### Typical pipeline — disable

```
pico_xr_grab(action=disable)   → ok
pico_xr_status()               → grab=off (internal verify)
Save Scene                     → ok
```

## Notes

- **Decoupled from hand/controller**: grab does not touch input-source
  visibility. Pair it with `pico_xr_controller` (controller path) or
  `pico_xr_hand` (hand path); the input block owns the interactor and — for
  controllers — the PICO-prefab model.
- This block reuses the SAME XRI package + Starter Assets dependency as XR
  Origin.
- Idempotent (R1): re-running `enable` when the marker exists is a no-op;
  `make_grabbable` on an already-grabbable object leaves it unchanged.
- Non-destructive (R2): only agent-owned `[PICO_MCP] ...` objects are created or
  removed. A pre-existing `XRInteractionManager` is reused, never modified, and
  user grabbables survive `disable`.
- Every XRI type is reflection-resolved (R3): the `Interactors.` /
  `Interactables.` sub-namespaces are XRI 3.x; 2.x legacy namespaces are tried
  as a fallback, so the block is not pinned to one XRI major version.
- No domain reload: unlike Plane / Spatial Mesh, this block imports no `.cs`
  driver, so no settle loop is needed after `enable` / `make_grabbable`.
- `make_grabbable` needs a real interactor + manager to actually pick things up
  at runtime; enable an input block (`pico_xr_controller` / `pico_xr_hand`) so an
  interactor exists.
- **Grabbables do NOT fall** (defect fix): the Rigidbody `make_grabbable` adds is
  kinematic with gravity off (`useGravity = false`, `isKinematic = true`), so the
  object stays put until grabbed instead of dropping to the floor. This mirrors
  the PICO SDK's own Grab Interactable block, which likewise disables gravity on
  the body it creates. Objects that already carry a Rigidbody are untouched (R1),
  so intentionally-falling user objects keep their behaviour.
