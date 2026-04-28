'use client'

import { useEffect, useRef } from 'react'

interface HeatmapOverlayProps {
  videoRef: React.RefObject<HTMLVideoElement | null>
  lipLandmarks: Array<{
    frame_idx: number
    lip_bbox: { x: number, y: number, w: number, h: number }
  }>
  syncnetScores: number[]
  fps: number
  videoResolution: [number, number] // [width, height]
}

export function HeatmapOverlay({
  videoRef,
  lipLandmarks,
  syncnetScores,
  fps,
  videoResolution,
}: HeatmapOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video) return

    let rafId: number

    // Keep canvas size synced with video element render size
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        canvas.width = entry.contentRect.width
        canvas.height = entry.contentRect.height
      }
    })
    resizeObserver.observe(video)

    const draw = () => {
      const ctx = canvas.getContext('2d')
      if (!ctx || canvas.width === 0 || canvas.height === 0) {
        rafId = requestAnimationFrame(draw)
        return
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Find current frame based on video time
      const frameIdx = Math.floor(video.currentTime * fps)
      
      const landmark = lipLandmarks.find(l => l.frame_idx === frameIdx)
      const score = syncnetScores[frameIdx]

      if (landmark && score !== undefined && landmark.lip_bbox.w > 0) {
        // Calculate scale factor from original video res to rendered size
        const scaleX = canvas.width / videoResolution[0]
        const scaleY = canvas.height / videoResolution[1]

        const { x, y, w, h } = landmark.lip_bbox
        const scaledX = x * scaleX
        const scaledY = y * scaleY
        const scaledW = w * scaleX
        const scaledH = h * scaleY

        // Determine color based on confidence
        let color = 'rgba(239, 68, 68, 0.4)' // Red (< 0.5)
        let strokeColor = '#EF4444'
        if (score >= 0.75) {
          color = 'rgba(34, 197, 94, 0.4)'   // Green
          strokeColor = '#22C55E'
        } else if (score >= 0.5) {
          color = 'rgba(234, 179, 8, 0.4)'   // Yellow
          strokeColor = '#EAB308'
        }

        // Draw bbox
        ctx.fillStyle = color
        ctx.strokeStyle = strokeColor
        ctx.lineWidth = 2
        ctx.fillRect(scaledX, scaledY, scaledW, scaledH)
        ctx.strokeRect(scaledX, scaledY, scaledW, scaledH)

        // Draw score text
        ctx.fillStyle = '#FFFFFF'
        ctx.font = '10px monospace'
        const pct = Math.round(score * 100)
        
        // Background for text to ensure readability
        const textW = ctx.measureText(`${pct}%`).width
        ctx.fillStyle = 'rgba(0,0,0,0.6)'
        ctx.fillRect(scaledX, scaledY - 14, textW + 4, 14)
        
        ctx.fillStyle = strokeColor
        ctx.fillText(`${pct}%`, scaledX + 2, scaledY - 4)
      }

      rafId = requestAnimationFrame(draw)
    }

    rafId = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(rafId)
      resizeObserver.disconnect()
    }
  }, [videoRef, lipLandmarks, syncnetScores, fps, videoResolution])

  return (
    <canvas
      ref={canvasRef}
      className="absolute top-0 left-0 w-full h-full pointer-events-none"
    />
  )
}
