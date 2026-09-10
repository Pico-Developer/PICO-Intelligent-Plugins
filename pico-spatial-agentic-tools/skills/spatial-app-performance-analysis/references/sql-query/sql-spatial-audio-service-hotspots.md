# Spatial Audio Service Hotspots SQL Query Set

This document supplements the execution details for "hit system_server audio service hotspots first, then infer app-side spatial audio issues" in `analysis-spatial-audio.md`. The goal is not merely to prove that `IAudioService` activity exists, but to further narrow down an audio-related Binder wait on the critical path to:

1. The heaviest system audio-service hotspot methods within the issue window
2. Key audio-service slices within the worst doFrame window
3. `PlaybackActivityMonitor`-related lock contention
4. The amplification linkage between `IAudioService` and `IPowerManager`
5. App-side spatial audio component/controller lifecycle clues

Before execution, replace placeholders:

- `<window_start_ns>`: issue window start
- `<window_end_ns>`: issue window end
- `<worst_doframe_start_ns>`: worst doFrame start
- `<worst_doframe_end_ns>`: worst doFrame end
- `<target.package.name>`: target app package name

Execution contract: run these SQL snippets through `pico-cli perf trace query --session <sessionId> --sql "..."` after `pico-cli perf trace load`. If the daemon/session is gone, restart the daemon and reload the trace; do not invoke `trace_processor_shell` directly during normal analysis.

---

## query-01-iaudio-service-hotspot-summary.sql: Full-Window IAudioService Hotspot Summary

Purpose: first confirm what types of `IAudioService` methods are heaviest within the issue window, and prioritize determining whether it is overly dense config queries, a playback event storm, or release-player jitter.

```sql
SELECT
  s.name AS slice_name,
  COUNT(*) AS cnt,
  ROUND(SUM(s.dur) / 1000000.0, 3) AS total_ms,
  ROUND(MAX(s.dur) / 1000000.0, 3) AS max_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = 'system_server'
  AND s.ts < <window_end_ns>
  AND s.ts + s.dur > <window_start_ns>
  AND (
    s.name GLOB 'AIDL::java::IAudioService::*'
    OR s.name GLOB '*PlaybackActivityMonitor*'
    OR s.name GLOB '*AudioService*'
  )
GROUP BY s.name
ORDER BY total_ms DESC, max_ms DESC
LIMIT 100;
```

Interpretation highlights:

- High `getActivePlaybackConfigurations*`: prioritize suspecting overly dense playback-config queries, excessive polling, or heavy serialization of config objects.
- High `playerEvent`: prioritize suspecting overly frequent playback state switches, event storms, or overly tight lifecycle binding.
- High `releasePlayer`: prioritize suspecting frequent creation/destruction of players / `AudioPlayerController`, with insufficient reuse.

---

## query-02-iaudio-service-hotspot-slices-window.sql: Full-Window Audio-Service Hotspot Details

Purpose: flatten all audio-service hotspot slices within the issue window, sort by duration to view the slowest instances, and pick typical time ranges for further drill-down.

```sql
SELECT
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms,
  s.depth
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = 'system_server'
  AND s.ts < <window_end_ns>
  AND s.ts + s.dur > <window_start_ns>
  AND (
    s.name GLOB 'AIDL::java::IAudioService::*'
    OR s.name GLOB '*PlaybackActivityMonitor*'
    OR s.name GLOB '*AudioService*'
    OR s.name GLOB '*AudioTrack*'
  )
ORDER BY s.dur DESC, s.ts ASC
LIMIT 200;
```

Interpretation highlights:

- First check whether they concentrate on a small number of binder threads, such as `binder:*`.
- Then check whether the slowest instance names already provide an exact method name.
- If hotspots concentrate on `AudioTrack` creation / writing / playback control, you should also continue to trace back the app-side playback control strategy.

---

## query-03-playback-activity-monitor-lock-contention.sql: PlaybackActivityMonitor Lock Contention

Purpose: determine whether slow audio-service replies are amplified by internal lock contention in `PlaybackActivityMonitor`, rather than the method itself being purely compute-heavy.

