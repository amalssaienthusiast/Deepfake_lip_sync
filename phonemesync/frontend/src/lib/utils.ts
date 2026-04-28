// src/lib/utils.ts — pure utility functions

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { PhonemeEntry, WordEntry } from '@/types/api'
import { CONFIDENCE_HIGH, CONFIDENCE_MID } from './constants'

/** Tailwind class merger — standard shadcn/ui pattern */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

/** Format seconds to mm:ss string */
export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

/** Map milliseconds to canvas X pixel coordinate */
export function msToX(ms: number, durationMs: number, canvasWidth: number): number {
  if (durationMs <= 0) return 0
  return (ms / durationMs) * canvasWidth
}

/** Map canvas X pixel to milliseconds (for click-to-seek) */
export function xToMs(x: number, canvasWidth: number, durationMs: number): number {
  if (canvasWidth <= 0) return 0
  return (x / canvasWidth) * durationMs
}

/** Map confidence [0,1] to a hex color string */
export function confidenceToColor(confidence: number): string {
  if (confidence >= CONFIDENCE_HIGH) return '#22C55E'  // green
  if (confidence >= CONFIDENCE_MID)  return '#EAB308'  // yellow
  return '#EF4444'                                      // red
}

/** Flatten WordEntry[] → PhonemeEntry[] in chronological order */
export function flattenPhonemes(timeline: WordEntry[]): PhonemeEntry[] {
  return timeline.flatMap((w) => w.phonemes)
}

/** Find the phoneme active at currentTimeMs (binary-search friendly, linear ok at this scale) */
export function getActivePhoneme(
  flatPhonemes: PhonemeEntry[],
  currentTimeMs: number
): PhonemeEntry | null {
  for (const ph of flatPhonemes) {
    if (ph.start_ms <= currentTimeMs && currentTimeMs <= ph.end_ms) {
      return ph
    }
  }
  return null
}

/** Draw a rounded rectangle on a 2D canvas context */
export function roundRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
): void {
  if (width < 2 * radius) radius = width / 2
  if (height < 2 * radius) radius = height / 2
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.arcTo(x + width, y, x + width, y + height, radius)
  ctx.arcTo(x + width, y + height, x, y + height, radius)
  ctx.arcTo(x, y + height, x, y, radius)
  ctx.arcTo(x, y, x + width, y, radius)
  ctx.closePath()
  ctx.fill()
}

/** Get human-readable quality label from SyncNet avg score */
export function syncQuality(avg: number): { label: string; color: string } {
  if (avg >= 0.72) return { label: 'Good',  color: '#22C55E' }
  if (avg >= 0.55) return { label: 'Fair',  color: '#EAB308' }
  return              { label: 'Low',   color: '#EF4444' }
}
