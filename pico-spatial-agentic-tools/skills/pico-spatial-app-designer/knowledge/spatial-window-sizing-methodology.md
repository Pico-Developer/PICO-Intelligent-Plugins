# PICO Spatial Window Sizing Decision Methodology

## When to Use This Document

Invoke when any one holds:

- Deciding "how big should the window of a PICO / spatial app be", "how to set window size", or "window-size strategy for different scenes";
- Doing design / building the skeleton and needing to give a window a **default size + resizable range**;
- Judging during review whether a window is **too large and occludes the view / too small to be usable / beyond the clear field of view**.

Not applicable: pure component size-tier lookup (use the spec-library quick-reference table); planar UI unrelated to PICO.

---

## 0. Core in One Sentence

In PICO, "how big" a window is not set as a dp constant, but rather **first decide "how much field of view it should occupy + how far away + what content type it is", then land it onto PICO's dp specs and tiers**. The system uses dynamic scale to keep things clear whether pulled far or near, so what really needs to be controlled is **field-of-view occupancy**, not the absolute physical size.

---

## 1. First Switch Your Unit Mindset: "Size" in PICO Comes in Three Sets

Before deciding, you must first be clear about which set of units to use—this is the biggest difference between PICO and phone / desktop:

| Content Type | Unit | Behavior |
|---|---|---|
| Planar panel (Planar window / UI) | **dp** (auto-converted by the system to dmm) | dynamic scale on distance change, field-of-view occupancy stays constant, always clear, readable, and interactive |
| 3D subject (Volumetric window / model) | **meters** | fixed physical size, shrinks when pulled far, like a real object |
| Angular unit | **dmm** (distance-independent millimeters) | underlying expression, use dp when designing |

Conclusion: when designing a Planar window, what you set is "how much it occupies in the field of view" (dp); when designing 3D content, what you set is "how big it is in the real world" (meters). Spatial panels use dmm, design uses dp, and the system auto-converts dp→dmm; when a window is pulled near or pushed far, a spatial panel keeps a relatively constant FOV via dynamic scale, while a Volumetric window and 3D model do not change size.

---

## 2. Four-Step Decision Framework

### Step 1 · Choose window type and size baseline by content type

First judge whether the content subject is a "planar interface" or a "3D object", which decides the window type:

| Content Subject | Window Type | Size Baseline |
|---|---|---|
| Familiar 2D interface / task (document, list, board, settings) | **Planar window** | default 1280 × 720 dp, range 320×180 ~ 2700×1800 dp |
| Content subject is 3D (model, scene, breathing sphere) | **Volumetric window** | custom size, can be fixed or follow content, scales proportionally when resized |

A Planar window launches by default 1.75 m in front of the wearer; when the distance is adjusted, it dynamically scales by default. If 3D content is added inside a planar window, all content must fall within the 640 dp depth range; anything beyond is clipped, and multiple 3D contents should keep their depth as consistent as possible.

### Step 2 · Use the "clear field-of-view zone" to constrain the size upper limit

This is the hard constraint that decides "how big it can be": core content must fall within the clear field-of-view zone and must not be so big that you frequently turn your head.

- **Core content**: within the horizontal 65° / vertical 40° clear field-of-view zone;
- **Secondary content**: peripheral field of view, recommended ≤ horizontal 85° / vertical 55°;
- Place the window initially farther away to reduce eye strain, and use a horizontal layout to suit the wide field of view.

**Derivation logic**: window width → convert to horizontal field-of-view angle at a 1.75 m distance → the main UI must fall into the 65° sweet spot. The part beyond 65° can only hold secondary / optional information. Big enough to require turning your head to browse the main content is a size-design failure.

### Step 3 · Use "depth + hit target" to back out the minimum usable size

The lower limit of the size is decided by readability and interactability:

- **Interaction hit target ≥ 56 × 56 dp**: directly constrains the window's minimum usable width; if controls are too dense, the window must be widened;
- **Minimum font size 12 dp**: smaller is only for non-core, non-interactive content; for CJK and ≤17sp body text, use Medium; when the window widens, a single line should not exceed about 50 Chinese characters, and if it is too wide, either split into columns or limit the body column width;
- **Depth is priority**: closer to the user = more important; do not stack more interactive content behind interactive 3D content;
- **Framework component minimum sizes make up the window base**: TitleBar height 96 dp, TabBar main area 64 dp, Toolbar minimum 64 dp, AlertDialog minimum height 184 dp, ListItem minimum height 60 dp. Stack these framework heights together and that is the fixed overhead outside the window content area; the content area must leave enough room above and beyond that.

