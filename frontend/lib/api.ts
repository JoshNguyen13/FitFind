import type { AnalyzeResponse, ResultsResponse, SortOption } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed with status ${res.status}`)
  }
  return res.json()
}

export async function analyzeMock(): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/analyze-mock`, { method: 'POST' })
  return handleResponse<AnalyzeResponse>(res)
}

export async function getMockResults(): Promise<ResultsResponse> {
  const res = await fetch(`${API_URL}/results-mock`, { method: 'POST' })
  return handleResponse<ResultsResponse>(res)
}

export async function analyzeUrl(url: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_URL}/analyze-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  return handleResponse<AnalyzeResponse>(res)
}

export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_URL}/analyze-image`, {
    method: 'POST',
    body: form,
  })
  return handleResponse<AnalyzeResponse>(res)
}

export async function getResults(
  exactQueries: string[],
  relatedQuery: string,
): Promise<ResultsResponse> {
  const res = await fetch(`${API_URL}/results`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      exact_queries: exactQueries,
      related_query: relatedQuery,
    }),
  })
  return handleResponse<ResultsResponse>(res)
}