```sql
SELECT
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = 'system_server'
  AND s.ts < <window_end_ns>
  AND s.ts + s.dur > <window_start_ns>
  AND (
    s.name GLOB '*PlaybackActivityMonitor*monitor contention*'
    OR s.name GLOB '*monitor contention*PlaybackActivityMonitor*'
    OR s.name GLOB '*AudioPlaybackConfiguration.writeToParcel*'
    OR s.name GLOB '*getActivePlaybackConfigurations*monitor contention*'
    OR s.name GLOB '*playerEvent*monitor contention*'
    OR s.name GLOB '*releasePlayer*monitor contention*'
  )
ORDER BY s.dur DESC, s.ts ASC
LIMIT 100;
```

Interpretation highlights:

- If `monitor contention` is prominent, prioritize judging that internal lock contention in the audio service amplifies the slowness.
- If it also accompanies `writeToParcel()`, prioritize suspecting compounded overhead from the config-query path and serialization.
- Such conclusions are closer to "unreasonable control mode / lifecycle design" rather than "the spatial audio algorithm itself is too heavy".

---

## query-04-worst-doframe-audio-slice.sql: Audio Hotspots Within the Worst doFrame Window

Purpose: confirm whether the worst doFrame directly overlaps the audio-service hotspots in the same window, to avoid mislabeling background noise as the critical path.

```sql
SELECT
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = 'system_server'
  AND s.ts < <worst_doframe_end_ns>
  AND s.ts + s.dur > <worst_doframe_start_ns>
  AND (
    s.name GLOB 'AIDL::java::IAudioService::*'
    OR s.name GLOB '*PlaybackActivityMonitor*'
    OR s.name GLOB '*AudioService*'
    OR s.name GLOB '*AudioTrack*'
  )
ORDER BY s.dur DESC, s.ts ASC
LIMIT 100;
```

Interpretation highlights:

- If audio hotspots are dense within the worst doFrame and have a high share, you can raise confidence that "the audio service is on the critical path".
- If the full window is hot but it is not hot within the worst doFrame, be cautious that audio may be background noise or a secondary factor.

---

## query-05-power-iaudio-audio-linkage.sql: Linkage Between Power and IAudioService

Purpose: count the total volume and time-share of `IAudioService` and `IPowerManager` within the same window, to determine whether Power is the primary root cause or a secondary amplification factor for the audio path.

```sql
WITH target_slices AS (
  SELECT
    CASE
      WHEN s.name GLOB 'AIDL::java::IAudioService::*'
        OR s.name GLOB '*PlaybackActivityMonitor*'
        OR s.name GLOB '*AudioService*'
        OR s.name GLOB '*AudioTrack*'
      THEN 'audio'
      WHEN s.name GLOB 'AIDL::java::IPowerManager::*'
        OR s.name GLOB '*PowerManagerService*'
        OR s.name GLOB '*WakeLock*'
      THEN 'power'
      ELSE 'other'
    END AS service_group,
    s.dur
  FROM slice s
  JOIN thread_track tt ON s.track_id = tt.id
  JOIN thread t ON tt.utid = t.utid
  JOIN process p ON t.upid = p.upid
  WHERE p.name = 'system_server'
    AND s.ts < <window_end_ns>
    AND s.ts + s.dur > <window_start_ns>
)
SELECT
  service_group,
  COUNT(*) AS cnt,
  ROUND(SUM(dur) / 1000000.0, 3) AS total_ms,
  ROUND(MAX(dur) / 1000000.0, 3) AS max_ms
FROM target_slices
WHERE service_group != 'other'
GROUP BY service_group
ORDER BY total_ms DESC, max_ms DESC;
```

Interpretation highlights:

- If `audio` is clearly higher than `power`, write "Audio dominates, Power is secondary amplification".
- Only when overall `power` evidence outweighs `audio` should you consider promoting Power to a primary root-cause candidate.

---

## query-06-application-audio-component-slices.sql: App-Side Slices Related to Spatial Audio Components

