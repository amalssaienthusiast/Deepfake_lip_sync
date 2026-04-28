'use client'

import { useEffect, useRef, useState } from 'react'
import { usePhonemeData } from '@/hooks/usePhonemeData'
import { PhonemeTooltip } from './PhonemeTooltip'
import { roundRect, confidenceToColor } from '@/lib/utils'
import { TIMELINE_BG, TIMELINE_PLAYHEAD_COLOR } from '@/lib/constants'
import type { PhonemesResponse, PhonemeEntry } from '@/types/api'

interface PhonemeTimelineProps {
  phonemes: PhonemesResponse
  currentTimeMs: number
  onSeek: (timeMs: number) => void
}

export function PhonemeTimeline({ phonemes, currentTimeMs, onSeek }: PhonemeTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { flatPhonemes, timeToX } = usePhonemeData(phonemes, currentTimeMs)
  
  // Tooltip state
  const [hoveredPhoneme, setHoveredPhoneme] = useState<PhonemeEntry | null>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [isHovering, setIsHovering] = useState(false)

  useEffect(() => {
    const canvas = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return

    let rafId: number

    // ResizeObserver ensures canvas always matches container CSS width
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        canvas.width = entry.contentRect.width
        canvas.height = 80 // Fixed height from spec
      }
    })
    resizeObserver.observe(container)

    const draw = () => {
      const ctx = canvas.getContext('2d')
      if (!ctx || canvas.width === 0) {
        rafId = requestAnimationFrame(draw)
        return
      }

      const { width, height } = canvas
      ctx.clearRect(0, 0, width, height)

      // 1. Background
      ctx.fillStyle = TIMELINE_BG
      ctx.fillRect(0, 0, width, height)

      // 2. Word Labels Row (y=0..20)
      ctx.fillStyle = '#475569'
      ctx.font = '10px monospace'
      ctx.textBaseline = 'middle'
      
      for (const word of phonemes.timeline) {
        const x = timeToX(word.word_start_ms, width)
        const w = timeToX(word.word_end_ms, width) - x
        if (w > 10) { // Only draw text if it fits reasonably
          ctx.fillText(word.word, x + 4, 10)
        }
        // Vertical separator
        ctx.strokeStyle = '#1E293B'
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, height)
        ctx.stroke()
      }

      // 3. Phoneme Blocks Row (y=20..60, height=40)
      for (const ph of flatPhonemes) {
        const x = timeToX(ph.start_ms, width)
        const w = Math.max(timeToX(ph.end_ms, width) - x - 1, 1)
        
        // Height driven by confidence
        const blockH = 20 + (ph.syncnet_confidence * 18)
        const blockY = 20 + (40 - blockH) / 2
        
        ctx.fillStyle = ph.viseme_color
        ctx.globalAlpha = 0.7 + (ph.syncnet_confidence * 0.3)
        roundRect(ctx, x, blockY, w, blockH, 2)
        ctx.globalAlpha = 1.0

        // Symbol text
        if (w > 14) {
          ctx.fillStyle = '#FFFFFF'
          ctx.font = '9px monospace'
          ctx.textAlign = 'center'
          ctx.fillText(ph.symbol, x + w / 2, 40) // center of the 40px row
        }
      }

      // 4. Confidence Bar Row (y=60..80, height=20)
      for (const ph of flatPhonemes) {
        const x = timeToX(ph.start_ms, width)
        const w = Math.max(timeToX(ph.end_ms, width) - x - 1, 1)
        const barH = ph.syncnet_confidence * 18
        
        ctx.fillStyle = confidenceToColor(ph.syncnet_confidence)
        ctx.fillRect(x, 78 - barH, w, barH)
      }

      // 5. Active Phoneme Highlight (based on currentTimeMs)
      const activePh = flatPhonemes.find(p => p.start_ms <= currentTimeMs && currentTimeMs <= p.end_ms)
      if (activePh) {
        const x = timeToX(activePh.start_ms, width)
        const w = Math.max(timeToX(activePh.end_ms, width) - x - 1, 1)
        const blockH = 20 + (activePh.syncnet_confidence * 18)
        const blockY = 20 + (40 - blockH) / 2

        ctx.strokeStyle = '#FFFFFF'
        ctx.lineWidth = 1.5
        roundRect(ctx, x, blockY, w, blockH, 2)
        ctx.stroke()
      }

      // 6. Playhead (always on top)
      const playheadX = timeToX(currentTimeMs, width)
      ctx.strokeStyle = TIMELINE_PLAYHEAD_COLOR
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.moveTo(playheadX, 0)
      ctx.lineTo(playheadX, height)
      ctx.stroke()
      
      // Playhead triangle
      ctx.fillStyle = TIMELINE_PLAYHEAD_COLOR
      ctx.beginPath()
      ctx.moveTo(playheadX - 4, 0)
      ctx.lineTo(playheadX + 4, 0)
      ctx.lineTo(playheadX, 6)
      ctx.fill()

      rafId = requestAnimationFrame(draw)
    }

    rafId = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(rafId)
      resizeObserver.disconnect()
    }
  }, [phonemes, flatPhonemes, timeToX, currentTimeMs])

  // Click to seek handler
  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const ratio = Math.max(0, Math.min(1, x / canvas.clientWidth))
    onSeek(ratio * phonemes.audio_duration_ms)
  }

  // Hover handlers for Tooltip
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    setIsHovering(true)
    setMousePos({ x: e.clientX, y: e.clientY })
    
    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const hoverMs = (x / canvas.clientWidth) * phonemes.audio_duration_ms
    
    const ph = flatPhonemes.find(p => hoverMs >= p.start_ms && hoverMs <= p.end_ms)
    setHoveredPhoneme(ph || null)
  }

  const handleMouseLeave = () => {
    setIsHovering(false)
    setHoveredPhoneme(null)
  }

  return (
    <div className="relative w-full" ref={containerRef}>
      <canvas
        ref={canvasRef}
        className="timeline-canvas-wrap bg-[#0F172A] border border-slate-700/50 shadow-inner"
        style={{ height: 80 }}
        onClick={handleClick}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      />
      <PhonemeTooltip 
        phoneme={hoveredPhoneme} 
        x={mousePos.x} 
        y={mousePos.y} 
        visible={isHovering && hoveredPhoneme !== null} 
      />
    </div>
  )
}
