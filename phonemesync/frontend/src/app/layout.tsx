import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'sonner'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PhonemeSync — Audio-driven lip synthesis',
  description:
    'Real-time phoneme-to-viseme alignment with per-frame sync confidence. ' +
    'Powered by Wav2Lip, Whisper, SyncNet, and MediaPipe.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0F172A] text-slate-100 min-h-screen`}>
        {children}
        <Toaster
          position="bottom-right"
          theme="dark"
          toastOptions={{
            style: {
              background: '#1E293B',
              border: '1px solid #334155',
              color: '#F1F5F9',
            },
          }}
        />
      </body>
    </html>
  )
}
