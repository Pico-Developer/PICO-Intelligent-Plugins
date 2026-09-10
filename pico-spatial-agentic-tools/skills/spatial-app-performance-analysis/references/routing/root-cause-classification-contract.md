# Root Cause Classification Contract

This contract defines a standardized, closed two-level taxonomy for the **final root-cause classification** of every analysis produced by this Skill. 

It is intentionally orthogonal to `issue_type_key` (defined in [Output Contract](output-contract.md)):

- `issue_type_key` records **which protocol/topic produced the evidence**(`spatial-engine` / `binder` / `memory` / `cpu_sched` / ...).
- `root_cause_classification` (this contract) records **what resource is the bottleneck and by which mechanism**, in a closed enum.

Both are emitted; neither replaces the other.

## 1. Position In The Pipeline (A Standalone Artifact, Produced Last)

This classification is a **downstream distillation** of the per-topic analysis, and it is written to its **own dedicated YAML file**. It is NOT a field of any topic output, NOT part of `final-summary.md`, and NOT part of the report template. It is produced as a separate, final step:

1. First, each executed topic emits its own output per the [Output Contract](output-contract.md) (YAML header + 6 body sections). That contract stays unchanged and does NOT carry any classification field.
2. Then `final-summary.md` aggregates the topics per the [Final Summary Contract](final-summary-contract.md). That file also does NOT carry the classification.
3. Finally, distill the topic outputs into this closed taxonomy and write it to a standalone file:

   ```text
   session-output-<timestamp>/root-cause-classification.yaml
   ```

   This is the canonical, isolated artifact used for baseline and evaluation. Keeping it in its own file (not mixed into other products) means baseline/eval tooling can consume it directly without parsing unrelated content.

Do not add `root_cause_classification` to a per-topic header or to `final-summary.md`. Keep the per-topic `evidence[*].id`s stable so this file's `evidence_refs` can point back into the underlying topic evidence.

## 2. Output Is a List, Not A-or-B

A single trace often breaks the frame budget for more than one reason (e.g. a GPU geometry spike overlapping a CPU-side GC burst). Therefore the output is a **list of independent classification entries**. Emit one entry per distinct, evidence-backed bottleneck; do not force a single winner.

- Each entry stands on its own evidence and its own `conclusion_level`.
- If several entries share a mechanism, keep them separate only when the evidence is separable; otherwise merge into one entry.
- When evidence is insufficient to classify anything, emit exactly one `undetermined` entry (see §6).

## 3. Level 1 — `resource_type` (closed enum)

| `resource_type` | 中文 | Meaning |
|---|---|---|
| `cpu` | CPU | CPU-side work/scheduling breaks the frame budget |
| `gpu` | GPU | GPU-side rendering work breaks the frame budget |
| `memory` | 内存 | Memory pressure (reclaim / exhaustion / kill) is the bottleneck |
| `undetermined` | 未定 | Evidence insufficient to classify (see §6) |

## 4. Level 2 — `bottleneck_category` (closed enum, scoped by Level 1)

`bottleneck_category` is only valid when paired with its parent `resource_type`. Each category is **evidence-driven**: it may only be emitted when its evidence signature is observed in / overlapping the user-visible abnormal window and on the critical path. Do not escalate a keyword, a raised metric, a topic name, or a downstream symptom alone into a classification.

## Classification Method

Do not map topic names or keywords directly to categories. For each candidate, fill in this chain:

```text
abnormal window → critical path → budget owner → mechanism → evidence refs → category
```

1. **Anchor:** use the user-visible frame/jank window and identify the frame-driving thread or render stage.
2. **Locate the lost budget:** decide whether the interval is spent running on the app CPU, waiting on the app path, executing on the service/GPU side, or under memory pressure.
3. **Prove the mechanism:** require both the candidate signal and its binding-side evidence in the same window. A Binder client wait is not service contention without server lock/queue/runnable-starvation or server work that exceeds its own budget. High geometry counters are not a GPU bottleneck without GPU execution time/stage evidence.
4. **Choose and deduplicate:** select the most specific category supported by the chain. Add a second category only when it represents a separate mechanism with separate evidence; otherwise keep the conservative category and record the unresolved dependency in `note`.

If the chain cannot be completed, do not guess. Use the conservative app-side category when the loss is visibly on the app frame path, or emit `undetermined` when even the owner is not established.

### 4.1 `resource_type: cpu`

