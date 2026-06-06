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
    <div className="flex flex-wrap items-end gap-8 mb-12 pb-8 border-b border-neutral-200">
      <div>
        <label className="block text-xs tracking-widest uppercase text-neutral-400 mb-2">
          Sort
        </label>
        <select
          value={sort}
          onChange={handleSortChange}
          className="border-b border-black bg-white text-sm py-1.5 pr-8 outline-none appearance-none cursor-pointer"
        >
          <option value="relevance">Relevance</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="top_rated">Top Rated</option>
        </select>
      </div>

      <div className="flex items-end gap-3">
        <div>
          <label className="block text-xs tracking-widest uppercase text-neutral-400 mb-2">
            Min
          </label>
          <input
            type="number"
            min={0}
            value={localMin}
            onChange={e => setLocalMin(e.target.value)}
            placeholder="—"
            className="w-20 border-b border-black bg-white text-sm py-1.5 outline-none placeholder:text-neutral-300"
          />
        </div>
        <div>
          <label className="block text-xs tracking-widest uppercase text-neutral-400 mb-2">
            Max
          </label>
          <input
            type="number"
            min={0}
            value={localMax}
            onChange={e => setLocalMax(e.target.value)}
            placeholder="—"
            className="w-20 border-b border-black bg-white text-sm py-1.5 outline-none placeholder:text-neutral-300"
          />
        </div>
        <button
          onClick={handlePriceApply}
          className="text-xs tracking-widest uppercase pb-1.5 border-b border-black hover:text-neutral-500 transition-colors"
        >
          Apply
        </button>
      </div>
    </div>
  )
}
