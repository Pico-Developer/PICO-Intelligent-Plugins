# Spatial Audio Performance Analysis Workflow

Used to analyze spatial audio related performance issues in PICO OS6, including spatialization API selection, `AudioPlayerController` instance counts, resource lifecycle, `AudioMixGroups` batch control, frame rate / latency / memory impacts, and empirical verification of indicators not quantified officially.

## Topic Execution Instructions

This subprotocol is executed only when the Main protocol in [Analysis Topic Routing](../routing/analysis-topic-routing.md) adds it to the execution queue. The Main protocol owns activation. Execute this subprotocol from Availability Check through its core principles, evidence order, closure assessment, and output requirements. Hand back cross-topic evidence to the Main protocol; do not activate or load other subprotocols from this document.

## Availability Check

Before performing root cause analysis, confirm if the user has provided any of the following evidence:
- Spatial audio API usage method, such as `ChannelAudioComponent`, `AmbientAudioComponent`, `ObjectAudioComponent`, or `SpatialAudioTrackExtension`.
- Records of creation, reuse, release, or `close()` of `AudioPlayerController`, `AudioResource`, `AudioMixerGroupResource`.
- Perfetto trace, thread scheduling, decoding thread, main thread, or system service activity within the problem time window.
- Audio resource format information, such as channel count, sampling rate, duration, purpose, and whether 3D positioning is required.
- User-visible phenomenon, such as dropped frames, jank, playback latency, creation failure, memory rise, or resource leak.

The subprotocol can execute partially from a trace when audio-service or spatializer evidence is present, even if API and lifecycle data are unavailable. In that case, analyze the observed service/critical-path mechanism, mark API and lifecycle fields as evidence gaps, and return the missing fields as next validation. Do not block the subprotocol merely because the strongest App-side conclusion is not yet provable. If there is neither audio evidence nor a relevant user symptom, the Main protocol may leave the subprotocol not activated.

## Core Principles

Spatial audio performance analysis prioritizes starting from API selection. The core judgment principle is: do not use high-overhead APIs for audio that does not require spatialization.

| API Type | Spatialization Capability | Performance Overhead Level | Priority Judgment |
|---|---|---|---|
| Android Native API (`SoundPool` / `MediaPlayer` / `AudioTrack`) | No spatialization | Lowest | Prioritize for ordinary audio, short UI sound effects, and playback without need for spatial positioning |
| `ChannelAudioComponent` | No spatialization | Low | Use when needing to integrate into the spatial SDK audio component system but without need for spatialization |
| `AmbientAudioComponent` | Head tracking + HRTF, no distance attenuation | Medium | Ambient sound, non-precise positioning but audio needing to change with head movement |
| `ObjectAudioComponent` | Full 3D positioning + distance attenuation + HRTF | High | Sound sources needing clear spatial position, distance changes, and HRTF |
| `SpatialAudioTrackExtension` | Depends on configuration mode | Depends on configuration | Suitable for transforming existing players into spatialized playback; evaluate according to actual mode |

## API Selection Check

### Android Native API

`SoundPool`, `MediaPlayer`, `AudioTrack` do not perform spatialization processing and have the lowest performance overhead. Short UI sound effects should prioritize `SoundPool`, as the official documentation clarifies that its short sound effect playback latency is lower. If the audio is just button sounds, prompt sounds, ordinary background sounds, or media playback without the need for spatial positioning, it should not be upgraded to `ObjectAudioComponent`.

### ChannelAudioComponent

`ChannelAudioComponent` does not perform spatialization processing and has low overhead. It is suitable for scenarios that need to use the spatial audio component system, but the audio itself does not require head tracking, HRTF, distance attenuation, or 3D positioning. During performance analysis, if it is found that non-positioning audio uses `ObjectAudioComponent`, a downgrade to `ChannelAudioComponent` or Android native API should be recommended first.

### AmbientAudioComponent

`AmbientAudioComponent` provides head tracking and HRTF, but no distance attenuation, with medium overhead. It is suitable for atmosphere sound, environmental noise, or sound that does not require precise 3D position changes. If the business only requires a "sense of space" without distance attenuation, Ambient should be considered first over Object.

### ObjectAudioComponent

`ObjectAudioComponent` provides full 3D positioning, distance attenuation, and HRTF, with high overhead. It is only suitable for individual spatial sound sources that truly need positioning. `ObjectAudioComponent` only supports mono audio; if multi-channel audio is passed in, the system will automatically downmix it to mono, causing extra decoding resource waste. Performance analysis must check if the audio source for Object Audio is mono.

