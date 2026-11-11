import { Box3, REVISION } from 'three'

const PRODUCER_ID = 'three-runtime-aabb-probe'
const PRODUCER_VERSION = 1
const LOG_PREFIX = 'SPATIAL_FIT_MEASUREMENT '

function canonicalJson(value) {
  if (Array.isArray(value)) {
    return `[${value.map(canonicalJson).join(',')}]`
  }
  if (value && typeof value === 'object') {
    const entries = Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`)
    return `{${entries.join(',')}}`
  }
  return JSON.stringify(value)
}

function fnv1a32(value) {
  let hash = 0x811c9dc5
  for (const byte of new TextEncoder().encode(value)) {
    hash ^= byte
    hash = Math.imul(hash, 0x01000193)
  }
  return `fnv1a32:${(hash >>> 0).toString(16).padStart(8, '0')}`
}

function vector(value) {
  return [value.x, value.y, value.z]
}

function boxValue(minimum, maximum, space) {
  return {
    space,
    min: minimum,
    max: maximum,
    size: maximum.map((value, axis) => value - minimum[axis]),
  }
}

function corners(minimum, maximum) {
  const result = []
  for (const x of [minimum[0], maximum[0]]) {
    for (const y of [minimum[1], maximum[1]]) {
      for (const z of [minimum[2], maximum[2]]) {
        result.push([x, y, z])
      }
    }
  }
  return result
}

export function measureThreeSceneAabb({
  root,
  stateId,
  context = {},
  emit = (measurement) => {
    console.info(`${LOG_PREFIX}${JSON.stringify(measurement)}`)
  },
}) {
  if (!root?.isObject3D) {
    throw new TypeError('root must be a THREE.Object3D')
  }
  if (typeof stateId !== 'string' || stateId.trim() === '') {
    throw new TypeError('stateId must be a non-empty string')
  }

  root.updateWorldMatrix(true, true)
  const bounds = new Box3().setFromObject(root, true)
  if (bounds.isEmpty()) {
    throw new Error(`Three.js state "${stateId}" has an empty world-space AABB`)
  }

  let objectCount = 0
  root.traverse(() => {
    objectCount += 1
  })

  const minimum = vector(bounds.min)
  const maximum = vector(bounds.max)
  const probeContext = {
    ...context,
    object_count: objectCount,
    root_uuid: root.uuid,
    state_id: stateId,
    three_revision: String(REVISION),
  }
  const rawBox = boxValue(minimum, maximum, 'three-world-source-units')
  const measurement = {
    schema_version: 1,
    measurement_kind: 'source-scene-aabb',
    producer: {
      id: PRODUCER_ID,
      version: PRODUCER_VERSION,
    },
    captured_at_utc: new Date().toISOString(),
    context: probeContext,
    context_fingerprint: fnv1a32(canonicalJson(probeContext)),
    raw_box: rawBox,
    raw_corners: corners(minimum, maximum),
    aabb_source: {
      min: rawBox.min,
      max: rawBox.max,
      size: rawBox.size,
    },
  }

  emit(measurement)
  return measurement
}
