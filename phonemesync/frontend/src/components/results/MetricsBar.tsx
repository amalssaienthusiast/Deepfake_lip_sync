'use client'

import { formatDuration, syncQuality } from '@/lib/utils'
import type { ResultResponse } from '@/types/api'

interface MetricsBarProps {
  result: ResultResponse
}

export function MetricsBar({ result }: MetricsBarProps) {
  const quality = syncQuality(result.syncnet_avg)

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
      {/* SyncNet Score */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 flex flex-col justify-center relative overflow-hidden group">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Sync Confidence</span>
          <span 
            className="text-[10px] px-2 py-0.5 rounded-full font-medium"
            style={{ backgroundColor: `${quality.color}20`, color: quality.color }}
          >
            {quality.label}
          </span>
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-mono font-medium text-slate-100">
            {result.syncnet_avg.toFixed(2)}
          </span>
          <span className="text-xs text-slate-500 font-mono">
            ±{result.syncnet_std.toFixed(2)}
          </span>
        </div>
        {/* Tooltip hint visible on hover */}
        <div className="absolute inset-0 bg-slate-800 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 px-4 text-center">
          <p className="text-[10px] text-slate-300 leading-tight">
            Baseline: 6.37<br/>LatentSync SOTA: 7.62
          </p>
        </div>
      </div>

      {/* Duration */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 flex flex-col justify-center">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Duration</span>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-mono font-medium text-slate-100">
            {formatDuration(result.duration_seconds)}
          </span>
          <span className="text-xs text-slate-500">
            {result.fps.toFixed(0)} fps
          </span>
        </div>
      </div>

      {/* Processing Time */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 flex flex-col justify-center">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Process Time</span>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-mono font-medium text-slate-100">
            {result.processing_time_seconds.toFixed(1)}
          </span>
          <span className="text-xs text-slate-500">seconds</span>
        </div>
      </div>

      {/* Model Used */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 flex flex-col justify-center">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Synthesis Model</span>
        <div className="flex items-center mt-1">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-sm font-mono font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            Wav2Lip GAN
          </span>
        </div>
      </div>
    </div>
  )
}
