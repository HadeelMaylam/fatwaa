'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const [query, setQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const router = useRouter()

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!query.trim()) return

    setIsSearching(true)

    // Navigate to results page with query
    router.push(`/results?q=${encodeURIComponent(query)}`)
  }

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-sage-800 mb-4">
            ابحث عن الفتوى
          </h1>
          <p className="text-sage-600 text-lg">
            ابحث في فتاوى الشيخ ابن باز والشيخ ابن عثيمين
          </p>
        </div>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="space-y-6">
          {/* Search Input */}
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="اكتب سؤالك هنا..."
              className="search-input"
              disabled={isSearching}
            />
          </div>

          {/* Search Button */}
          <button
            type="submit"
            disabled={!query.trim() || isSearching}
            className="search-button w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSearching ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                جاري البحث...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                ابحث
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </span>
            )}
          </button>
        </form>

        {/* Examples */}
        <div className="mt-12 text-center">
          <p className="text-sage-600 mb-4">أمثلة على الأسئلة:</p>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              'ما حكم الصلاة في البيت؟',
              'هل يجوز الصيام بدون سحور؟',
              'حكم الزكاة'
            ].map((example) => (
              <button
                key={example}
                onClick={() => setQuery(example)}
                className="px-4 py-2 bg-white rounded-full text-sage-700
                         hover:bg-sage-100 transition-colors duration-200
                         text-sm shadow-sm border border-sage-200"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  )
}