| `bottleneck_category` | 中文 | Evidence signature (metric) | Evidence signature (slice / track / table) | Owning topic |
|---|---|---|---|---|
| `cpu_app_main_thread_busy_or_blocked` | APP 主线程繁忙或阻塞 | — | App `main` / frame-driving thread: `Choreographer#doFrame` / `ViewRootImpl` / `deliverInputEvent` / Compose·View traversal over single-frame budget, or a wait whose remote cause is not proven | `analysis-kotlin-spatial-app-jank.md` |
| `cpu_app_service_call_amplification` | APP 服务调用放大 | call count / per-frame call frequency ↑ | App frame-driving thread repeatedly creates, starts, configures, or synchronously updates service-backed resources; the trace shows the call pattern but does not prove server contention | `analysis-binder.md` / topic-specific subprotocol |
| `cpu_ec_submit_busy` | EC 提交繁忙 | `transformComponentCount` / `modelComponentCount` ↑ | `System_Update`, `System_Update: {name}`, `3d_ec`, `Choreographer#beginSpatialFrame` / `endSpatialFrame` **duration grows on the app critical path and independently exceeds the frame budget** in the abnormal window (APP Produce) | `analysis-spatial-engine.md` |
| `cpu_drawcall_overload` | DrawCall 绘制任务过多 | `Draw Call Count` / `3D Mesh Draw Call Count` / `Particle Draw Call Count` / `Shadow Draw Call Count` ↑ | `Eng-Render` **CPU submit** segment grows (submit/batch cost); CPU time high while `gpu_frame_end` is NOT the binding side | `analysis-spatial-engine.md` |
| `cpu_physics_overload` | 物理模拟过重 | `collisionComponentCount` / `rigidBodyComponentCount` ↑ | App-side physics `*System` / physics step slices grow | `analysis-spatial-engine.md` |
| `cpu_gc_storm` | GC 风暴导致 CPU 资源被占用 | Memory-class metrics move; high GC frequency | `SuspendAll` / `concurrent copying` / STW overlap the abnormal window AND GC/Heap threads consume CPU on the critical path | `analysis-memory.md` |
| `cpu_animation_overload` | 动画过重 | `animationResourceCount` / `Skeletal Animation Count` ↑ | Animation `*System` slices grow | `analysis-spatial-engine.md` |
| `cpu_system_service_contention` | 其他系统服务争用导致响应变慢 | — | Critical-path Binder wait **plus** server-side lock/queue contention, server runnable starvation (runnable > 3ms without running), or service work that itself exceeds the relevant service budget; a callee name or Binder duration alone is insufficient | `analysis-binder.md` / `analysis-cpu-scheduling.md` |

> **DrawCall attribution rule (decided):** "DrawCall 绘制任务过多" is classified under **CPU** as `cpu_drawcall_overload` because it measures the CPU submit / batching cost. If the raised `Draw Call Count` instead binds on the GPU side (`gpu_frame_end` grows, CPU submit is fine), classify it as `gpu_geometry_complexity`.

### 4.2 `resource_type: gpu`

| `bottleneck_category` | 中文 | Evidence signature (metric) | Evidence signature (slice / track / table) | Owning topic |
|---|---|---|---|---|
| `gpu_app_self_rendering_overload` | 应用自渲染过重 | `GPU Utilization` (App) / `CPU Utilization` (App 2D) / `viewAttachmentCount` ↑ | App `RenderThread` grows; Overdrawing, video playback, Compose recomposition storm, frequent invalidations | `analysis-kotlin-spatial-app-jank.md` + `analysis-spatial-engine.md` |
| `gpu_geometry_complexity` | 几何复杂度过高 | `Triangle Count` / `Vertex Count` / `3D Mesh *` / `Particle *` ↑ + GPU time ↑ | `gpu_frame_end` or equivalent GPU execution stage is high in the same abnormal frames; judged via Spatial Runtime process (`3D Mesh`, `Particle`) | `analysis-spatial-engine.md` |
| `gpu_scene_complexity` | 场景复杂度过高 | `Visible Lights` / `Visible Spot Lights` / `Shadow Draw Call/Triangle/Vertex Count` ↑ + GPU time ↑ | `gpu_frame_end` or equivalent GPU execution stage is high in the same abnormal frames; judged via Spatial Runtime process (`Spot Lights`, `Shadow`) | `analysis-spatial-engine.md` |
| `gpu_2d_effect_overload` | 2D 渲染特效过重 | `Effect_3DClipCount` / `Effect_3DTRSCount` / `Effect_GlassEffectCount` / `Effect_TotalEffectsCount` ↑ + GPU time ↑ | 2D Render GPU pressure is shown in the same abnormal frames; judged via Spatial Runtime process | `analysis-spatial-engine.md` |

### 4.3 `resource_type: memory`

| `bottleneck_category` | 中文 | Evidence signature (metric) | Evidence signature (slice / track / table) | Owning topic |
|---|---|---|---|---|
| `memory_gc` | GC | GC frequency / duration ↑; heap / PSS / RSS growth | GC event timeline, `concurrent copying`, allocation peaks | `analysis-memory.md` |
| `memory_oom` | OOM | Heap approaching limit; allocation failures | OOM event / tombstone, allocation-failure logs | `analysis-memory.md` |
| `memory_lmk` | LMK | System low-memory; process killed | LMK event, process kill, `lowmemorykiller` | `analysis-memory.md` |

> **`cpu_gc_storm` vs `memory_gc` (allowed dual-classification):** GC can be both a CPU consumer and a memory-pressure signal. Because the output is a list, a GC storm that both steals CPU on the critical path AND reflects heap-allocation pressure MAY legitimately produce two entries: `cpu_gc_storm` **and** `memory_gc`. Emit both only when both evidence signatures hold; otherwise emit the one that the evidence supports.

