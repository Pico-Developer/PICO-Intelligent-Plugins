# Memory Performance Analysis Workflow

Used to analyze PSS/RSS growth, OOM, LMK, GC jitter, heap leaks, reclamation pressure, or memory-related jank in PICO OS6.

## Topic Execution Instructions

This subprotocol is executed only when the Main protocol in [Analysis Topic Routing](../routing/analysis-topic-routing.md) adds it to the execution queue. The Main protocol owns activation. Execute this subprotocol from Availability Check through the Evidence Order, closure assessment, and Output Supplement Items. Hand back cross-topic evidence to the Main protocol; do not activate or load other subprotocols from this document.

## Availability Check

Before performing root cause analysis, confirm if the user has provided any of the following evidence:
- PSS / RSS / meminfo snapshots
- GC logs or GC timestamps
- LMK / OOM records
- Perfetto memory counters or App process Slices
- Time window where the user-visible problem occurred

If none are available, first request the user to supplement the meminfo / PSS trend, GC logs, LMK/OOM evidence, and operation window.

## Evidence Order

1. Confirm the problem window and target process.
2. Judge if memory growth, GC, reclamation, LMK, or OOM coincides with the problem window.
3. When data allows, distinguish between Java/Kotlin heap, native heap, graphics / DMA-BUF, and system memory pressure.
4. Judge if GC / reclamation blocks critical UI, Render, Spatial, or Runtime threads.
5. Judge if memory is a direct root cause, an upstream cause, or a related signal.

## Common Signals

- `PSS`, `RSS`, `USS`
- Java heap / native heap growth
- `GC`, `concurrent copying`, `collector transition`
- `OOM`, `LMK`, `lowmemorykiller`
- swap / reclaim
- DMA-BUF / graphics memory

## Root Cause Patterns

### Jank Caused by GC

Evidence needed:
- GC timestamp coincides with the problem window.
- Critical App / Runtime threads are paused, delayed, or competing for resources with GC.
- Frame duration or interaction latency rises in the same window.

### Memory Leak or Continuous Growth

Evidence needed:
- PSS / RSS / heap continues to grow with repeated operations.
- Memory does not fall back after scene exit or operation end.
- Growth is related to object or resource lifecycle.

### LMK / OOM Risk

Evidence needed:
- LMK / OOM logs or memory pressure events exist.
- Target process or critical dependency is killed, restarted, or severely reclaimed.

## Output Supplement Items

After the analysis, output according to the unified protocol defined in `output-contract.md`. Set `issue_type_key` to `memory_gc_jank` and supplement the following topic fields in `extensions.memory`:
- memory_metrics: Memory metrics and units (summary of PSS/RSS/USS, heap, DMA-BUF, etc.)
- gc_events: GC / reclamation events (type, count, critical timestamps, STW situation)
- lmk_oom: LMK / OOM information (whether occurred, related processes, timestamps)
- baseline_compare: Comparison method and conclusion between before/after or baseline / candidate

## Controller Handoff

Hand back memory-pressure, lifecycle, and critical-path evidence to the Main protocol. The Main protocol decides whether the evidence activates another subprotocol; this document does not name or activate other subprotocols.
