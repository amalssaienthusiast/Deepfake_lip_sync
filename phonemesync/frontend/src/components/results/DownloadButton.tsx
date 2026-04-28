'use client'

import { Download } from 'lucide-react'
import { resolveMediaUrl } from '@/lib/api'

interface DownloadButtonProps {
  videoUrl: string
  jobId: string
}

export function DownloadButton({ videoUrl, jobId }: DownloadButtonProps) {
  const handleDownload = () => {
    const url = resolveMediaUrl(videoUrl)
    const a = document.createElement('a')
    a.href = url
    a.download = `phonemesync_${jobId.substring(0, 8)}.mp4`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }

  return (
    <button
      onClick={handleDownload}
      className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-sm font-medium rounded-lg transition-colors"
    >
      <Download className="w-4 h-4" />
      Save Video
    </button>
  )
}
