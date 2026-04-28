// src/types/api.ts — TypeScript types mirroring backend schemas exactly

export type JobStatus = 'queued' | 'processing' | 'done' | 'failed'
export type ProcessingStage = 'wav2lip' | 'whisper' | 'syncnet' | 'mediapipe' | 'done'

export type VisemeClass =
  | 'silence'
  | 'bilabial'
  | 'labiodental'
  | 'dental'
  | 'alveolar'
  | 'postalveolar'
  | 'velar'
  | 'glottal'
  | 'front_vowel'
  | 'mid_vowel'
  | 'back_vowel'
  | 'diphthong'

export interface JobSubmitResponse {
  job_id: string
  status: JobStatus
  estimated_seconds: number
  created_at: string
}

export interface JobStatusResponse {
  job_id: string
  status: JobStatus
  progress: number
  stage: ProcessingStage | null
  error: string | null
  created_at: string
  updated_at: string
}

export interface LipBbox {
  x: number
  y: number
  w: number
  h: number
}

export interface LipLandmarkFrame {
  frame_idx: number
  timestamp_ms: number
  lip_outer: [number, number][]
  lip_inner: [number, number][]
  lip_bbox: LipBbox
}

export interface ResultResponse {
  job_id: string
  video_url: string
  original_video_url: string
  duration_seconds: number
  fps: number
  resolution: [number, number]
  syncnet_scores: number[]
  syncnet_avg: number
  syncnet_std: number
  lip_landmarks: LipLandmarkFrame[]
  processing_time_seconds: number
  model_used: string
}

export interface PhonemeEntry {
  symbol: string
  viseme_class: VisemeClass
  viseme_color: string
  start_ms: number
  end_ms: number
  frame_start: number
  frame_end: number
  syncnet_confidence: number
}

export interface WordEntry {
  word: string
  word_start_ms: number
  word_end_ms: number
  phonemes: PhonemeEntry[]
}

export interface VisemeSummaryEntry {
  count: number
  avg_confidence: number
}

export interface PhonemesResponse {
  job_id: string
  audio_duration_ms: number
  total_phonemes: number
  timeline: WordEntry[]
  viseme_summary: Partial<Record<VisemeClass, VisemeSummaryEntry>>
}

export interface ErrorResponse {
  error: string
  message: string
  job_id: string | null
}
