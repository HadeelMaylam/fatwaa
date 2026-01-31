'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import axios from 'axios'

interface Fatwa {
  question: string
  answer: string
  shaykh: string
  series: string
  link: string
  confidence_score?: number
}

interface SearchResponse {
  found: boolean
  confidence?: number
  fatwa?: Fatwa
  other_results?: Fatwa[]
  message?: string
  suggestions?: string[]
}

export default function ResultsPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const query = searchParams.get('q') || ''

  const [results, setResults] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!query) {
      router.push('/')
      return
    }

    searchFatwas()
  }, [query])

  const searchFatwas = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post<SearchResponse>(
        'http://localhost:8000/api/search',
        {
          query: query,
          limit: 5
        }
      )

      setResults(response.data)
    } catch (err: any) {
      console.error('Search error:', err)
      setError(err.response?.data?.detail || 'حدث خطأ أثناء البحث')
    } finally {
      setLoading(false)
    }
  }

  const FatwaCard = ({ fatwa, index }: { fatwa: Fatwa; index: number }) => (
    <div className="fatwa-card" key={index}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-sage-900 font-bold text-xl mb-2">
            المبدع: {fatwa.shaykh}
          </h3>
          <p className="text-sage-700 text-sm">
            العصر: {fatwa.series}
          </p>
        </div>
        {fatwa.confidence_score && (
          <div className="bg-white px-4 py-2 rounded-full shadow-sm">
            <span className="text-sage-700 font-semibold">
              {(fatwa.confidence_score * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>

      {/* Question */}
      <div className="mb-4">
        <h4 className="text-sage-800 font-semibold mb-2 flex items-center gap-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
          </svg>
          السؤال:
        </h4>
        <p className="text-sage-900 leading-relaxed bg-white/50 p-4 rounded-xl">
          {fatwa.question}
        </p>
      </div>

      {/* Answer */}
      <div className="mb-4">
        <h4 className="text-sage-800 font-semibold mb-2 flex items-center gap-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clipRule="evenodd" />
          </svg>
          الجواب:
        </h4>
        <p className="text-sage-900 leading-relaxed bg-white/50 p-4 rounded-xl whitespace-pre-line">
          {fatwa.answer}
        </p>
      </div>

      {/* Link */}
      {fatwa.link && (
        <a
          href={fatwa.link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sage-600 hover:text-sage-800
                     transition-colors duration-200 text-sm font-medium"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          المصدر
        </a>
      )}
    </div>
  )

  return (
    <main className="min-h-screen p-4 py-12">
      <div className="max-w-4xl mx-auto">
        {/* Header with back button */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/')}
            className="mb-4 flex items-center gap-2 text-sage-700 hover:text-sage-900
                       transition-colors duration-200 font-medium"
          >
            <svg className="w-5 h-5 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            بحث جديد
          </button>

          <div className="bg-white rounded-2xl p-6 shadow-lg border border-sage-200">
            <p className="text-sage-600 text-sm mb-2">سؤالك:</p>
            <p className="text-sage-900 font-semibold text-lg">{query}</p>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-sage-200 border-t-sage-600"></div>
            <p className="text-sage-700 mt-4 text-lg">جاري البحث...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
            <p className="text-red-700 font-semibold">{error}</p>
          </div>
        )}

        {/* No Results */}
        {!loading && !error && results && !results.found && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-8 text-center">
            <h3 className="text-yellow-800 font-bold text-xl mb-4">{results.message}</h3>
            {results.suggestions && results.suggestions.length > 0 && (
              <div className="mt-4">
                <p className="text-yellow-700 mb-2">اقتراحات:</p>
                <ul className="text-yellow-600 space-y-1">
                  {results.suggestions.map((suggestion, i) => (
                    <li key={i}>• {suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Results */}
        {!loading && !error && results && results.found && (
          <div className="space-y-6">
            {/* Warning Message */}
            {results.message && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-4 text-center">
                <p className="text-yellow-800">{results.message}</p>
              </div>
            )}

            {/* Main Result */}
            {results.fatwa && (
              <div>
                <h2 className="text-2xl font-bold text-sage-900 mb-4">النتيجة الأفضل:</h2>
                <FatwaCard fatwa={results.fatwa} index={0} />
              </div>
            )}

            {/* Other Results */}
            {results.other_results && results.other_results.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-sage-900 mb-4">نتائج أخرى:</h2>
                <div className="space-y-4">
                  {results.other_results.map((fatwa, index) => (
                    <FatwaCard key={index} fatwa={fatwa} index={index + 1} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
