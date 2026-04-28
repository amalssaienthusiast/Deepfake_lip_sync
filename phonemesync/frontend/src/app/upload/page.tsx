'use client'

import { UploadForm } from '@/components/upload/UploadForm'

export default function UploadPage() {
  return (
    <main className="min-h-screen grid-bg flex flex-col items-center justify-center p-4">
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div className="text-center mb-8 fade-in" style={{ animationDelay: '0.1s' }}>
        <h1 className="text-4xl font-bold bg-gradient-to-br from-white to-slate-400 bg-clip-text text-transparent mb-3">
          PhonemeSync
        </h1>
        <p className="text-slate-400 text-sm max-w-sm mx-auto">
          Audio-driven lip synthesis · Phoneme-level analysis
        </p>
      </div>

      {/* ── Main Form ──────────────────────────────────────────────────────── */}
      <div className="w-full max-w-2xl bg-[#1E293B] rounded-2xl border border-slate-700/50 p-6 md:p-8 shadow-2xl shadow-indigo-900/10 fade-in" style={{ animationDelay: '0.2s' }}>
        <UploadForm />
      </div>

      {/* ── Research Footer ────────────────────────────────────────────────── */}
      <div className="mt-12 text-center text-xs text-slate-500 space-y-2 fade-in" style={{ animationDelay: '0.3s' }}>
        <p className="font-mono">
          Powered by Wav2Lip · Whisper · SyncNet · MediaPipe
        </p>
        <p className="opacity-70">
          Baseline: SyncNet 6.37 | SOTA reference: LatentSync 7.62
        </p>
      </div>
    </main>
  )
}
