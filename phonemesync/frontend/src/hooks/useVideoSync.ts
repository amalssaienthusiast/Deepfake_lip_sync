'use client'

import { useEffect, useRef } from 'react'
import { useStore } from '@/lib/store'

interface UseVideoSyncReturn {
  currentTimeMs: number
  isPlaying: boolean
  duration: number
}

export function useVideoSync(
  videoRef: React.RefObject<HTMLVideoElement | null>
): UseVideoSyncReturn {
  const setCurrentVideoTime = useStore((s) => s.setCurrentVideoTime)
  const currentVideoTime    = useStore((s) => s.currentVideoTime)
  const rafRef              = useRef<number | null>(null)
  const isPlayingRef        = useRef(false)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const onTimeUpdate = () => setCurrentVideoTime(video.currentTime)
    const onPlay       = () => { isPlayingRef.current = true }
    const onPause      = () => { isPlayingRef.current = false }
    const onSeeked     = () => setCurrentVideoTime(video.currentTime)

    video.addEventListener('timeupdate', onTimeUpdate)
    video.addEventListener('play',       onPlay)
    video.addEventListener('pause',      onPause)
    video.addEventListener('seeked',     onSeeked)

    // rAF loop for smooth canvas updates
    const loop = () => {
      if (video && !video.paused) {
        setCurrentVideoTime(video.currentTime)
      }
      rafRef.current = requestAnimationFrame(loop)
    }
    rafRef.current = requestAnimationFrame(loop)

    return () => {
      video.removeEventListener('timeupdate', onTimeUpdate)
      video.removeEventListener('play',       onPlay)
      video.removeEventListener('pause',      onPause)
      video.removeEventListener('seeked',     onSeeked)
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [videoRef, setCurrentVideoTime])

  return {
    currentTimeMs: currentVideoTime * 1000,
    isPlaying:     isPlayingRef.current,
    duration:      videoRef.current?.duration ?? 0,
  }
}
