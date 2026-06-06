'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { analyzeUrl, analyzeImage } from '@/lib/api'

function friendlyError(err: unknown): string {
  const msg = err instanceof Error ? err.message : ''
  if (msg.includes('Could not download') || msg.includes('DownloadError'))
    return "This video isn't publicly accessible. Make sure the account is public and try again."
  if (msg.includes('No frames'))
    return "Couldn't extract frames from this video. Try a different URL."
  if (msg.includes('no clothing') || msg.includes('items: []') || msg.includes('No clothing'))
    return 'No clothing detected in this image. Try a clearer photo with a visible outfit.'
  if (msg.includes('Gemini could not'))
    return 'Analysis failed. Try again in a moment.'
  if (msg.includes('fetch') || msg.includes('network') || msg.includes('Failed to fetch'))
    return 'Could not reach the server. Make sure the backend is running.'
  return msg || 'Something went wrong. Try again.'
}

export default function Home() {
  const router = useRouter()
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  async function handleUrlSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const result = await analyzeUrl(url)
      sessionStorage.setItem('fitfind_analysis', JSON.stringify(result))
      sessionStorage.removeItem('fitfind_mock')
      router.push('/select')
    } catch (err) {
      setError(friendlyError(err))
    } finally {
      setLoading(false)
    }
  }

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Please upload a JPG, PNG, or WEBP image.')
      return
    }

    setPreview(URL.createObjectURL(file))
    setError(null)
    setLoading(true)
    try {
      const result = await analyzeImage(file)
      sessionStorage.setItem('fitfind_analysis', JSON.stringify(result))
      sessionStorage.removeItem('fitfind_mock')
      router.push('/select')
    } catch (err) {
      setError(friendlyError(err))
      setPreview(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen max-w-xl mx-auto px-8 flex flex-col justify-center py-24">

      {/* Wordmark */}
      <div className="mb-16">
        <h1 className="font-serif text-6xl font-light tracking-widest uppercase mb-4">
          FitFind
        </h1>
        <p className="text-xs tracking-widest uppercase text-neutral-500">
          Identify any outfit. Shop the look.
        </p>
      </div>

      {/* URL input */}
      <form onSubmit={handleUrlSubmit} className="mb-10">
        <label className="block text-xs tracking-widest uppercase text-neutral-400 mb-3">
          Paste a TikTok or Instagram URL
        </label>
        <div className="flex gap-0 border border-black">
          <input
            type="url"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://www.tiktok.com/@..."
            disabled={loading}
            required
            className="flex-1 px-4 py-3.5 text-sm bg-white outline-none placeholder:text-neutral-300 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !url}
            className="px-6 py-3.5 bg-black text-white text-xs tracking-widest uppercase hover:bg-neutral-800 transition-colors disabled:opacity-40 whitespace-nowrap"
          >
            {loading ? 'Analyzing…' : 'Analyze'}
          </button>
        </div>
      </form>

      {/* Divider */}
      <div className="flex items-center gap-6 mb-10">
        <div className="flex-1 h-px bg-neutral-200" />
        <span className="text-xs tracking-widest uppercase text-neutral-400">Or</span>
        <div className="flex-1 h-px bg-neutral-200" />
      </div>

      {/* Image upload */}
      <input
        ref={fileRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileChange}
        disabled={loading}
        className="hidden"
      />

      {preview ? (
        <div className="relative border border-black overflow-hidden">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={preview} alt="Preview" className="w-full max-h-72 object-cover" />
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-white/80">
              <span className="text-xs tracking-widest uppercase">Analyzing…</span>
            </div>
          )}
        </div>
      ) : (
        <button
          onClick={() => fileRef.current?.click()}
          disabled={loading}
          className="w-full border border-black py-12 text-xs tracking-widest uppercase text-neutral-400 hover:text-black hover:border-black transition-colors disabled:opacity-50"
        >
          Upload Image — JPG, PNG, WEBP
        </button>
      )}

      {error && (
        <p className="mt-6 text-xs text-red-600 tracking-wide">{error}</p>
      )}

    </main>
  )
}
