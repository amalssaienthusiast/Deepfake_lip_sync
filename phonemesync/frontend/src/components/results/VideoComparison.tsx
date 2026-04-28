'use client'

import { useRef, useEffect } from 'react'
import { resolveMediaUrl } from '@/lib/api'
import { HeatmapOverlay } from './HeatmapOverlay'
import type { ResultResponse } from '@/types/api'

interface VideoComparisonProps {
  result: ResultResponse
  onTimeUpdate: (time: number) => void
}

export function VideoComparison({ result, onTimeUpdate }: VideoComparisonProps) {
  const originalRef = useRef<HTMLVideoElement>(null)
  const syncedRef = useRef<HTMLVideoElement>(null)

  // Sync playback between the two videos.
  // The 'synced' video is the master controller.
  useEffect(() => {
    const master = syncedRef.current
    const slave = originalRef.current
    if (!master || !slave) return

    const handlePlay = () => slave.play().catch(() => {})
    const handlePause = () => slave.pause()
    const handleSeek = () => { slave.currentTime = master.currentTime }
    const handleTimeUpdate = () => {
      onTimeUpdate(master.currentTime)
      // Hard resync if they drift too far
      if (Math.abs(master.currentTime - slave.currentTime) > 0.1) {
        slave.currentTime = master.currentTime
      }
    }

    master.addEventListener('play', handlePlay)
    master.addEventListener('pause', handlePause)
    master.addEventListener('seeked', handleSeek)
    master.addEventListener('timeupdate', handleTimeUpdate)

    return () => {
      master.removeEventListener('play', handlePlay)
      master.removeEventListener('pause', handlePause)
      master.removeEventListener('seeked', handleSeek)
      master.removeEventListener('timeupdate', handleTimeUpdate)
    }
  }, [onTimeUpdate])

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      
      {/* Original Video */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-slate-300">Original Target</span>
        </div>
        <div className="relative rounded-xl overflow-hidden bg-black border border-slate-700/50 aspect-video">
          <video
            ref={originalRef}
            src={resolveMediaUrl(result.original_video_url)}
            className="w-full h-full object-contain"
            muted
            playsInline
            crossOrigin="anonymous"
          />
        </div>
      </div>

      {/* Synced Video with Overlay */}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-indigo-400">PhonemeSync Output</span>
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
          </span>
        </div>
        <div className="video-wrap rounded-xl overflow-hidden bg-black border border-indigo-500/30 shadow-[0_0_20px_rgba(99,102,241,0.1)] aspect-video">
          <video
            ref={syncedRef}
            src={resolveMediaUrl(result.video_url)}
            className="w-full h-full object-contain"
            controls
            playsInline
            crossOrigin="anonymous"
          />
          <HeatmapOverlay
            videoRef={syncedRef}
            lipLandmarks={result.lip_landmarks}
            syncnetScores={result.syncnet_scores}
            fps={result.fps}
            videoResolution={result.resolution}
          />
        </div>
      </div>

    </div>
  )
}
