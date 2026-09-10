# PICO Spatial Surface Sizing

The single biggest way a spatial surface fails is size — whether it's a room-scale wall, a compact utility panel, a HUD/Augment widget, or a volumetric model. Too large and the user turns their head to read core content or the surface occludes the room; too small and it's unreadable or unhittable. On PICO you don't set a size as a dp constant — you decide **how much field of view it should occupy, at what distance, for what content**, then land that onto PICO's dp specs. The system dynamically scales a Planar window with distance so field-of-view occupancy stays roughly constant; occupancy is what you actually control. (Volumetric surfaces size in meters at real-world scale; Stage 2D controls are placed via `AttachmentPanel`.)

## The chain — run it for every window

**content type → scene tier → baseline → clear field of view → readable/clickable floor → default / min / max**

### 1 · Content type decides the unit and window type

| Content subject | Window type | Unit | Size basis |
|---|---|---|---|
| 2D interface/task (board, list, table, media surface, dashboard) | **Planar** | **dp** (system converts to dmm) | **default 1280×720 dp (landscape large-screen baseline)**, legal range 320×180 ~ 2700×1800 dp |
| 3D subject (model, scene, product) | **Volumetric** | **meters** | real-world size; scales proportionally when resized |

> **Critical: large-screen baseline, not phone size.** PICO spatial windows are viewed at ~1.75m distance on a head-mounted display — this is a **large-screen** context, not a phone. Never use phone-portrait dimensions (e.g. 360×640, 480×800) as defaults. The 1280×720 dp baseline matches a comfortable ~65° horizontal FOV at mid-distance; content density should be sized for reading across the room, not held in hand. Portrait orientation is acceptable only for deliberately narrow/tall content like a scroll or document reader, and must be justified in the sizing chain.

Most windowed apps are **Planar**. Even Planar windows support Z-axis depth layering: selected items can rise forward (8–24 dp), hover feedback pops 2–6 dp, and content can have thickness. All 3D content inside a Planar window must stay within the **640 dp total depth** range or it clips. See `spatial-design-rules.md` → "Z-axis / depth layering" for depth vocabulary and rules.

### 2 · Scene tier sets the baseline and distance

| Scene tier | Typical use | Size strategy | FOV / distance |
|---|---|---|---|
| Productivity / main content | boards, tables, control panels, ops consoles | Planar from 1280×720 dp default; multiple windows side by side, 56 dp gap | mid, ~1.75 m, core content locked to the 65° sweet spot |
| Media / immersion | video wall, panorama, theater, big data-viz canvas | large Planar or wraparound, actively enlarged toward 2700×1800 dp for immersion | far; wrap deliberately but guard the edges against motion sickness |
| Spatial-anchored / 3D | 3D models, product preview embedded in the wall | Volumetric at real size, depth ≤ 640 dp | depends on content; keep depth near the planar plane to avoid refocusing |

A Planar window launches ~1.75 m in front of the wearer and scales dynamically as distance changes.

### 3 · Clear field of view caps the upper size

Core content must fall inside the **horizontal 65° / vertical 40°** clear-FOV zone. Secondary/optional content may sit in the periphery, ideally **≤ horizontal 85° / vertical 55°**. If the user has to turn their head to browse the *main* content, the window is too big — that's a sizing failure, not a preference. Prefer horizontal layouts to suit the wide FOV, and place the window a bit farther to reduce eye strain.

### 4 · Readable/clickable floor backs out the minimum

- **Hit target ≥ 56×56 dp** — directly constrains minimum usable width; widen the window if controls get dense.
- **Body text ≥ 12 dp** (smaller only for non-core, non-interactive text); for CJK / ≤17sp body use Medium weight. When wide, keep a single line ≤ ~50 Chinese characters — split into columns past that.
- **Framework overhead stacks on top of content**: TitleBar 96 dp, TabBar main area 64 dp, Toolbar min 64 dp, AlertDialog min height 184 dp, ListItem min height 60 dp. Subtract these before sizing the content area.
- **Depth = priority**: nearest/most-central = most important; don't stack interactive content behind interactive 3D content.

### 5 · Set default + range, not a fixed number

PICO windows are user-movable and resizable by design. Your job is a sensible **default inside 320×180 ~ 2700×1800 dp** plus a min/max, not a single locked size. New windows appear in front of the user with a 56 dp gap from the source, ordered left-to-right, top-to-bottom.

## Padding tokens — spacing inside containers

Window size sets the outer frame; padding sets the breathing room inside it. On a surface read from across a room, too-tight padding makes dense content unreadable and too-loose padding wastes the clear-FOV budget — so pick the token by the container's role, don't hand-tune per element.

| Token | Value (dp) | Use for |
|---|---:|---|
| `Padding Small` | 8 | Inner padding of small controls — icon buttons, compact list items, chip/badge content. |
| `Padding Regular` | 16 | Default container padding — standard cards, list items, form blocks. |
| `Padding Medium` | 24 | Emphasis containers — dialog content areas, feature/info cards, sheet / coach-mark main content. |
| `Padding Large` | 32 | Window-container-to-content spacing — immersive panels, page-level modules, or wherever a looser reading rhythm is wanted. |

`Padding Large` (32 dp) intentionally matches the fixed 32 dp window corner radius, so content clears the rounded corner and the window edge reads as one consistent frame. When a window widens into its Large tier, step padding up toward Medium/Large; when it reflows to Compact/Constrained, step down toward Regular/Small before you start dropping content.

## Comfort constraints tied to size

- **Vestibular-visual consistency**: moving a large window easily triggers motion sickness — use semi-transparent transitions, dynamic blur, or a reduced FOV; avoid fast displacement of large windows.
- **Motion graded by size**: small feedback <300 ms snappy; large frame/scene 300–800 ms soothing; peripheral motion only slight amplitude.
- **Don't occlude the room by default**: an oversized initial window creates pressure; in dark environments avoid large high-saturation color blocks.
- **Corner radius fixed at 32 dp** regardless of window size.

## Key numbers

| Item | Value |
|---|---|
| Planar default size | 1280×720 dp |
| Planar legal range | 320×180 ~ 2700×1800 dp |
| Planar launch distance | ~1.75 m in front |
| 3D depth inside a Planar window | ≤ 640 dp |
| Multi-window gap | 56 dp |
| Corner radius | 32 dp (fixed) |
| Padding Small / Regular / Medium / Large | 8 / 16 / 24 / 32 dp |
| Clear-FOV (core content) | horizontal 65° / vertical 40° |
| Peripheral (secondary) | ≤ horizontal 85° / vertical 55° |
| Hit target | ≥ 56×56 dp |
| Min body text | 12 dp |
| Max chars per line | ~50 Chinese chars |
| TitleBar / TabBar / Toolbar min height | 96 / 64 / 64 dp |

## Sizing checklist (answer in order)

1. Is the subject 2D or 3D? → Planar (dp) or Volumetric (meters).
2. Which scene tier? → baseline + default distance.
3. Does core content fall inside 65°×40°? If not, it's too big.
4. Framework overhead subtracted from the content area?
5. Hit target ≥56 dp, body ≥12 dp, line ≤~50 CJK chars met? → minimum width.
6. Depth hierarchy right — nearest is most important, 3D within 640 dp?
7. Default inside 320×180 ~ 2700×1800 dp, with a resize range?
8. Will moving/animating a large window cause sickness?
