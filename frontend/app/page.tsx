'use client'

import { useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { analyzeUrl, analyzeImage } from '@/lib/api'

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
      router.push('/results')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Try again.')
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
      router.push('/results')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Try again.')
      setPreview(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen max-w-xl mx-auto px-6 py-20">
      <h1 className="text-4xl font-bold tracking-tight mb-2">FitFind</h1>
      <p className="text-gray-500 mb-12 text-sm">
        Paste a TikTok or Instagram URL, or upload a screenshot — get shoppable results.
      </p>

      {/* URL input */}
      <form onSubmit={handleUrlSubmit} className="flex gap-3 mb-8">
        <input
          type="url"
          value={url}
          onChange={e => setUrl(e.target.value)}
          placeholder="https://www.tiktok.com/@..."
          disabled={loading}
          required
          className="flex-1 border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-black disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !url}
          className="bg-black text-white px-5 py-3 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors disabled:opacity-40"
        >
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>

      {/* Divider */}
      <div className="flex items-center gap-4 mb-8">
        <div className="flex-1 h-px bg-gray-200" />
        <span className="text-xs text-gray-400 uppercase tracking-wide">or upload an image</span>
        <div className="flex-1 h-px bg-gray-200" />
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
        <div className="relative rounded-lg overflow-hidden">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={preview} alt="Preview" className="w-full max-h-72 object-cover" />
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-white/75">
              <span className="text-sm font-medium">Analyzing…</span>
            </div>
          )}
        </div>
      ) : (
        <button
          onClick={() => fileRef.current?.click()}
          disabled={loading}
          className="w-full border-2 border-dashed border-gray-300 rounded-lg py-14 text-sm text-gray-400 hover:border-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
        >
          Click to upload JPG, PNG, or WEBP
        </button>
      )}

      {error && <p className="mt-5 text-sm text-red-600">{error}</p>}
    </main>
  )
}
