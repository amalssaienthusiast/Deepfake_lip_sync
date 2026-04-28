// src/lib/store.ts — Zustand global state for the PhonemeSync app

import { create } from 'zustand'
import type { JobStatusResponse, ResultResponse, PhonemesResponse } from '@/types/api'

interface PhoneSyncStore {
  // ── Upload ──────────────────────────────────────────────────────────────
  faceFile: File | null
  audioFile: File | null
  setFaceFile: (f: File | null) => void
  setAudioFile: (f: File | null) => void

  // ── Job lifecycle ────────────────────────────────────────────────────────
  jobId: string | null
  jobStatus: JobStatusResponse | null
  setJobId: (id: string) => void
  setJobStatus: (s: JobStatusResponse) => void

  // ── Results ──────────────────────────────────────────────────────────────
  result: ResultResponse | null
  phonemes: PhonemesResponse | null
  setResult: (r: ResultResponse) => void
  setPhonemes: (p: PhonemesResponse) => void

  // ── Playback sync ────────────────────────────────────────────────────────
  currentVideoTime: number   // seconds — shared between video element + canvas
  setCurrentVideoTime: (t: number) => void

  // ── Reset ────────────────────────────────────────────────────────────────
  reset: () => void
}

const initialState = {
  faceFile:         null,
  audioFile:        null,
  jobId:            null,
  jobStatus:        null,
  result:           null,
  phonemes:         null,
  currentVideoTime: 0,
}

export const useStore = create<PhoneSyncStore>((set) => ({
  ...initialState,

  setFaceFile:          (f) => set({ faceFile: f }),
  setAudioFile:         (f) => set({ audioFile: f }),
  setJobId:             (id) => set({ jobId: id }),
  setJobStatus:         (s) => set({ jobStatus: s }),
  setResult:            (r) => set({ result: r }),
  setPhonemes:          (p) => set({ phonemes: p }),
  setCurrentVideoTime:  (t) => set({ currentVideoTime: t }),

  reset: () => set(initialState),
}))