### SpatialAudioTrackExtension

The performance overhead of `SpatialAudioTrackExtension` depends on the configuration mode. When an existing player needs to be modified for spatialized playback, this solution should be evaluated first rather than directly rewriting to high-overhead components. During analysis, its configuration mode, spatialization capability, whether head tracking is enabled, whether HRTF and distance attenuation are needed must be recorded.

## Instance Count Hard Limits

Spatial audio performance analysis cannot only count instances currently playing; it must also count the creation, reuse, and release of `AudioPlayerController`.

| Scope | Type | Limit | Impact of Exceeding Limit |
|---|---|---|---|
| Single App | Object Audio + Ambient Audio total | Max 40 `AudioPlayerController` | Exceeding the limit leads to creation failure |
| Single App | Channel Audio | Max 40 | Exceeding the limit leads to creation failure |
| System Level | Various audio instances | Max 256 | Exceeding the limit leads to creation failure or resource competition |

During analysis, three quantities must be distinguished: created count, currently playing count, and released count. If a business frequently creates but does not reuse, or does not release the Controller after stopping playback, it may approach the limit even if the playing count at a single moment is not high, triggering creation failure, memory rise, or resource leaks.

## System Audio Service Hotspot Patterns

Experience from this protocol execution shows that spatial audio issues in trace often do not first appear with App-side object names like `ObjectAudioComponent` or `AudioPlayerController`. Instead, they first manifest as audio service hotspots in `system_server`. Therefore, the protocol needs to accept the reality that "server-side phenomena appear first" and then back-infer App-side usage.

### High-frequency Hotspot 1: `getActivePlaybackConfigurations*`

If `IAudioService::getActivePlaybackConfigurations*` appears heavily within the problem window, first suspect:

- The app frequently queries current playback configurations
- Audio state polling is too dense
- Playback configuration object serialization / `writeToParcel()` causes extra overhead

This type of problem is not necessarily due to large spatialization overhead itself, but could be an unreasonable **playback configuration query strategy**. Do not directly write it as "spatial audio algorithm causing jank" during analysis.

### High-frequency Hotspot 2: `playerEvent`

If `IAudioService::playerEvent` is very dense within the problem window, first suspect:

- Player state changes are too frequent
- The app constantly triggers play / pause / stop / seek or similar state transitions
- Audio lifecycle is too tightly bound to business state, leading to a server-side event storm

### High-frequency Hotspot 3: `releasePlayer`

If `IAudioService::releasePlayer` or `PlaybackActivityMonitor.releasePlayer()` becomes obviously heavy, first suspect:

- `AudioPlayerController` / player objects are frequently created and destroyed without reuse
- Batch release of players during scene transitions, entity destruction, or component reconstruction
- The release path forms lock contention with internal operations like playback state recovery and mute port updates

### High-frequency Hotspot 4: `PlaybackActivityMonitor` Lock Contention

If `monitor contention` directly appears on methods like `PlaybackActivityMonitor.portMuteEvent()`, `playerEvent()`, `getActivePlaybackConfigurations()` in the trace, judge with priority:

- Audio service internal lock contention is the slow response amplification point
- The app triggered too dense playback events / configuration queries / release behaviors in a short time
- This type of problem looks more like an **audio lifecycle and control mode design issue** rather than simple DSP / HRTF computation being too heavy

### Secondary Hotspot: `IPowerManager` and Audio Linkage

If `IPowerManager::acquireWakeLockAsync`, `releaseWakeLockAsync`, `updateWakeLockUidsAsync` appear alongside `IAudioService` hotspots, record them as secondary amplification factors. They usually indicate:

- Audio playback control is coupled with wake lock management
- Audio service pressure may be amplified along the power management chain

However, do not mistake Power as the main root cause unless Power evidence outweighs Audio.

## Common Performance Pitfalls

### Object Audio Playing Multi-channel Audio

`ObjectAudioComponent` only supports mono. Passing multi-channel audio will automatically downmix to mono, which neither obtains multi-channel positioning benefits nor avoids wasting decoding resources. When this pattern is found, the resource should be converted to mono before being integrated into Object Audio.

### Non-positioning Audio Using ObjectAudioComponent

