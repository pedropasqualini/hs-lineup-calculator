import { useState } from 'react'

export default function CalculateStep({ matchups, field, onComplete, onBack, setProgress, setIsLoading }) {
  const [error, setError] = useState(null)
  const [isCalculating, setIsCalculating] = useState(false)

  const handleCalculate = () => {
    setIsLoading(true)
    setIsCalculating(true)
    setError(null)

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/calculate`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      ws.send(JSON.stringify({
        matchups,
        field,
      }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setProgress({
        phase: data.phase,
        progress: data.progress,
        message: data.message,
      })

      if (data.completed) {
        setIsLoading(false)
        setIsCalculating(false)
        if (data.error) {
          setError(data.error)
        } else if (data.results) {
          onComplete(data.results)
        }
        ws.close()
      }
    }

    ws.onerror = (err) => {
      console.error('WebSocket error:', err)
      setError('Connection error. Please try again.')
      setIsLoading(false)
      setIsCalculating(false)
    }

    ws.onclose = () => {
      setIsLoading(false)
      setIsCalculating(false)
    }
  }

  // Summary of data
  const deckCount = matchups.deck_names.length
  const fieldEntries = field.entries.filter(e => e.pct > 0).length

  // Estimate calculation time (rough)
  const estimatedTime = Math.ceil((deckCount * deckCount * fieldEntries) / 5000)

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-hs-gold">
          Calculate Optimal Lineups
        </h2>
        <button
          onClick={onBack}
          className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
        >
          ← Back
        </button>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-6">
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {/* Summary */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <div className="bg-slate-700/50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-hs-gold">{deckCount}</div>
          <div className="text-gray-400 text-sm">Decks</div>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-hs-gold">{fieldEntries}</div>
          <div className="text-gray-400 text-sm">Field Entries</div>
        </div>
        <div className="bg-slate-700/50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-hs-gold">~{estimatedTime}s</div>
          <div className="text-gray-400 text-sm">Est. Time</div>
        </div>
      </div>

      {/* Mode Info */}
      <div className="bg-slate-700/30 rounded-lg p-6 mb-6">
        <h3 className="text-white font-medium mb-2">Conquest Bo5 with Ban</h3>
        <p className="text-gray-400 text-sm">
          The calculator will find the optimal 4-deck lineup for Conquest Best of 5 format 
          with one ban. It uses game theory (Lemke-Howson algorithm) to model perfect 
          decision-making by both players during the ban phase.
        </p>
      </div>

      {/* Calculation Process */}
      <div className="bg-slate-700/30 rounded-lg p-6 mb-6">
        <h3 className="text-white font-medium mb-4">What happens next:</h3>
        <ol className="space-y-3 text-sm text-gray-400">
          <li className="flex gap-3">
            <span className="text-hs-gold font-medium">1.</span>
            <span>Generate all possible 4-deck lineups (one deck per class)</span>
          </li>
          <li className="flex gap-3">
            <span className="text-hs-gold font-medium">2.</span>
            <span>Create artificial field of ~400 lineups based on deck frequencies</span>
          </li>
          <li className="flex gap-3">
            <span className="text-hs-gold font-medium">3.</span>
            <span>For each lineup, calculate expected win rate against the entire field</span>
          </li>
          <li className="flex gap-3">
            <span className="text-hs-gold font-medium">4.</span>
            <span>Apply game theory to optimize ban decisions for each matchup</span>
          </li>
          <li className="flex gap-3">
            <span className="text-hs-gold font-medium">5.</span>
            <span>Rank lineups by overall expected win rate</span>
          </li>
        </ol>
      </div>

      {/* Calculate Button */}
      <button
        onClick={handleCalculate}
        disabled={isCalculating}
        className={`w-full py-4 rounded-lg font-bold text-lg transition-all ${
          isCalculating
            ? 'bg-slate-700 text-gray-500 cursor-not-allowed'
            : 'bg-hs-gold hover:bg-yellow-500 text-hs-dark hover:scale-[1.02]'
        }`}
      >
        {isCalculating ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Calculating...
          </span>
        ) : (
          '⚔️ Calculate Optimal Lineups'
        )}
      </button>
    </div>
  )
}
