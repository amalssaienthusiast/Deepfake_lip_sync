'use client'

import { VISEME_COLORS, VISEME_LABELS } from '@/lib/constants'
import type { VisemeClass } from '@/types/api'

export function VisemeLegend() {
  const entries = Object.entries(VISEME_COLORS) as [VisemeClass, string][]

  return (
    <div className="flex flex-wrap gap-x-4 gap-y-2 mt-4 text-xs">
      {entries.map(([key, color]) => (
        <div key={key} className="flex items-center gap-1.5">
          <div 
            className="w-3 h-3 rounded-sm border border-black/20" 
            style={{ backgroundColor: color }} 
          />
          <span className="text-slate-400 font-mono">
            {VISEME_LABELS[key] || key}
          </span>
        </div>
      ))}
    </div>
  )
}
