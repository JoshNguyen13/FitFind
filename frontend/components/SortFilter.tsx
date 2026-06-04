'use client'

import { useState } from 'react'
import type { SortOption } from '@/types'

type Props = {
  sort: SortOption
  minPrice: number
  maxPrice: number
  onChange: (sort: SortOption, minPrice: number, maxPrice: number) => void
}

export default function SortFilter({ sort, minPrice, maxPrice, onChange }: Props) {
  const [localMin, setLocalMin] = useState(minPrice === 0 ? '' : minPrice.toString())
  const [localMax, setLocalMax] = useState(maxPrice === 10000 ? '' : maxPrice.toString())

  function handleSortChange(e: React.ChangeEvent<HTMLSelectElement>) {
    onChange(e.target.value as SortOption, minPrice, maxPrice)
  }

  function handlePriceApply() {
    const min = localMin === '' ? 0 : parseFloat(localMin) || 0
    const max = localMax === '' ? 10000 : parseFloat(localMax) || 10000
    onChange(sort, min, max)
  }

  return (
    <div className="flex flex-wrap items-end gap-4 mb-10 p-4 bg-gray-50 rounded-xl">
      <div>
        <label className="block text-xs text-gray-500 mb-1.5">Sort by</label>
        <select
          value={sort}
          onChange={handleSortChange}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-black"
        >
          <option value="relevance">Relevance</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="top_rated">Top Rated</option>
        </select>
      </div>

      <div>
        <label className="block text-xs text-gray-500 mb-1.5">Min price</label>
        <input
          type="number"
          min={0}
          value={localMin}
          onChange={e => setLocalMin(e.target.value)}
          placeholder="0"
          className="w-24 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>

      <div>
        <label className="block text-xs text-gray-500 mb-1.5">Max price</label>
        <input
          type="number"
          min={0}
          value={localMax}
          onChange={e => setLocalMax(e.target.value)}
          placeholder="No limit"
          className="w-24 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
        />
      </div>

      <button
        onClick={handlePriceApply}
        className="px-4 py-2 bg-black text-white text-sm font-medium rounded-lg hover:bg-gray-800 transition-colors"
      >
        Apply
      </button>
    </div>
  )
}
