'use client'

import { useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { getJobStatus, getJobResult, getPhonemes } from '@/lib/api'
import { useStore } from '@/lib/store'
import { POLL_INTERVAL_MS } from '@/lib/constants'

interface UseJobPollingReturn {
  status: string | null
  progress: number
  stage: string | null
  isComplete: boolean
  isError: boolean
}

export function useJobPolling(jobId: string): UseJobPollingReturn {
  const router   = useRouter()
  const setJobStatus = useStore((s) => s.setJobStatus)
  const setResult    = useStore((s) => s.setResult)
  const setPhonemes  = useStore((s) => s.setPhonemes)
  const jobStatus    = useStore((s) => s.jobStatus)
  const intervalRef  = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!jobId) return

    const poll = async () => {
      try {
        const status = await getJobStatus(jobId)
        setJobStatus(status)

        if (status.status === 'done') {
          clearInterval(intervalRef.current!)
          // Fetch result + phonemes in parallel
          const [result, phonemes] = await Promise.all([
            getJobResult(jobId),
            getPhonemes(jobId),
          ])
          setResult(result)
          setPhonemes(phonemes)
          // Navigate to results after brief delay for animation
          setTimeout(() => router.push(`/results/${jobId}`), 800)
        }

        if (status.status === 'failed') {
          clearInterval(intervalRef.current!)
          toast.error(`Processing failed: ${status.error ?? 'Unknown error'}`)
        }
      } catch (err) {
        console.error('Polling error:', err)
        // Don't stop polling on transient network errors
      }
    }

    // Poll immediately, then every POLL_INTERVAL_MS
    poll()
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [jobId]) // eslint-disable-line react-hooks/exhaustive-deps

  return {
    status:     jobStatus?.status ?? null,
    progress:   jobStatus?.progress ?? 0,
    stage:      jobStatus?.stage ?? null,
    isComplete: jobStatus?.status === 'done',
    isError:    jobStatus?.status === 'failed',
  }
}
