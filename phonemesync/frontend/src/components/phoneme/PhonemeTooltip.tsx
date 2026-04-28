'use client'

import type { PhonemeEntry } from '@/types/api'
import { VISEME_LABELS } from '@/lib/constants'

interface PhonemeTooltipProps {
  phoneme: PhonemeEntry | null
  x: number
  y: number
  visible: boolean
}

export function PhonemeTooltip({ phoneme, x, y, visible }: PhonemeTooltipProps) {
  if (!visible || !phoneme) return null

  // Offset tooltip slightly above and right of cursor
  const style = {
    left: `${x + 15}px`,
    top: `${y - 100}px`,
  }

  const confidencePct = Math.round(phoneme.syncnet_confidence * 100)

  return (
    <div
      className="fixed z-50 pointer-events-none bg-slate-900 border border-slate-700 shadow-xl rounded-lg p-3 w-48 transition-opacity duration-150"
      style={style}
    >
      <div className="flex items-center justify-between mb-2 pb-2 border-b border-slate-800">
        <span className="text-lg font-bold text-slate-100 font-mono">/{phoneme.symbol}/</span>
        <div
          className="w-4 h-4 rounded-full border border-black/20 shadow-sm"
          style={{ backgroundColor: phoneme.viseme_color }}
        />
      </div>
      
      <div className="space-y-1.5 text-xs">
        <div className="flex justify-between">
          <span className="text-slate-500">Viseme</span>
          <span className="font-medium text-slate-300">
            {VISEME_LABELS[phoneme.viseme_class] || phoneme.viseme_class}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-slate-500">Confidence</span>
          <span className={`font-mono font-medium ${
            confidencePct >= 75 ? 'text-emerald-400' : 
            confidencePct >= 50 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {confidencePct}%
          </span>
        </div>
        
        <div className="flex justify-between">
          <span className="text-slate-500">Time</span>
          <span className="font-mono text-slate-400">
            {phoneme.start_ms} - {phoneme.end_ms}ms
          </span>
        </div>
      </div>
    </div>
  )
}
