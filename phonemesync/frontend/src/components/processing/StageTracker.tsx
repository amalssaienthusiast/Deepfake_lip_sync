'use client'

import { cn } from '@/lib/utils'
import { PROCESSING_STAGES } from '@/lib/constants'
import { Check, Loader2 } from 'lucide-react'

interface StageTrackerProps {
  currentStage: string | null
  progress: number
}

export function StageTracker({ currentStage, progress }: StageTrackerProps) {
  // Find index of current stage; if done, all are complete.
  let currentIndex = PROCESSING_STAGES.findIndex(s => s.key === currentStage)
  if (currentStage === 'done') currentIndex = PROCESSING_STAGES.length
  if (currentIndex === -1) currentIndex = 0

  return (
    <div className="w-full max-w-md mx-auto space-y-6">
      {/* ── Stage Pills ────────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-2">
        {PROCESSING_STAGES.map((stage, idx) => {
          const isComplete = idx < currentIndex
          const isActive   = idx === currentIndex && currentStage !== 'done'
          const isPending  = idx > currentIndex

          return (
            <div
              key={stage.key}
              className={cn(
                'flex items-center gap-4 p-3 rounded-lg border transition-all duration-300',
                isComplete && 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
                isActive   && 'bg-indigo-500/10 border-indigo-500/50 text-indigo-400 stage-active glow-active',
                isPending  && 'bg-slate-800/30 border-slate-700/50 text-slate-500'
              )}
            >
              <div className="flex-shrink-0 w-6 h-6 flex items-center justify-center">
                {isComplete ? (
                  <Check className="w-4 h-4 text-emerald-400" />
                ) : isActive ? (
                  <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                ) : (
                  <span className="text-xs font-mono">{idx + 1}</span>
                )}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">{stage.label}</p>
                <p className={cn(
                  'text-xs mt-0.5',
                  isActive ? 'text-indigo-400/70' : isComplete ? 'text-emerald-400/70' : 'text-slate-600'
                )}>
                  {stage.description}
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {/* ── Progress Bar ────────────────────────────────────────────────────── */}
      <div className="space-y-2">
        <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="flex justify-between text-xs font-mono text-slate-500">
          <span>{progress}%</span>
          <span>{currentStage === 'done' ? 'Complete' : 'Processing...'}</span>
        </div>
      </div>
    </div>
  )
}