Purpose: after server-side hotspots are confirmed, reverse-check in the app process for clues about spatial audio components, resources, and playback control, to provide app-side evidence for `usage-suspected`.

```sql
SELECT
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms,
  s.depth
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND s.ts < <window_end_ns>
  AND s.ts + s.dur > <window_start_ns>
  AND (
    s.name GLOB '*ObjectAudioComponent*'
    OR s.name GLOB '*AmbientAudioComponent*'
    OR s.name GLOB '*ChannelAudioComponent*'
    OR s.name GLOB '*SpatialAudioTrackExtension*'
    OR s.name GLOB '*AudioResource*'
    OR s.name GLOB '*AudioMixerGroup*'
    OR s.name GLOB '*AudioPlayerController*'
    OR s.name GLOB '*AudioTrack*'
  )
ORDER BY s.dur DESC, s.ts ASC
LIMIT 200;
```

Interpretation highlights:

- If you can directly see spatial-audio component names, controller names, or resource-loading names, you can move the conclusion from `service-confirmed` toward `usage-suspected`.
- If nothing is found on the app side, it does not mean there is no issue; it only indicates insufficient trace instrumentation. You still need to combine code and resource checks.

---

## query-07-audio-player-controller-lifecycle-slices.sql: Controller Create/Release Lifecycle

Purpose: confirm whether there is frequent creation/destruction/release of `AudioPlayerController` or player objects, supporting an app-side explanation for `releasePlayer` / `playerEvent` hotspots.

```sql
SELECT
  t.name AS thread_name,
  s.name AS slice_name,
  s.ts,
  s.dur,
  ROUND(s.dur / 1000000.0, 3) AS dur_ms
FROM slice s
JOIN thread_track tt ON s.track_id = tt.id
JOIN thread t ON tt.utid = t.utid
JOIN process p ON t.upid = p.upid
WHERE p.name = '<target.package.name>'
  AND s.ts < <window_end_ns>
  AND s.ts + s.dur > <window_start_ns>
  AND (
    s.name GLOB '*AudioPlayerController*create*'
    OR s.name GLOB '*AudioPlayerController*init*'
    OR s.name GLOB '*AudioPlayerController*release*'
    OR s.name GLOB '*AudioPlayerController*close*'
    OR s.name GLOB '*createPlayer*'
    OR s.name GLOB '*releasePlayer*'
    OR s.name GLOB '*stop*'
    OR s.name GLOB '*pause*'
    OR s.name GLOB '*play*'
  )
ORDER BY s.ts ASC, s.dur DESC
LIMIT 300;
```

Interpretation highlights:

- If there are many create/release/stop/play alternations within a short time, prioritize suspecting lifecycle churn.
- If `releasePlayer` hotspots overlap with batch releases on the app side in the same window, you can explain the server-side hotspots with high confidence.

---

## Recommended Analysis Order

1. Run `query-01` first to confirm the heaviest audio-service method types within the full window.
2. Run `query-02` to lock down the slowest audio hotspot instances and binder threads.
3. Run `query-03` to determine whether `PlaybackActivityMonitor` lock contention amplifies it.
4. Run `query-04` to confirm whether audio hotspots truly fall on the critical path within the worst doFrame.
5. Run `query-05` to determine whether `Power` is the primary cause or secondary linkage amplification.
6. Run `query-06` and `query-07` to supplement evidence on API type, controller lifecycle, and resource management from the app side.

## Output Recommendations

In the final output, it is recommended to additionally include:

- `audio_service_confidence`: `service-confirmed` / `usage-suspected` / `usage-proven`
- `audio_service_hotspots`: matched hotspot methods of `IAudioService` / `PlaybackActivityMonitor` / `AudioTrack`
- `audio_hotspot_pattern`: `playback_config_polling` / `player_event_storm` / `release_player_churn` / `lock_contention`
- `power_linkage`: whether there is amplification linkage via `IPowerManager`
- `app_side_audio_evidence`: summary of app-side evidence on API type, controller count, lifecycle, and resource format
- `next_step`: whether to continue checking code/resources/controller reuse or server-side slowness factors