Using `ObjectAudioComponent` for non-positioning audio, background sounds, ordinary UI sound effects, or sound sources that do not change with spatial position will introduce unnecessary 3D positioning, distance attenuation, and HRTF costs. It should be downgraded to `ChannelAudioComponent` or Android native API based on needs.

### Short UI Sound Effects Using High-overhead APIs

Short UI sound effects should not use high-overhead spatialization APIs. The official recommendation is to prioritize `SoundPool` for short sound effects because latency is lower and spatialization calculation is not needed.

## AudioMixGroups Performance Related

The core value of `AudioMixGroups` is batch control. Through `AudioMixerGroupResource`, the volume or playback speed of an entire group can be controlled at once, avoiding the App layer having to traverse multiple players one by one for setting. In multi-source scenarios, if volume, speed, or playback states are frequently modified one by one, check if they can be changed to `AudioMixerGroupResource` batch control.

Lifecycle must be strictly managed. `AudioMixerGroupResource` must call `close()` after use; `clear()` must be called when the component is destroyed or removed. Otherwise, resource leaks may occur and manifest as memory rise, instance residue, or subsequent creation failures during long runs, scene transitions, or repeated entering and exiting.

Thread constraints must also be included in the check. `AudioMixerGroupsComponent` related operations must be called on the main thread. If called on a non-main thread, it may cause exceptions, state inconsistency, or competition with the component lifecycle.

Accessing objects that have already been `close()`-ed is prohibited. Calling methods like `getVolume()` on closed objects will throw an `IllegalStateException`. If the problem manifests as occasional crashes or state reading failures, check if there are paths that continue to access objects after they are closed.

## Frame Rate / Latency / Memory Analysis

### Frame Rate

Analyze the audio thread, main thread, decoding thread, and system service scheduling in the same window within the trace. Only when audio resource creation, decoding, batch Controller creation, main thread audio component operations, or system service waiting occur within the abnormal frame window can spatial audio further be judged as the upstream pressure source of the frame rate issue.

### Latency

The official documentation only clarifies that `SoundPool` short sound effect latency is lower; other APIs have no public latency indicators. When analyzing playback latency, it is necessary to distinguish between business latency from trigger to playback, resource loading / decoding latency, thread scheduling latency, system service return latency, and spatialization processing latency. In the absence of measured data, only a judgment to be verified can be given; it cannot be written as a quantified conclusion.

### Memory

There is no officially quantified data on the memory usage of various spatial audio objects. Typical troubleshooting points are `AudioPlayerController` not released, `AudioResource` not released, `AudioMixerGroupResource` not `close()`-ed, not `clear()`-ed when components are removed, and resource residue caused by frequent creation without reuse. If PSS / RSS continues to rise, continue checking for leaks in combination with the memory workflow.

## Matters Not Clarified by Official

The following matters have not been explicitly quantified officially, and must be marked as "requires empirical verification" in conclusions:

| Matters Not Clarified | Analysis Handling Method |
|---|---|
| Specific usage of CPU / GPU / DSP respectively | Requires empirical verification through trace, system metrics, or specialized stress testing |
| Recommended sampling rates and impact of sampling rate on performance | Requires A/B empirical testing according to resource format, device, and scenario |
| Direct quantification of spatial audio impact on FPS | Requires empirical testing through enabling/disabling spatialization in the same scenario and controlling variables |
| Latency values of each API | Requires empirical testing through end-to-end instrumentation or specialized audio tools |
| Memory usage of audio resources and `AudioMixerGroupResource` | Requires empirical testing in combination with PSS / RSS, object quantity, and lifecycle |

## Evidence Order

Strictly execute the following evidence chain; do not reverse-infer the root cause:

```text
User phenomenon and time window
    -> API type and audio purpose
        -> AudioPlayerController / Resource / MixGroup count and lifecycle
            -> Audio resource format (channel count, sampling rate, duration)
                -> Perfetto trace (main thread, audio thread, decoding thread, system service)
                    -> Whether in the same window as dropped frames, latency, or memory rise
```

If App-side API evidence is temporarily missing but the trace has already shown clear `IAudioService` / `PlaybackActivityMonitor` hotspots, the following "server-side first" variant evidence chain is permitted:

