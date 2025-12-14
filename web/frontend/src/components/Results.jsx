import { useState, useMemo } from 'react'

export default function Results({ results, onBack, onReset }) {
  const [filter, setFilter] = useState('')
  const [showTop, setShowTop] = useState(20)

  const filteredResults = useMemo(() => {
    if (!filter) return results.slice(0, showTop)
    
    const lowerFilter = filter.toLowerCase()
    return results
      .filter(r => r.decks.some(d => d.toLowerCase().includes(lowerFilter)))
      .slice(0, showTop)
  }, [results, filter, showTop])

  const handleExportCSV = () => {
    const headers = ['Deck 1', 'Deck 2', 'Deck 3', 'Deck 4', 'Win Rate']
    const rows = results.map(r => [...r.decks, r.win_rate.toFixed(4)])
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'lineup_results.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  // Best lineup
  const bestLineup = results[0]

  // Class colors
  const getClassColor = (deckName) => {
    const classColors = {
      'Warrior': 'text-amber-600',
      'Paladin': 'text-yellow-400',
      'Hunter': 'text-green-500',
      'Rogue': 'text-yellow-600',
      'Priest': 'text-gray-300',
      'Shaman': 'text-blue-400',
      'Mage': 'text-cyan-400',
      'Warlock': 'text-purple-500',
      'Druid': 'text-orange-600',
      'Demon Hunter': 'text-emerald-400',
      'Death Knight': 'text-sky-300',
    }
    
    for (const [className, color] of Object.entries(classColors)) {
      if (deckName.includes(className)) return color
    }
    return 'text-gray-400'
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-hs-gold">
            Results
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            {results.length} lineups calculated and ranked by win rate
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={onBack}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            ← Back
          </button>
          <button
            onClick={handleExportCSV}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-white transition-colors"
          >
            📥 Export CSV
          </button>
          <button
            onClick={onReset}
            className="px-4 py-2 bg-hs-gold hover:bg-yellow-500 text-hs-dark font-semibold rounded-lg transition-colors"
          >
            New Calculation
          </button>
        </div>
      </div>

      {/* Best Lineup Highlight */}
      {bestLineup && (
        <div className="bg-gradient-to-r from-hs-gold/20 to-yellow-600/20 border border-hs-gold/50 rounded-lg p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-2xl">🏆</span>
            <h3 className="text-lg font-bold text-hs-gold">Best Lineup</h3>
            <span className="ml-auto text-2xl font-bold text-white">
              {(bestLineup.win_rate * 100).toFixed(2)}%
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {bestLineup.decks.map((deck, idx) => (
              <div
                key={idx}
                className="bg-slate-800/50 rounded-lg p-3 text-center"
              >
                <span className={`font-medium ${getClassColor(deck)}`}>
                  {deck}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter and Controls */}
      <div className="flex gap-4 mb-4">
        <input
          type="text"
          placeholder="Filter by deck name..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:border-hs-gold focus:outline-none"
        />
        <select
          value={showTop}
          onChange={(e) => setShowTop(parseInt(e.target.value))}
          className="bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:border-hs-gold focus:outline-none"
        >
          <option value={10}>Top 10</option>
          <option value={20}>Top 20</option>
          <option value={50}>Top 50</option>
          <option value={100}>Top 100</option>
        </select>
      </div>

      {/* Results Table */}
      <div className="bg-slate-700/30 rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-slate-800">
              <th className="px-4 py-3 text-left text-gray-400 text-sm font-medium w-12">
                #
              </th>
              <th className="px-4 py-3 text-left text-gray-400 text-sm font-medium">
                Lineup
              </th>
              <th className="px-4 py-3 text-right text-gray-400 text-sm font-medium w-24">
                Win Rate
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.map((result, idx) => {
              const originalIdx = results.indexOf(result)
              return (
                <tr
                  key={idx}
                  className="border-t border-slate-700 hover:bg-slate-700/50 transition-colors"
                >
                  <td className="px-4 py-3 text-gray-500 text-sm">
                    {originalIdx + 1}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      {result.decks.map((deck, deckIdx) => (
                        <span
                          key={deckIdx}
                          className={`text-sm ${getClassColor(deck)}`}
                        >
                          {deck}
                          {deckIdx < result.decks.length - 1 && (
                            <span className="text-gray-600 ml-2">•</span>
                          )}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <span className={`font-mono font-medium ${
                      result.win_rate >= 0.52
                        ? 'text-green-400'
                        : result.win_rate >= 0.5
                        ? 'text-yellow-400'
                        : 'text-red-400'
                    }`}>
                      {(result.win_rate * 100).toFixed(2)}%
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {filteredResults.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No lineups match your filter
        </div>
      )}

      {/* Statistics */}
      <div className="mt-6 grid md:grid-cols-3 gap-4">
        <div className="bg-slate-700/30 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Highest Win Rate</div>
          <div className="text-xl font-bold text-green-400">
            {(results[0]?.win_rate * 100).toFixed(2)}%
          </div>
        </div>
        <div className="bg-slate-700/30 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Average Top 10</div>
          <div className="text-xl font-bold text-yellow-400">
            {(results.slice(0, 10).reduce((sum, r) => sum + r.win_rate, 0) / Math.min(10, results.length) * 100).toFixed(2)}%
          </div>
        </div>
        <div className="bg-slate-700/30 rounded-lg p-4">
          <div className="text-gray-400 text-sm">Total Lineups</div>
          <div className="text-xl font-bold text-white">
            {results.length}
          </div>
        </div>
      </div>
    </div>
  )
}
