'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { cn } from '@/lib/utils'
import { Upload } from 'lucide-react'
import type { ReactNode } from 'react'

interface DropZoneProps {
  accept: Record<string, string[]>
  maxSizeMB: number
  label: string
  icon?: ReactNode
  onFileAccepted: (file: File) => void
  currentFile: File | null
}

export function DropZone({
  accept,
  maxSizeMB,
  label,
  icon,
  onFileAccepted,
  currentFile,
}: DropZoneProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onFileAccepted(accepted[0])
    },
    [onFileAccepted]
  )

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept,
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: false,
  })

  const hasError = fileRejections.length > 0

  return (
    <div
      {...getRootProps()}
      className={cn(
        'relative flex flex-col items-center justify-center min-h-[200px] rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200 select-none',
        isDragActive
          ? 'border-indigo-500 bg-indigo-500/10 glow-active'
          : hasError
          ? 'border-red-500 bg-red-500/5'
          : currentFile
          ? 'border-emerald-500/50 bg-emerald-500/5'
          : 'border-slate-600 bg-slate-800/40 hover:border-slate-500 hover:bg-slate-800/60'
      )}
    >
      <input {...getInputProps()} />

      {currentFile ? (
        <div className="flex flex-col items-center gap-2 p-4 text-center">
          <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
            <span className="text-emerald-400 text-xl">✓</span>
          </div>
          <p className="text-sm font-medium text-emerald-400 truncate max-w-[180px]">
            {currentFile.name}
          </p>
          <p className="text-xs text-slate-500">
            {(currentFile.size / (1024 * 1024)).toFixed(1)} MB
          </p>
          <p className="text-xs text-slate-600">Click or drop to replace</p>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-3 p-6 text-center">
          <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center text-slate-400">
            {icon ?? <Upload className="w-5 h-5" />}
          </div>
          <div>
            <p className="text-sm font-medium text-slate-300">{label}</p>
            <p className="text-xs text-slate-500 mt-1">
              Drag & drop or click to browse
            </p>
            <p className="text-xs text-slate-600 mt-0.5">Max {maxSizeMB} MB</p>
          </div>
        </div>
      )}

      {isDragActive && (
        <div className="absolute inset-0 rounded-xl bg-indigo-500/10 flex items-center justify-center">
          <p className="text-indigo-400 font-medium text-sm">Drop it here</p>
        </div>
      )}

      {hasError && (
        <p className="absolute bottom-2 text-xs text-red-400">
          {fileRejections[0]?.errors[0]?.message ?? 'Invalid file'}
        </p>
      )}
    </div>
  )
}