### Step 4 · Set "default value + resizable range", don't nail it down

PICO windows inherently allow users to freely move / resize; the design responsibility is to give a **reasonable default value that falls within the 320×180 ~ 2700×1800 dp range**, rather than a single size. With multiple windows, a new window appears by default in front of the user, keeping a 56 dp gap from the source window, with orientation following the visual habit of left to right and top to bottom.

---

## 3. Window Size Tier Suggestions by Scene Domain

Group common scenes into four tiers and give a PICO landing starting point (all are default values, users can resize further):

| Scene Tier | Typical Domains | Window Type and Size Strategy | Field of View / Distance |
|---|---|---|---|
| **Auxiliary / HUD** | notifications, control panels, Augment attachments | small Planar or Augment, occupying only a corner of the center, approaching the 320×180 dp lower limit | near, placed at the edge of the central field of view |
| **Productivity / main content** | documents, tables, lists, boards | Planar, starting from the 1280×720 dp default, can be placed side by side in multiple windows (gap 56dp) | mid, 1.75 m, main content locked to the 65° sweet spot |
| **Media / immersion** | video, panorama, theater mode | large Planar or wraparound, actively enlarged to occupy the field of view for enhanced immersion, can approach 2700×1800 dp | far, actively wrap but guard against edge motion sickness |
| **Spatial-anchored / 3D** | 3D models, breathing sphere, product preview | Volumetric, at real size (meters), content within 640dp depth, most valuable face toward the user | depends on content, depth close to the planar window to avoid frequent refocusing |

---

## 4. Comfort and Safety Constraints Related to Size

Changes in window size directly trigger PICO-specific comfort risks, which must be considered together when setting the size:

- **Vestibular-visual consistency**: moving a large-area / large-volume window easily causes motion sickness; use a semi-transparent transition, dynamic blur, or a reduced FOV to mitigate, and avoid fast displacement of large windows;
- **Motion graded by size**: small-size feedback elements <300ms fast-paced; large-size framework / scene 300–800ms soothing curves; motion at the edge of the field of view uses only slight amplitude;
- **Don't let the window get too large and occlude the view**: an oversized initial size occludes the environment and creates a sense of pressure; in a dark environment, a large window should even more avoid large-area high-saturation color blocks;
- **Corner radius fixed at 32 dp**: kept no matter how large the window is, to reduce visual distraction.

---

## 5. Decision Checklist

When setting any window's size, answer in order:

1. **Is the content subject 2D or 3D?** → choose Planar (dp) or Volumetric (meters);
2. **Which scene tier does it belong to?** (auxiliary / productivity / media / 3D) → set the size baseline and default distance;
3. **Can the main content fall into the horizontal 65° / vertical 40° clear field-of-view zone?** If not, it's too big;
4. **Has the framework component overhead been accounted for?** (TitleBar 96 + Toolbar / TabBar 64...) → the content area leaves enough room above and beyond;
5. **Are hit target ≥56dp, body text ≥12dp, and single line ≤50 Chinese characters all met?** → back out the minimum width;
6. **Is the depth hierarchy correct?** The most important is the nearest and most central; 3D content within 640dp depth;
7. **Does the default value fall within 320×180 ~ 2700×1800 dp and allow the user to resize?**
8. **Will moving / motion of a large window cause sickness?** Field-tested from the wearing viewpoint + normal posture.

---

## 6. Key-Number Quick Reference

| Item | Value |
|---|---|
| Planar window default size | 1280 × 720 dp |
| Planar window size range | 320×180 ~ 2700×1800 dp |
| Planar default launch distance | 1.75 m in front |
| 3D content depth range inside a planar window | ≤ 640 dp |
| Multi-window default gap | 56 dp |
| Window corner radius | fixed 32 dp |
| Clear field-of-view zone (core content) | horizontal 65° / vertical 40° |
| Peripheral field of view (secondary content) | ≤ horizontal 85° / vertical 55° |
| Interaction hit target | ≥ 56 × 56 dp |
| Minimum font size | 12 dp |
| Max characters per line | about 50 Chinese characters |
| TitleBar height | 96 dp |
| TabBar main area height | 64 dp |
| Toolbar minimum height | 64 dp |
