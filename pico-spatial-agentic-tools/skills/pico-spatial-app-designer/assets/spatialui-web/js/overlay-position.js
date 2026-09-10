/*
 * Pure positioning helpers shared by Augment and SpatialPopup.
 * Keeping geometry independent from DOM APIs makes it easy to verify.
 */

const NAMED_POINTS = {
  "top-left": { x: 0, y: 0, z: 1 },
  "top-left-front": { x: 0, y: 0, z: 1 },
  top: { x: 0.5, y: 0, z: 1 },
  "top-center": { x: 0.5, y: 0, z: 1 },
  "top-front": { x: 0.5, y: 0, z: 1 },
  "top-center-front": { x: 0.5, y: 0, z: 1 },
  "top-right": { x: 1, y: 0, z: 1 },
  "top-right-front": { x: 1, y: 0, z: 1 },
  left: { x: 0, y: 0.5, z: 1 },
  "center-left": { x: 0, y: 0.5, z: 1 },
  "center-left-front": { x: 0, y: 0.5, z: 1 },
  center: { x: 0.5, y: 0.5, z: 1 },
  front: { x: 0.5, y: 0.5, z: 1 },
  "center-front": { x: 0.5, y: 0.5, z: 1 },
  right: { x: 1, y: 0.5, z: 1 },
  "center-right": { x: 1, y: 0.5, z: 1 },
  "center-right-front": { x: 1, y: 0.5, z: 1 },
  "bottom-left": { x: 0, y: 1, z: 1 },
  "bottom-left-front": { x: 0, y: 1, z: 1 },
  bottom: { x: 0.5, y: 1, z: 1 },
  "bottom-center": { x: 0.5, y: 1, z: 1 },
  "bottom-front": { x: 0.5, y: 1, z: 1 },
  "bottom-center-front": { x: 0.5, y: 1, z: 1 },
  "bottom-right": { x: 1, y: 1, z: 1 },
  "bottom-right-front": { x: 1, y: 1, z: 1 },
};

function finite(value, fallback = 0) {
  const number = Number(value);
  return Number.isFinite(number) ? number : fallback;
}

/** Parse a named point or an "x,y,z" normalized tuple. */
export function parseNormalizedPoint(value, fallback = "center") {
  const source = String(value || fallback).trim();
  const tuple = source.split(",").map((part) => Number(part.trim()));
  if (tuple.length >= 2 && tuple.every(Number.isFinite)) {
    return { x: tuple[0], y: tuple[1], z: tuple[2] ?? 1 };
  }

  const normalized = source
    .trim()
    .replace(/([a-z0-9])([A-Z])/g, "$1-$2")
    .replace(/[_.\s]+/g, "-")
    .toLowerCase();
  if (NAMED_POINTS[normalized]) return { ...NAMED_POINTS[normalized] };
  return { ...(NAMED_POINTS[fallback] || NAMED_POINTS.center) };
}

/** Align one normalized content point to a normalized point on the host. */
export function computeAugmentPosition(
  anchorRect,
  contentSize,
  anchorPoint,
  contentAlignment,
  offset = {},
) {
  return {
    x: anchorRect.left + anchorRect.width * anchorPoint.x
      - contentSize.width * contentAlignment.x + finite(offset.x),
    y: anchorRect.top + anchorRect.height * anchorPoint.y
      - contentSize.height * contentAlignment.y + finite(offset.y),
    z: finite(offset.z),
  };
}

function horizontalPosition(anchorRect, width, placement, direction) {
  const rtl = direction === "rtl";
  switch (placement) {
    case "to-start-of": return rtl ? anchorRect.right : anchorRect.left - width;
    case "center": return anchorRect.left + (anchorRect.width - width) / 2;
    case "align-end": return rtl ? anchorRect.left : anchorRect.right - width;
    case "to-end-of": return rtl ? anchorRect.left - width : anchorRect.right;
    case "align-start":
    default: return rtl ? anchorRect.right - width : anchorRect.left;
  }
}

function verticalPosition(anchorRect, height, placement) {
  switch (placement) {
    case "align-top": return anchorRect.top;
    case "center": return anchorRect.top + (anchorRect.height - height) / 2;
    case "align-bottom": return anchorRect.bottom - height;
    case "below": return anchorRect.bottom;
    case "above":
    default: return anchorRect.top - height;
  }
}

/** Position a popup with the SDK HorizontalPlacement/VerticalPlacement model. */
export function computePopupPosition(
  anchorRect,
  contentSize,
  horizontalPlacement = "align-start",
  verticalPlacement = "above",
  offset = {},
  direction = "ltr",
) {
  return {
    x: horizontalPosition(anchorRect, contentSize.width, horizontalPlacement, direction)
      + finite(offset.x),
    y: verticalPosition(anchorRect, contentSize.height, verticalPlacement) + finite(offset.y),
    z: finite(offset.z),
  };
}

/** Clamp a popup to a viewport when clipping-enabled is explicitly requested. */
export function clampPosition(position, contentSize, viewport, padding = 0) {
  const maxX = Math.max(padding, viewport.width - contentSize.width - padding);
  const maxY = Math.max(padding, viewport.height - contentSize.height - padding);
  return {
    ...position,
    x: Math.min(Math.max(position.x, padding), maxX),
    y: Math.min(Math.max(position.y, padding), maxY),
  };
}
