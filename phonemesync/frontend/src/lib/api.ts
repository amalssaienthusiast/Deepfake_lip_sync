// src/lib/api.ts — all backend calls, typed and centralised
// NEVER import in server components — client only

import axios from 'axios'
import type {
  JobSubmitResponse,
  JobStatusResponse,
  ResultResponse,
  PhonemesResponse,
} from '@/types/api'

const client = axios.create({
  baseURL: (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000') + '/api/v1',
  timeout: 30_000,
})

/** POST /process — submit lip-sync job */
export async function submitJob(
  faceFile: File,
  audioFile: File
): Promise<JobSubmitResponse> {
  const form = new FormData()
  form.append('video_file', faceFile)
  form.append('audio_file', audioFile)
  const { data } = await client.post<JobSubmitResponse>('/process', form)
  return data
}

/** GET /status/:jobId — poll job progress */
export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const { data } = await client.get<JobStatusResponse>(`/status/${jobId}`)
  return data
}

/** GET /result/:jobId — fetch synthesis result */
export async function getJobResult(jobId: string): Promise<ResultResponse> {
  const { data } = await client.get<ResultResponse>(`/result/${jobId}`)
  return data
}

/** GET /phonemes/:jobId — fetch phoneme timeline (the innovation endpoint) */
export async function getPhonemes(jobId: string): Promise<PhonemesResponse> {
  const { data } = await client.get<PhonemesResponse>(`/phonemes/${jobId}`)
  return data
}

/** Resolve a relative media path to an absolute URL using the API base */
export function resolveMediaUrl(path: string): string {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const base = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
  return base + path
}
