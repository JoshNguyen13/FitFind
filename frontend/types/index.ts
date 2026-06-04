export type AnalysisResult = {
  items: string[]
  aesthetic: string
  confidence: number
}

export type AnalyzeResponse = {
  frame_count: number
  analysis: AnalysisResult
  exact_queries: string[]
  related_query: string
}

export type Product = {
  product_id: string
  product_title: string
  price: number | null
  image_url: string | null
  purchase_url: string | null
  brand: string | null
  section: string
  item_label: string | null
}

export type ResultsResponse = {
  exact_items: Product[]
  related_items: Product[]
}

export type SortOption = 'relevance' | 'price_asc' | 'price_desc' | 'top_rated'
