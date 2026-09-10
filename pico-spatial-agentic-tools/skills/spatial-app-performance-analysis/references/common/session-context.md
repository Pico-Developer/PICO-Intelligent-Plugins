# Session Context Collection

Before entering data capture or performance analysis, collect the information on this page first. The goal is to ensure that subsequent trace capture, SQL queries, and topic analysis are aligned with the same application, device, and problem scenario.

## Mandatory Items

If the following information is missing, first use existing script capabilities to auto-detect what is detectable yourself (device type via `check_device.py`; APK type via `check_debuggable.py` once the package is known and a device is reachable), and follow up with the user only for fields that have no auto-detection path (the app package name generally must come from the user). Then confirm the resolved values with the user via the Environment Confirmation Gate below; do not enter root cause analysis directly, and do not default to asking the user for every mandatory item when some are auto-detectable.

| Field | Description | Example |
|---|---|---|
| App Package Name | Package name of the target PICO OS6 application | `com.example.spatialapp` |
| Device Type | Physical device or emulator | Physical device / Emulator |

> **Auto-detection**: Executing `python scripts/check_device.py [-s <serial>] --json` can automatically determine if it's a physical device/emulator and whether it's a PICO Swan device, outputting the `final_verdict` and `pico_os` fields.

| APK Type | release or debug | release / debug |

> **Auto-detection**: Executing `python scripts/check_debuggable.py -s <serial> --app <package> --json` can automatically detect whether the APK is debuggable, outputting `DEBUGGABLE` / `NOT_DEBUGGABLE` / `UNKNOWN`.

## Recommended Items

It is recommended to collect these as much as possible; you can continue if they are missing, but limitations need to be marked in the conclusion.

| Field | Description | Example |
|---|---|---|
| Problem Scenario | In which business scenario did the jank/dropped frames occur | Dragging a model, opening the spatial panel, loading a large scene |
| Reproduction Path | Operation steps from startup to the occurrence of the problem | Launch app → Enter Scene A → Drag model for 10 seconds |
| Capture Duration | Duration of trace or live data collection | 30 seconds / 45 seconds / 60 seconds |
| User Visible Phenomenon | Performance seen by the user | Continuous dropped frames, startup latency, frozen screen, input latency |

- The Reproduction Path and User Visible Phenomenon are Recommended, not Mandatory: they help shape the capture command's reproduction steps and the analysis entry, so try to collect them together with the environment confirmation rather than as a separate later step. 
- If the user cannot provide a reproduction path (or a symptom), do not block.
- Under a plan/planning flow, collect what the user can give during the plan phase and continue to the performance-data plan.

## Optional Items

This information helps explain environment differences and reproduction stability.

| Field | Description | Example |
|---|---|---|
| OS Version | PICO OS version | OS6.x |
| SDK Version | Spatial SDK / OpenXR SDK version | Spatial SDK x.y.z |
| Device Model | Specific device model | PICO device model |
| Refresh Rate | Target refresh rate | 90Hz |
| First Startup | Whether cold start or first-time resource loading is involved | Yes / No |
| Network Status | Whether the scenario depends on network resources | Wi-Fi / Offline |
| Resource Scale | Scale of resources such as models, textures, videos, audio, etc. | Large models / Multiple textures / Multiple videos |

## Minimum Follow-up Template

Use this template only for the mandatory items that could not be auto-detected (for example when no device is reachable, or the package name is unknown). Do not ask for items you have already auto-detected; instead surface the detected values in the Environment Confirmation Gate for confirmation. When nothing is detectable yet, you may ask for all three:

```text
Before continuing the analysis, I need to confirm 3 mandatory pieces of information:
1. What is the app package name?
2. Is the device type a physical device or an emulator?
3. Is the APK type release or debug?

If you already have a trace / SQL / screenshot, you can also send it over.
```

## Context Completeness Judgment

- Mandatory items complete: Can enter data availability check.
- Mandatory items incomplete: First auto-detect the detectable ones (device type, APK type) with the scripts above, then follow up with the user only for what cannot be detected (typically the app package name). Confirm the resolved values via the Environment Confirmation Gate before proceeding.
- Recommended items missing: Can continue, but need to explain limitations in the conclusion.
- Optional items missing: Does not block analysis; follow up only when environment differences need to be explained.

## Status Confirmation Before Capture

Before entering data capture, it is recommended to first confirm that the App is running in the foreground:

> **Auto-detection**: Execute `python scripts/check_foreground.py -s <serial> --app <package>` to check if the target App is in the foreground, returning `true` / `false`.

## Environment Confirmation Gate

After the mandatory items are collected — whether provided by the user or filled in by auto-detection — confirm the resolved environment with the user before entering data capture or analysis. This gate is mandatory and exists to avoid capturing or analysing against the wrong app, device, or build type. It is a normal turn in the session, not a hard stop; the analysis simply waits for the confirmation before continuing.

Behavior:

1. Present the resolved values the analysis will actually use, so the user can verify or correct them:
   - App package name.
   - Device type (physical device / emulator), including the `final_verdict` / `pico_os` result from `check_device.py` when it was auto-detected.
   - APK type (release / debug), including the `check_debuggable.py` result when it was auto-detected.
   - Foreground status, when it was checked above.
2. Wait for the user to confirm or correct these values before proceeding to "Capture Performance Data".
3. Prefer a structured confirmation capability when the host agent supports one (for example `AskUserQuestion`): offer the detected values as the default selectable option, plus an option for "values are wrong / let me adjust". When the host has no such capability, fall back to the plain-text [Minimum Follow-up Template](#minimum-follow-up-template) above. Do not hard-depend on any specific tool being available.
4. Run the gate once. Skip it only when the user has already stated every mandatory item explicitly in this session and nothing auto-detected contradicts those values; do not re-ask what the user already pinned down.
5. Never auto-proceed on a low-confidence detection. If `check_debuggable.py` returns `UNKNOWN`, the device verdict is ambiguous, or auto-detection disagrees with what the user said, surface the conflict and ask before capture.
6. When the APK type is `NOT_DEBUGGABLE` (a release build), do not silently proceed. State the evidence impact in the gate, then continue capture without blocking (unless the user asks to switch builds) and carry the impact forward as an analysis limitation:
   - Still fully available on a release build: system-level Perfetto trace, `SpatialFrames` / `SpatialMetrics`, and the `fast-perf` live report — none of these require a debuggable app.
   - Possibly limited or unavailable: app-level `simpleperf` call-stack profiling (the one-click script's `app_profiler.py -p <package>` step) and any `run-as`-based per-app data, because Android app-level profiling generally requires a debuggable or profileable app. If this data cannot be collected, record `simpleperf_not_enabled` / limited app-level CPU stacks as a limitation in the conclusion rather than treating its absence as evidence.

## Trace Identity Confirmation Convention

After obtaining a trace, prioritize executing `python scripts/spatial_probe.py --trace <trace> --package <package> --detail --output session-output-<timestamp>/performance-data/trace-probe-detail.yaml` to solidify process and thread identities. `probe_app_identity()` is responsible for the target App process and App frame driving thread, `probe_spatial_runtime_identity()` is responsible for Spatial Runtime, OpenXR Runtime, and compositor candidates, and `probe_identities()` only serves as a compatibility entry to schedule these detections in turn and then check key threads.

The frame driving thread `utid` must be read from `identities.app_frame_driving_threads.candidates[0].utid` in `trace-probe-detail.yaml`; hardcoding the thread name `main` is prohibited.
