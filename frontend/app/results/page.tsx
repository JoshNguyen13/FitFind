'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getResults } from '@/lib/api'
import type { AnalyzeResponse, Product, SortOption } from '@/types'
import ProductCard from '@/components/ProductCard'
import DetectedTags from '@/components/DetectedTags'
import SortFilter from '@/components/SortFilter'

export default function ResultsPage() {
  const router = useRouter()
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)
  const [exactItems, setExactItems] = useState<Product[]>([])
  const [relatedItems, setRelatedItems] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
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
    try {
      const results = await getResults(data.exact_queries, data.related_query, sortVal, min, max)
      setExactItems(results.exact_items)
      setRelatedItems(results.related_items)
    } catch {
      // Leave current results in place on a failed re-fetch
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

  // Filter exact items by selected item label. item_label is the full query string
  // (e.g. "light blue polo shirt streetwear"), analysis.items are the clean names
  // (e.g. "light blue polo shirt"), so startsWith matches them correctly.
  const filteredExact = activeItem
    ? exactItems.filter(p => p.item_label?.startsWith(activeItem) ?? false)
    : exactItems

  if (!analysis) return null

  const detectedItems = analysis.analysis.items.slice(0, 6)

  return (
    <main className="max-w-6xl mx-auto px-6 py-12">
      {/* Back link + detected tags */}
      <div className="mb-10">
        <button
          onClick={() => router.push('/')}
          className="text-sm text-gray-400 hover:text-black mb-6 block transition-colors"
        >
          ← New search
        </button>
        <h1 className="text-2xl font-bold mb-4">Results</h1>
        <DetectedTags analysis={analysis.analysis} />
      </div>

      <SortFilter
        sort={sort}
        minPrice={minPrice}
        maxPrice={maxPrice}
        onChange={handleFilterChange}
      />

      {/* Exact Items */}
      <section className="mb-16">
        <h2 className="text-lg font-semibold mb-1">Exact Items</h2>
        <p className="text-sm text-gray-400 mb-4">Items detected directly from the source</p>

        {/* Item filter buttons */}
        {!loading && exactItems.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-6">
            <button
              onClick={() => setActiveItem(null)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                activeItem === null
                  ? 'bg-black text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              All
            </button>
            {detectedItems.map(item => (
              <button
                key={item}
                onClick={() => setActiveItem(activeItem === item ? null : item)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium capitalize transition-colors ${
                  activeItem === item
                    ? 'bg-black text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
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
          <p className="text-sm text-gray-400 py-8">No exact items found</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
            {filteredExact.map(p => <ProductCard key={p.product_id} product={p} />)}
          </div>
        )}
      </section>

      {/* Related Items */}
      <section>
        <h2 className="text-lg font-semibold mb-1">Related Items</h2>
        <p className="text-sm text-gray-400 mb-6">
          More items matching the {analysis.analysis.aesthetic} aesthetic
        </p>
        {loading ? (
          <SkeletonGrid />
        ) : relatedItems.length === 0 ? (
          <p className="text-sm text-gray-400 py-8">No related items found</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
            {relatedItems.map(p => <ProductCard key={p.product_id} product={p} />)}
          </div>
        )}
      </section>
    </main>
  )
}

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="animate-pulse">
          <div className="aspect-[3/4] bg-gray-200 rounded-lg mb-3" />
          <div className="h-2.5 bg-gray-200 rounded mb-2 w-1/2" />
          <div className="h-2.5 bg-gray-200 rounded mb-2" />
          <div className="h-2.5 bg-gray-200 rounded w-1/3" />
        </div>
      ))}
    </div>
  )
}
