'use client'

import { useMemo } from 'react'
import { flattenPhonemes, getActivePhoneme, msToX } from '@/lib/utils'
import type { PhonemeEntry, PhonemesResponse, WordEntry } from '@/types/api'

interface UsePhonemeDataReturn {
  activePhoneme:  PhonemeEntry | null
  activeWord:     WordEntry    | null
  flatPhonemes:   PhonemeEntry[]
  timeToX:        (ms: number, canvasWidth: number) => number
}

export function usePhonemeData(
  phonemes: PhonemesResponse | null,
  currentTimeMs: number
): UsePhonemeDataReturn {
  const flatPhonemes = useMemo(
    () => (phonemes ? flattenPhonemes(phonemes.timeline) : []),
    [phonemes]
  )

  const activePhoneme = useMemo(
    () => getActivePhoneme(flatPhonemes, currentTimeMs),
    [flatPhonemes, currentTimeMs]
  )

  const activeWord = useMemo(() => {
    if (!phonemes) return null
    return (
      phonemes.timeline.find(
        (w) => w.word_start_ms <= currentTimeMs && currentTimeMs <= w.word_end_ms
      ) ?? null
    )
  }, [phonemes, currentTimeMs])

  const timeToX = useMemo(
    () => (ms: number, canvasWidth: number) =>
      msToX(ms, phonemes?.audio_duration_ms ?? 1, canvasWidth),
    [phonemes?.audio_duration_ms]
  )

  return { activePhoneme, activeWord, flatPhonemes, timeToX }
}
