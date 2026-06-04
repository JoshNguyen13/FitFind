import type { AnalysisResult } from '@/types'

export default function DetectedTags({ analysis }: { analysis: AnalysisResult }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Aesthetic badge */}
      <span className="bg-black text-white text-xs font-semibold px-3 py-1.5 rounded-full capitalize">
        {analysis.aesthetic}
      </span>

      {/* Detected item tags */}
      {analysis.items.map(item => (
        <span
          key={item}
          className="bg-gray-100 text-gray-700 text-xs px-3 py-1.5 rounded-full capitalize"
        >
          {item}
        </span>
      ))}
    </div>
  )
}
