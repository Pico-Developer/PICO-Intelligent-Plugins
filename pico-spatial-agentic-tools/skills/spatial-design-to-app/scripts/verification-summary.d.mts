/*
 * Copyright 2026 PICO Immersive Pte. Ltd.
 * SPDX-License-Identifier: Apache-2.0
 */

export const REQUIRED_CHECKS: readonly string[];
export type ValidationInputs = {
  target: string;
  sourceDigest: string;
  designDigest: string | null;
};
export function captureValidationInputs(
  target: string,
  signal?: AbortSignal,
  designText?: string | Uint8Array | null,
): Promise<ValidationInputs>;
export function beginVerification(
  target: string,
): Promise<{ invocationId: string; inputs: ValidationInputs }>;
export function completeVerification(target: string): Promise<Record<string, unknown>>;
export function verifyCurrentVerification(
  summary: unknown,
  target: string,
  signal?: AbortSignal,
  designText?: string | Uint8Array | null,
): Promise<void>;
