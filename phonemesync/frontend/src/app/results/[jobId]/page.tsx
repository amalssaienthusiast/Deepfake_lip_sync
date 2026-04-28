'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useStore } from '@/lib/store'
import { getJobResult, getPhonemes } from '@/lib/api'
import { MetricsBar } from '@/components/results/MetricsBar'
import { VideoComparison } from '@/components/results/VideoComparison'
import { DownloadButton } from '@/components/results/DownloadButton'
import { PhonemeTimeline } from '@/components/phoneme/PhonemeTimeline'
import { VisemeLegend } from '@/components/phoneme/VisemeLegend'
import { Loader2 } from 'lucide-react'

interface ResultsPageProps {
  params: { jobId: string }
}

export default function ResultsPage({ params }: ResultsPageProps) {
  const router = useRouter()
  const { jobId } = params
  
  const result = useStore((s) => s.result)
  const phonemes = useStore((s) => s.phonemes)
  const setResult = useStore((s) => s.setResult)
  const setPhonemes = useStore((s) => s.setPhonemes)
  
  const currentVideoTime = useStore((s) => s.currentVideoTime)
  const setCurrentVideoTime = useStore((s) => s.setCurrentVideoTime)

  const [loading, setLoading] = useState(!result || !phonemes)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (result && phonemes && result.job_id === jobId) {
      setLoading(false)
      return
    }

    const fetchData = async () => {
      try {
        const [r, p] = await Promise.all([
          getJobResult(jobId),
          getPhonemes(jobId),
        ])
        setResult(r)
        setPhonemes(p)
      } catch (err: unknown) {
        const errorResp = err as { response?: { status?: number, data?: { message?: string } } }
        if (errorResp.response?.status === 409) {
          router.push(`/processing/${jobId}`)
        } else {
          setError(errorResp.response?.data?.message || 'Failed to load results')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [jobId, result, phonemes, router, setResult, setPhonemes])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    )
  }

  if (error || !result || !phonemes) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-400">
        <p>{error || 'Results not found'}</p>
      </div>
    )
  }

  return (
    <main className="min-h-screen p-4 md:p-8 max-w-[1400px] mx-auto space-y-8 fade-in pb-24">
      
      {/* Header */}
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">PhonemeSync Results</h1>
          <p className="text-sm text-slate-400 font-mono mt-1">ID: {jobId}</p>
        </div>
        <div className="flex gap-3">
          <DownloadButton videoUrl={result.video_url} jobId={jobId} />
        </div>
      </header>

      {/* Metrics */}
      <section>
        <MetricsBar result={result} />
      </section>

      {/* Video Comparison */}
      <section className="bg-[#1E293B] rounded-2xl border border-slate-700/50 p-4 md:p-6 shadow-2xl">
        <VideoComparison 
          result={result} 
          onTimeUpdate={setCurrentVideoTime} 
        />
      </section>

      {/* Timeline Section */}
      <section className="bg-[#1E293B] rounded-2xl border border-slate-700/50 p-4 md:p-6 shadow-2xl">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-4 gap-2">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">Phoneme Alignment Timeline</h2>
            <p className="text-sm text-slate-400 mt-1">
              Click to seek · Hover for details · Block height indicates SyncNet confidence
            </p>
          </div>
          <div className="text-xs font-mono text-slate-500 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
            T={currentVideoTime.toFixed(2)}s
          </div>
        </div>
        
        <PhonemeTimeline 
          phonemes={phonemes}
          currentTimeMs={currentVideoTime * 1000}
          onSeek={(ms) => {
            // Finding the video element is slightly hacky but works for the demo
            // Better approach is to put the ref in the store or use an event dispatcher
            const videos = document.querySelectorAll('video')
            videos.forEach(v => { v.currentTime = ms / 1000 })
          }}
        />
        
        <VisemeLegend />
      </section>

    </main>
  )
}
