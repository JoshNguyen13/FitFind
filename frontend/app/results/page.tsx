'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getResults, getMockResults } from '@/lib/api'
import type { AnalyzeResponse, Product, SortOption } from '@/types'
import ProductCard from '@/components/ProductCard'
import SortFilter from '@/components/SortFilter'

export default function ResultsPage() {
  const router = useRouter()
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)
  const [exactItems, setExactItems] = useState<Product[]>([])
  const [relatedItems, setRelatedItems] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState<string | null>(null)
  const [sort, setSort] = useState<SortOption>('relevance')
  const [minPrice, setMinPrice] = useState(0)
  const [maxPrice, setMaxPrice] = useState(10000)
  const [activeItem, setActiveItem] = useState<string | null>(null)

  useEffect(() => {
    const stored = sessionStorage.getItem('fitfind_analysis')
    if (!stored) {
      router.replace('/')
      return
    }
    const data: AnalyzeResponse = JSON.parse(stored)
    setAnalysis(data)
    fetchResults(data, 'relevance', 0, 10000)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function fetchResults(
    data: AnalyzeResponse,
    sortVal: SortOption,
    min: number,
    max: number,
  ) {
    setLoading(true)
    setFetchError(null)
    try {
      const isMock = sessionStorage.getItem('fitfind_mock') === 'true'
      const results = isMock
        ? await getMockResults()
        : await getResults(data.exact_queries, data.related_query, sortVal, min, max)
      setExactItems(results.exact_items)
      setRelatedItems(results.related_items)
    } catch {
      setFetchError('Failed to load products. Try again.')
    } finally {
      setLoading(false)
    }
  }

  function handleFilterChange(newSort: SortOption, newMin: number, newMax: number) {
    setSort(newSort)
    setMinPrice(newMin)
    setMaxPrice(newMax)
    if (analysis) fetchResults(analysis, newSort, newMin, newMax)
  }

  const filteredExact = activeItem
    ? exactItems.filter(p => p.item_label?.startsWith(activeItem) ?? false)
    : exactItems

  if (!analysis) return null

  const detectedItems = analysis.analysis.items.slice(0, 6)

  return (
    <main className="max-w-6xl mx-auto px-8 py-16 min-h-screen">

      {/* Header */}
      <div className="mb-12">
        <button
          onClick={() => router.push('/')}
          className="text-xs tracking-widest uppercase text-neutral-400 hover:text-black transition-colors mb-8 block"
        >
          ← New Search
        </button>
        <div className="flex items-baseline gap-4 border-b border-black pb-6">
          <h1 className="font-serif text-5xl font-light tracking-wide">The Look</h1>
          <span className="text-xs tracking-widest text-neutral-500 capitalize">
            {analysis.analysis.aesthetic}
          </span>
        </div>
      </div>

      {fetchError && (
        <div className="mb-8 p-4 border border-red-200 flex items-center justify-between">
          <p className="text-xs tracking-wide text-red-600">{fetchError}</p>
          <button
            onClick={() => analysis && fetchResults(analysis, sort, minPrice, maxPrice)}
            className="text-xs tracking-widest uppercase underline underline-offset-2 text-red-600 hover:text-red-800"
          >
            Retry
          </button>
        </div>
      )}

      <SortFilter
        sort={sort}
        minPrice={minPrice}
        maxPrice={maxPrice}
        onChange={handleFilterChange}
      />

      {/* Exact Items */}
      <section className="mb-20">
        <div className="flex items-baseline justify-between mb-8">
          <div>
            <h2 className="font-serif text-3xl font-light tracking-wide mb-1">
              Exact Items
            </h2>
            <p className="text-xs tracking-widest uppercase text-neutral-400">
              Detected directly from the source
            </p>
          </div>
        </div>

        {/* Item filter buttons — only show buttons that have at least one product */}
        {!loading && exactItems.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-8">
            {detectedItems
              .filter(item => exactItems.some(p => p.item_label?.startsWith(item)))
              .map(item => (
                <button
                  key={item}
                  onClick={() => setActiveItem(activeItem === item ? null : item)}
                  className={`px-4 py-2 text-xs tracking-widest uppercase transition-colors border ${
                    activeItem === item
                      ? 'bg-black text-white border-black'
                      : 'border-neutral-300 text-neutral-500 hover:border-black hover:text-black'
                  }`}
                >
                  {item}
                </button>
              ))}
          </div>
        )}

        {loading ? (
          <SkeletonGrid />
        ) : filteredExact.length === 0 ? (
          <p className="text-xs tracking-widest uppercase text-neutral-400 py-12">
            No items found
          </p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-6 gap-y-12">
            {filteredExact.map(p => <ProductCard key={p.product_id} product={p} />)}
          </div>
        )}
      </section>

      {/* More aesthetic picks */}
      <section className="pt-12 border-t border-neutral-200">
        <div className="mb-8">
          <h2 className="font-serif text-3xl font-light tracking-wide mb-1 capitalize">
            More {analysis.analysis.aesthetic} Picks
          </h2>
          <p className="text-xs tracking-widest uppercase text-neutral-400">
            Other pieces that fit the {analysis.analysis.aesthetic} style
          </p>
        </div>

        {loading ? (
          <SkeletonGrid />
        ) : relatedItems.length === 0 ? (
          <p className="text-xs tracking-widest uppercase text-neutral-400 py-12">
            No items found
          </p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-6 gap-y-12">
            {relatedItems.map(p => <ProductCard key={p.product_id} product={p} />)}
          </div>
        )}
      </section>
    </main>
  )
}

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-6 gap-y-12">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="aspect-3/4 bg-neutral-100 mb-3" />
          <div className="h-2 bg-neutral-100 mb-2 w-1/3" />
          <div className="h-2 bg-neutral-100 mb-2" />
          <div className="h-2 bg-neutral-100 w-1/4" />
        </div>
      ))}
    </div>
  )
}
