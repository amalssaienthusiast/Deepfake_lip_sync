'use client'

interface ProgressRingProps {
  progress: number
}

export function ProgressRing({ progress }: ProgressRingProps) {
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (progress / 100) * circumference

  return (
    <div className="relative w-32 h-32 flex items-center justify-center mx-auto mb-8">
      {/* Glow behind ring */}
      <div className="absolute inset-0 rounded-full bg-indigo-500/20 blur-xl processing-bg-pulse" />
      
      <svg className="transform -rotate-90 w-full h-full relative z-10">
        <circle
          cx="64"
          cy="64"
          r={radius}
          stroke="currentColor"
          strokeWidth="4"
          fill="transparent"
          className="text-slate-800"
        />
        <circle
          cx="64"
          cy="64"
          r={radius}
          stroke="currentColor"
          strokeWidth="4"
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="text-indigo-500 transition-all duration-500 ease-out"
          strokeLinecap="round"
        />
      </svg>
      
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-3xl font-light font-mono text-slate-200">
          {progress}
        </span>
        <span className="text-[10px] uppercase tracking-widest text-slate-500 mt-1">
          %
        </span>
      </div>
    </div>
  )
}
