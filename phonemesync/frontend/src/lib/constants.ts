// src/lib/constants.ts

export const VISEME_COLORS: Record<string, string> = {
  silence:      '#94A3B8',
  bilabial:     '#EC4899',
  labiodental:  '#F97316',
  dental:       '#EAB308',
  alveolar:     '#22C55E',
  postalveolar: '#14B8A6',
  velar:        '#6366F1',
  glottal:      '#8B5CF6',
  front_vowel:  '#3B82F6',
  mid_vowel:    '#F97316',
  back_vowel:   '#EF4444',
  diphthong:    '#10B981',
}

export const VISEME_LABELS: Record<string, string> = {
  silence:      'Silence',
  bilabial:     'Bilabial (P,B,M)',
  labiodental:  'Labiodental (F,V)',
  dental:       'Dental (TH)',
  alveolar:     'Alveolar (T,D,N)',
  postalveolar: 'Postalveolar (SH)',
  velar:        'Velar (K,G)',
  glottal:      'Glottal (H)',
  front_vowel:  'Front Vowel (EE,IH)',
  mid_vowel:    'Mid Vowel (AH,ER)',
  back_vowel:   'Back Vowel (AA,OO)',
  diphthong:    'Diphthong (OW,AY)',
}

export const ACCEPTED_VIDEO_TYPES: Record<string, string[]> = {
  'video/mp4':       ['.mp4'],
  'video/quicktime': ['.mov'],
  'video/x-msvideo': ['.avi'],
  'image/jpeg':      ['.jpg', '.jpeg'],
  'image/png':       ['.png'],
}

export const ACCEPTED_AUDIO_TYPES: Record<string, string[]> = {
  'audio/wav':  ['.wav'],
  'audio/mpeg': ['.mp3'],
  'audio/aac':  ['.aac'],
}

export const PROCESSING_STAGES = [
  { key: 'wav2lip',   label: 'Lip Synthesis',     description: 'Wav2Lip GAN inference' },
  { key: 'whisper',   label: 'Phoneme Extraction', description: 'Whisper transcription' },
  { key: 'syncnet',   label: 'Sync Scoring',       description: 'SyncNet confidence' },
  { key: 'mediapipe', label: 'Landmark Detection', description: 'Lip geometry extraction' },
] as const

export const TIMELINE_HEIGHT         = 80
export const TIMELINE_PLAYHEAD_COLOR = '#FFFFFF'
export const TIMELINE_BG             = '#0F172A'
export const CONFIDENCE_HIGH         = 0.75
export const CONFIDENCE_MID          = 0.50

export const POLL_INTERVAL_MS = Number(process.env.NEXT_PUBLIC_POLL_INTERVAL_MS) || 2000
export const MAX_VIDEO_SIZE_MB = Number(process.env.NEXT_PUBLIC_MAX_VIDEO_SIZE_MB) || 50
export const MAX_AUDIO_SIZE_MB = Number(process.env.NEXT_PUBLIC_MAX_AUDIO_SIZE_MB) || 20
