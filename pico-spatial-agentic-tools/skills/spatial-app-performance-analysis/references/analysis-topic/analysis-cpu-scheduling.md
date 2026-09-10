# CPU Scheduling Analysis Workflow

Used to analyze performance issues in PICO OS6 caused by scheduling latency, runnable thread starvation, runqueue pressure, preemption, migration, CPU frequency, or abnormal big/little core allocation.

## Topic Execution Instructions

This subprotocol is executed only when the Main protocol in [Analysis Topic Routing](../routing/analysis-topic-routing.md) adds it to the execution queue. The Main protocol owns activation. Execute this subprotocol from Availability Check through the Evidence Order, closure assessment, and Output Supplement Items. Hand back cross-topic evidence to the Main protocol; do not activate or load other subprotocols from this document.

## Availability Check

Before performing root cause analysis, confirm if the user has provided any of the following evidence:
- Perfetto sched Slice
- Target process / thread name
- runnable / running / blocked states of threads near the problem window
- CPU frequency or core distribution data
- runqueue, migration, or preempt evidence

If none are available, first request the user to supplement the Perfetto trace containing sched data and the problem time window.

## Evidence Order

1. Confirm the target thread and problem time window.
2. Judge if the target thread is runnable but not running.
3. Check runqueue pressure and competing threads on the same CPU / same cluster.
4. Check CPU frequency, idle states, migration, and preemption.
5. Judge if scheduling latency can directly explain the user phenomenon.

## Common Signals

- `sched_switch`
- `sched_wakeup`
- runnable but not running
- `runqueue`
- `migration`
- `preempt`
- CPU frequency reduction
- Unreasonable big/little core allocation

## Root Cause Patterns

### runnable Thread Starvation

Evidence needed:
- Target thread is runnable within the problem window.
- Target thread did not obtain sufficient running time.
- Competing tasks or scheduling policies can explain the latency.

### Core Selection or Frequency Issues

Evidence needed:
- Critical thread runs on a weak core during heavy load, or CPU frequency is low.
- This slowdown coincides with the user phenomenon window.

### Not a Scheduling Problem

Do not list CPU scheduling as the root cause in the following cases:
- Target thread is blocked, sleeping, or waiting for Binder / locks / I/O.
- Scheduling latency is not in the same window as the user phenomenon.
- The critical path is actually in GPU / compositor / memory / GC.

## Output Supplement Items

After the analysis, output according to the unified protocol defined in `output-contract.md`. Set `issue_type_key` to `cpu_sched_latency` and supplement the following topic fields in `extensions.cpu_sched`:
- thread_state_summary: Summary of target thread states (running/runnable/blocked)
- sched_latency_ms: Quantification of runnable scheduling latency or insufficient running time (ms)
- runqueue: runqueue observation conclusion (length, concentrated on which CPUs/clusters)
- cpu_cluster_freq: Summary of CPU / core distribution and frequency context
- contenders: List of known competing threads

## Controller Handoff

Hand back scheduling-latency, runnable-state, and critical-path evidence to the Main protocol. The Main protocol decides whether the evidence activates another subprotocol; this document does not name or activate other subprotocols.
