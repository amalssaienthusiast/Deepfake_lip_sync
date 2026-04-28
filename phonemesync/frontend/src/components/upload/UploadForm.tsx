'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { FileVideo, Music, ArrowRight, Loader2 } from 'lucide-react'
import { DropZone } from './DropZone'
import { submitJob } from '@/lib/api'
import { useStore } from '@/lib/store'
import {
  ACCEPTED_VIDEO_TYPES,
  ACCEPTED_AUDIO_TYPES,
  MAX_VIDEO_SIZE_MB,
  MAX_AUDIO_SIZE_MB,
} from '@/lib/constants'

export function UploadForm() {
  const router     = useRouter()
  const faceFile   = useStore((s) => s.faceFile)
  const audioFile  = useStore((s) => s.audioFile)
  const setFace    = useStore((s) => s.setFaceFile)
  const setAudio   = useStore((s) => s.setAudioFile)
  const setJobId   = useStore((s) => s.setJobId)

  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!faceFile || !audioFile) {
      toast.error('Please select both a face file and an audio file.')
      return
    }
    setLoading(true)
    try {
      const resp = await submitJob(faceFile, audioFile)
      setJobId(resp.job_id)
      toast.success('Job submitted! Starting processing...')
      router.push(`/processing/${resp.job_id}`)
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { message?: string } } })
          ?.response?.data?.message ?? 'Failed to submit job. Is the API running?'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const bothReady = Boolean(faceFile && audioFile)

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Drop zones */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Face Source
          </label>
          <DropZone
            accept={ACCEPTED_VIDEO_TYPES}
            maxSizeMB={MAX_VIDEO_SIZE_MB}
            label="Face Image or Video"
            icon={<FileVideo className="w-5 h-5" />}
            onFileAccepted={setFace}
            currentFile={faceFile}
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Target Audio
          </label>
          <DropZone
            accept={ACCEPTED_AUDIO_TYPES}
            maxSizeMB={MAX_AUDIO_SIZE_MB}
            label="Speech Audio"
            icon={<Music className="w-5 h-5" />}
            onFileAccepted={setAudio}
            currentFile={audioFile}
          />
        </div>
      </div>

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!bothReady || loading}
        className={`
          w-full flex items-center justify-center gap-2 py-3 px-6 rounded-xl
          font-medium text-sm transition-all duration-200
          ${bothReady && !loading
            ? 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 cursor-pointer'
            : 'bg-slate-700 text-slate-500 cursor-not-allowed'
          }
        `}
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Submitting...
          </>
        ) : (
          <>
            Synthesize Lip Sync
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>

      {/* Hint */}
      <p className="text-center text-xs text-slate-600">
        ~45 seconds on CPU · Results stored for 1 hour
      </p>
    </div>
  )
}