```text
User phenomenon and time window
    -> Audio service hotspots in Perfetto trace (IAudioService / PlaybackActivityMonitor / AudioTrack)
        -> Server-side method types (getActivePlaybackConfigurations / playerEvent / releasePlayer)
            -> Server-side slow cause (lock contention / GC / scheduling / downstream Binder)
                -> Back-infer App-side API type, instance lifecycle, and resource format
```

However, the final conclusion must still return to App-side API, instance count, and lifecycle. It is not allowed to directly write it off as "spatial audio API misuse" solely based on server-side hotspots.

## Bottleneck Judgment Matrix

| Observation Result | Priority Suspected Direction |
|---|---|
| Non-positioning audio uses `ObjectAudioComponent` | API selection too heavy; prioritize downgrading to Channel or native API |
| `ObjectAudioComponent` uses multi-channel resources | downmix wastes decoding resources; prioritize changing to mono resources |
| Short UI sound effects use spatialization components | Improper API selection; prioritize changing to `SoundPool` |
| `AudioPlayerController` creation count approaches 40 | Risk of single-app instance limit; check reuse and release |
| Controller / Resource not released after stopping playback | Risk of resource leak; check `close()` and lifecycle binding |
| Traversing multiple sound sources one by one to adjust volume or speed | Lack of batch control; consider `AudioMixerGroupResource` |
| MixGroup not `clear()`-ed after component removal | Risk of resource residue or leak |
| Non-main thread operation on `AudioMixerGroupsComponent` | Thread violation; check main thread call constraints |
| Already `close()`-ed object still being accessed | Lifecycle error; may throw `IllegalStateException` |
| Audio creation / decoding / main thread operations concentrated in dropped frame window | Spatial audio may be upstream pressure; requires trace for further verification |
| `IAudioService::getActivePlaybackConfigurations*` appears at high frequency | Playback configuration queries too dense, polling too frequent, configuration serialization overhead too large |
| `IAudioService::playerEvent` appears at high frequency | Playback state changes too dense, player event storm |
| `IAudioService::releasePlayer` appears at high frequency | Frequent player destruction, lack of reuse, lifecycle jitter |
| Lock contention appears in `PlaybackActivityMonitor.*` | Internal lock contention in audio service; prioritize checking App-side event density and release paths |
| `IAudioService` hotspots accompanied by `IPowerManager` calls | Audio control linked with wake locks; Power is a secondary amplification factor |

## Performance Checklist

1. Is spatialization needed? If not, use Android native API or `ChannelAudioComponent`.
2. Is `ObjectAudioComponent` misused for non-positioning audio?
3. Is the audio source for Object Audio mono?
4. Is the total count of `AudioPlayerController` instances approaching the 40 limit?
5. Are `AudioResource` / `AudioPlayerController` `close()`-ed / released in time?
6. Is `AudioMixerGroupResource` used for batch control of multi-source audio?
7. Is `AudioMixerGroupResource` `close()`-ed when not in use? Is `clear()` called when components are removed?
8. Are all `AudioMixerGroupsComponent` operations on the main thread?
9. Is `SoundPool` used for short UI sound effects?
10. Is `SpatialAudioTrackExtension` prioritized for spatializing existing players?

## Output Requirements

Conclusions must include:
1. **Phenomenon**: Specific manifestation and time window of dropped frames, latency, creation failure, memory rise, or resource leak.
2. **Evidence**: API type, audio purpose, instance count, resource format, lifecycle records, and trace evidence in the same window.
3. **Server-side Judgment**: Whether it has hit system audio service hotspots like `IAudioService` / `PlaybackActivityMonitor` / `AudioTrack`; if so, whether the hotspot method belongs to query, event, release, or audio writing.
4. **Selection Judgment**: Whether the current API matches the audio purpose and whether there is misuse of high-overhead APIs.
5. **Resource Judgment**: Whether `AudioPlayerController`, `AudioResource`, `AudioMixerGroupResource` are reused, released, and `close()`-ed in time.
6. **Action**: Specific suggestions like downgrading API, changing to mono, using `SoundPool`, reusing Controller, supplementing `close()` / `clear()`, using MixGroup batch control, etc.
7. **Constraints and Next Steps**: Data not quantified officially must be marked as needing empirical verification, with an explanation of how to verify in the next step through trace, instrumentation, or A/B stress testing.

## Controller Handoff

Hand back audio-path, audio-service, lifecycle, and critical-path evidence to the Main protocol. The Main protocol decides whether the evidence activates another subprotocol; this document does not name or activate other subprotocols.