## 5. Output Schema (Standalone File)

The whole file is `session-output-<timestamp>/root-cause-classification.yaml`. It is self-describing: a small header identifies the run, followed by the classification list.

```yaml
# session-output-<timestamp>/root-cause-classification.yaml
schema_version: 2                      # bump on enum changes (§7)
session_dir: "session-output-20260731-140312"
final_summary: "./final-summary.md"    # provenance link; the summary itself does NOT embed this classification
root_cause_classification:
  - resource_type: gpu                 # L1 enum (§3), required
    bottleneck_category: gpu_geometry_complexity   # L2 enum (§4), required, must be valid for resource_type
    conclusion_level: likely           # confirmed | likely | candidate | insufficient_evidence (same enum as Output Contract)
    time_window: "2026-07-31 14:03:12 ~ 2026-07-31 14:03:25"   # optional; abnormal window for this classification
    evidence_refs: ["spatial-engine:e1", "spatial-engine:e3"]  # required; refs into underlying topic evidence ids
    note: "Triangle/Vertex counts spike during scene switch; gpu_frame_end binds." # optional, one line
  - resource_type: cpu
    bottleneck_category: cpu_gc_storm
    conclusion_level: candidate
    evidence_refs: ["memory:e2"]
    note: "Concurrent-copying STW overlaps late-frame cluster on the main cluster."
```

Field rules:

- `resource_type`: closed enum from §3. Required.
- `bottleneck_category`: closed enum from §4. Required. MUST be a valid child of `resource_type`; an invalid pair is a contract violation.
- `conclusion_level`: reuse the exact enum and semantics from the [Output Contract](output-contract.md).
- `evidence_refs`: required, non-empty for any non-`undetermined` entry. Each ref is the `id` of an evidence item declared in an underlying topic output's `evidence` list (per the [Output Contract](output-contract.md)). To support this, keep those per-topic `evidence[*].id`s stable. Because per-topic ids restart at `e1` in each topic, when aggregating across topics disambiguate with a topic prefix (e.g. `binder:e1`, or `b1`/`c1` style) so each ref stays unique. A classification with no resolvable evidence is not allowed (guards against "guessed" classifications).
- `time_window` / `note`: optional.

## 5.1 Fast Disambiguation Rules

- App `doFrame` is over budget because of local `System_Update`, Compose, traversal, or other app execution: use `cpu_app_main_thread_busy_or_blocked`; do not add service contention.
- Only a client Binder wait or callee name is known: use the app-side category. If repeated per-frame creation/start/configuration is proven, use `cpu_app_service_call_amplification`; do not use `cpu_system_service_contention`.
- Binder wait plus server lock/queue/runnable starvation or server work over its own budget: use `cpu_system_service_contention`; add the app-side wait only when it is independently evidenced.
- High DrawCall/triangle/texture counters with CPU submit or `System_Update` pressure: use `cpu_drawcall_overload` or `cpu_ec_submit_busy`. Use a `gpu_*` category only with same-window GPU execution evidence.
- GC, GPU utilization, temperature, or frequency is a supporting signal, not a category by itself. Require the corresponding binding-side evidence; otherwise remain conservative.

The `note` must explain the completed chain in one sentence: `window + owner + mechanism + why this category`, and must not claim more than the referenced evidence proves.

## 6. Insufficient Evidence

When evidence cannot support any classification, the file still exists and carries exactly one entry:

```yaml
# session-output-<timestamp>/root-cause-classification.yaml
schema_version: 2
session_dir: "session-output-20260731-140312"
final_summary: "./final-summary.md"
root_cause_classification:
  - resource_type: undetermined
    bottleneck_category: undetermined
    conclusion_level: insufficient_evidence
    evidence_refs: []
    note: "No trace / abnormal window not localizable; see limitations."
```

Consistency rule: `resource_type: undetermined` MUST pair with `bottleneck_category: undetermined` and `conclusion_level: insufficient_evidence`, and vice versa. This keeps insufficient-evidence samples out of the accuracy denominator during scoring.

## 7. Enum Stability (Baseline Discipline)

- The Level 1 and Level 2 value sets in §3–§4 are **closed**. Do not emit free text, and do not invent new keys inline.
- Adding, renaming, or removing an enum value is a contract change: bump this file and re-baseline. Older outputs stay comparable only against the enum version they were produced under.

## 8. Evaluation / Baseline Scoring Guidance

Because the output is a set of entries, score as sets, not as a single label:

- **Level 1 accuracy:** compare the set of `resource_type` values against the golden set (set match / Jaccard).
- **Level 2 accuracy:** compare the set of `(resource_type, bottleneck_category)` pairs against the golden set.
- **Evidence-support check:** every predicted entry MUST have non-empty `evidence_refs` that resolve to real `evidence` items. Entries that classify correctly but without resolvable evidence should be penalized (guards against lucky guesses).
- **Insufficient handling:** entries with `undetermined` / `insufficient_evidence` are excluded from the accuracy denominator and scored separately (e.g. as an abstention-correctness metric).
