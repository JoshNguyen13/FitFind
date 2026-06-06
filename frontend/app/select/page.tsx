'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { AnalyzeResponse } from '@/types'

export default function SelectPage() {
  const router = useRouter()
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)
  const [selected, setSelected] = useState<Set<string>>(new Set())

  useEffect(() => {
    const stored = sessionStorage.getItem('fitfind_analysis')
    if (!stored) {
      router.replace('/')
      return
    }
    const data: AnalyzeResponse = JSON.parse(stored)
    setAnalysis(data)
    setSelected(new Set(data.analysis.items))
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function toggle(item: string) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(item)) next.delete(item)
      else next.add(item)
      return next
    })
  }

  function handleShop() {
    if (!analysis) return
    const updated = {
      ...analysis,
      exact_queries: analysis.analysis.items.filter(item => selected.has(item)),
    }
    sessionStorage.setItem('fitfind_analysis', JSON.stringify(updated))
    router.push('/results')
  }

  if (!analysis) return null

  const items = analysis.analysis.items
  const allSelected = selected.size === items.length

  return (
    <main className="max-w-xl mx-auto px-8 py-16 min-h-screen">

      <button
        onClick={() => router.push('/')}
        className="text-xs tracking-widest uppercase text-neutral-400 hover:text-black transition-colors mb-8 block"
      >
        ← New Search
      </button>

      <div className="border-b border-black pb-6 mb-10">
        <h1 className="font-serif text-5xl font-light tracking-wide mb-2">Select Items</h1>
        <p className="text-xs tracking-widest uppercase text-neutral-500 capitalize">
          {analysis.analysis.aesthetic} · {items.length} item{items.length !== 1 ? 's' : ''} detected
        </p>
      </div>

      <p className="text-xs tracking-widest uppercase text-neutral-400 mb-6">
        Choose what to shop for
      </p>

      <div className="mb-10">
        {items.map(item => (
          <button
            key={item}
            onClick={() => toggle(item)}
            className="w-full flex items-center gap-4 py-4 border-b border-neutral-100 text-left group hover:border-neutral-300 transition-colors"
          >
            <div className={`w-4 h-4 border flex-shrink-0 flex items-center justify-center transition-colors ${
              selected.has(item)
                ? 'bg-black border-black'
                : 'border-neutral-400 group-hover:border-black'
            }`}>
              {selected.has(item) && (
                <svg viewBox="0 0 16 16" className="w-full h-full text-white" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <polyline points="3,8 6.5,12 13,4" />
                </svg>
              )}
            </div>
            <span className={`text-sm capitalize transition-colors ${
              selected.has(item) ? 'text-black' : 'text-neutral-400 group-hover:text-black'
            }`}>
              {item}
            </span>
          </button>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={() => setSelected(allSelected ? new Set() : new Set(items))}
          className="text-xs tracking-widest uppercase text-neutral-400 hover:text-black transition-colors"
        >
          {allSelected ? 'Deselect All' : 'Select All'}
        </button>
        <button
          onClick={handleShop}
          disabled={selected.size === 0}
          className="px-8 py-3.5 bg-black text-white text-xs tracking-widest uppercase hover:bg-neutral-800 transition-colors disabled:opacity-40"
        >
          Shop Selected ({selected.size})
        </button>
      </div>
    </main>
  )
}
