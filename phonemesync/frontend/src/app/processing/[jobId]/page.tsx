'use client'

import { useJobPolling } from '@/hooks/useJobPolling'
import { StageTracker } from '@/components/processing/StageTracker'
import { ProgressRing } from '@/components/processing/ProgressRing'
import { AlertCircle, RefreshCw } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface ProcessingPageProps {
  params: { jobId: string }
}

export default function ProcessingPage({ params }: ProcessingPageProps) {
  const router = useRouter()
  const { progress, stage, isError } = useJobPolling(params.jobId)

  if (isError) {
    return (
      <main className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-slate-900 border border-red-500/30 rounded-xl p-6 text-center shadow-2xl shadow-red-900/10">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-slate-200 mb-2">Processing Failed</h2>
          <p className="text-sm text-slate-400 mb-6">
            There was an error processing your files. Please ensure they contain a visible face.
          </p>
          <button
            onClick={() => router.push('/upload')}
            className="flex items-center justify-center gap-2 w-full py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[100px] processing-bg-pulse pointer-events-none" />

      <div className="relative z-10 w-full max-w-md fade-in">
        <ProgressRing progress={progress} />
        
        <div className="bg-[#1E293B] rounded-2xl border border-slate-700/50 p-6 shadow-2xl">
          <StageTracker currentStage={stage} progress={progress} />
          
          <div className="mt-8 text-center border-t border-slate-700/50 pt-4">
            <p className="text-xs text-slate-500 font-mono">
              JOB ID: {params.jobId.split('-')[0]}...
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
