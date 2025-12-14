import { useState, useEffect, useRef } from 'react'

export default function DataSourceStep({ onDataLoaded, setProgress, setIsLoading }) {
  const [mode, setMode] = useState(null) // 'crawler' or 'manual'
  const [options, setOptions] = useState(null)
  const [crawlerSettings, setCrawlerSettings] = useState({
    league_rank_range: 'BRONZE_THROUGH_GOLD',
    game_type: 'RANKED_STANDARD',
    region: 'ALL',
    time_range: 'LAST_7_DAYS',
    min_games: 10000,
  })
  const [uploadedMatchups, setUploadedMatchups] = useState(null)
  const [uploadedField, setUploadedField] = useState(null)
  const [error, setError] = useState(null)
  const matchupsInputRef = useRef(null)
  const fieldInputRef = useRef(null)

  useEffect(() => {
    // Fetch available options
    fetch('/api/options')
      .then((res) => res.json())
      .then((data) => {
        setOptions(data)
        setCrawlerSettings((prev) => ({
          ...prev,
          ...data.defaults,
        }))
      })
      .catch((err) => {
        console.error('Failed to fetch options:', err)
      })
  }, [])

  const handleCrawl = () => {
    setIsLoading(true)
    setError(null)

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/crawl`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      ws.send(JSON.stringify(crawlerSettings))
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
        if (data.error) {
          setError(data.error)
        } else if (data.matchups && data.field) {
          onDataLoaded(data.matchups, data.field)
        }
        ws.close()
      }
    }

    ws.onerror = (err) => {
      console.error('WebSocket error:', err)
      setError('Connection error. Please try again.')
      setIsLoading(false)
    }

    ws.onclose = () => {
      setIsLoading(false)
    }
  }

  const handleMatchupsUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload/matchups', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      if (data.success) {
        setUploadedMatchups(data.matchups)
        setError(null)
      } else {
        setError(data.detail || 'Failed to parse matchups file')
      }
    } catch (err) {
      setError('Failed to upload matchups file')
    }
  }

  const handleFieldUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/upload/field', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      if (data.success) {
        setUploadedField(data.field)
        setError(null)
      } else {
        setError(data.detail || 'Failed to parse field file')
      }
    } catch (err) {
      setError('Failed to upload field file')
    }
  }

  const handleManualContinue = () => {
    if (uploadedMatchups) {
      // If no field uploaded, create default field with equal distribution
      const defaultField = uploadedField || {
        entries: uploadedMatchups.deck_names.map((deck) => ({
          deck,
          pct: 100 / uploadedMatchups.deck_names.length,
        })),
      }
      onDataLoaded(uploadedMatchups, defaultField)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-hs-gold mb-6">
        Choose Data Source
      </h2>

      {error && (
        <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-6">
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {!mode && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Crawler Option */}
          <button
            onClick={() => setMode('crawler')}
            className="p-6 bg-slate-700/50 hover:bg-slate-700 rounded-lg border border-slate-600 hover:border-hs-gold transition-all text-left"
          >
            <div className="text-3xl mb-4">🌐</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Use HSReplay Crawler
            </h3>
            <p className="text-gray-400 text-sm">
              Fetch the latest matchup data directly from HSReplay.net. 
              Requires no preparation, but needs internet connection.
            </p>
          </button>

          {/* Manual Option */}
          <button
            onClick={() => setMode('manual')}
            className="p-6 bg-slate-700/50 hover:bg-slate-700 rounded-lg border border-slate-600 hover:border-hs-gold transition-all text-left"
          >
            <div className="text-3xl mb-4">📁</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Upload CSV Files
            </h3>
            <p className="text-gray-400 text-sm">
              Upload your own matchup and field data as CSV files. 
              Use this for custom matchups or offline analysis.
            </p>
          </button>
        </div>
      )}

      {mode === 'crawler' && options && (
        <div className="space-y-6">
          <button
            onClick={() => setMode(null)}
            className="text-gray-400 hover:text-white text-sm mb-4"
          >
            ← Back to options
          </button>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Rank Range
              </label>
              <select
                value={crawlerSettings.league_rank_range}
                onChange={(e) =>
                  setCrawlerSettings((prev) => ({
                    ...prev,
                    league_rank_range: e.target.value,
                  }))
                }
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:border-hs-gold focus:outline-none"
              >
                {options.league_rank_range.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Game Type
              </label>
              <select
                value={crawlerSettings.game_type}
                onChange={(e) =>
                  setCrawlerSettings((prev) => ({
                    ...prev,
                    game_type: e.target.value,
                  }))
                }
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:border-hs-gold focus:outline-none"
              >
                {options.game_type.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Region
              </label>
              <select
                value={crawlerSettings.region}
                onChange={(e) =>
                  setCrawlerSettings((prev) => ({
                    ...prev,
                    region: e.target.value,
                  }))
                }
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:border-hs-gold focus:outline-none"
              >
                {options.region.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Time Range
              </label>
              <select
                value={crawlerSettings.time_range}
                onChange={(e) =>
                  setCrawlerSettings((prev) => ({
                    ...prev,
                    time_range: e.target.value,
                  }))
                }
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:border-hs-gold focus:outline-none"
              >
                {options.time_range.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm text-gray-400 mb-2">
                Minimum Games (aim for ~20 decks)
              </label>
              <input
                type="number"
                value={crawlerSettings.min_games}
                onChange={(e) =>
                  setCrawlerSettings((prev) => ({
                    ...prev,
                    min_games: parseInt(e.target.value) || 10000,
                  }))
                }
                min={1000}
                max={100000}
                step={1000}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white focus:border-hs-gold focus:outline-none"
              />
              <p className="text-xs text-gray-500 mt-1">
                Higher value = fewer decks, faster calculation
              </p>
            </div>
          </div>

          <button
            onClick={handleCrawl}
            className="w-full bg-hs-gold hover:bg-yellow-500 text-hs-dark font-semibold py-3 rounded-lg transition-colors"
          >
            Fetch Data from HSReplay
          </button>
        </div>
      )}

      {mode === 'manual' && (
        <div className="space-y-6">
          <button
            onClick={() => setMode(null)}
            className="text-gray-400 hover:text-white text-sm mb-4"
          >
            ← Back to options
          </button>

          {/* Matchups Upload */}
          <div className="border border-slate-600 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-white font-medium">Matchups CSV</h3>
                <p className="text-gray-400 text-sm">
                  Square matrix with deck names as headers
                </p>
              </div>
              {uploadedMatchups && (
                <span className="text-green-400 text-sm">
                  ✓ {uploadedMatchups.deck_names.length} decks loaded
                </span>
              )}
            </div>
            <input
              ref={matchupsInputRef}
              type="file"
              accept=".csv"
              onChange={handleMatchupsUpload}
              className="hidden"
            />
            <button
              onClick={() => matchupsInputRef.current?.click()}
              className="w-full bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-lg py-3 text-white transition-colors"
            >
              {uploadedMatchups ? 'Replace Matchups File' : 'Upload Matchups CSV'}
            </button>
          </div>

          {/* Field Upload */}
          <div className="border border-slate-600 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-white font-medium">Field CSV (Optional)</h3>
                <p className="text-gray-400 text-sm">
                  Deck names with frequency percentages
                </p>
              </div>
              {uploadedField && (
                <span className="text-green-400 text-sm">
                  ✓ {uploadedField.entries.length} entries loaded
                </span>
              )}
            </div>
            <input
              ref={fieldInputRef}
              type="file"
              accept=".csv"
              onChange={handleFieldUpload}
              className="hidden"
            />
            <button
              onClick={() => fieldInputRef.current?.click()}
              className="w-full bg-slate-700 hover:bg-slate-600 border border-slate-600 rounded-lg py-3 text-white transition-colors"
            >
              {uploadedField ? 'Replace Field File' : 'Upload Field CSV'}
            </button>
          </div>

          <button
            onClick={handleManualContinue}
            disabled={!uploadedMatchups}
            className={`w-full py-3 rounded-lg font-semibold transition-colors ${
              uploadedMatchups
                ? 'bg-hs-gold hover:bg-yellow-500 text-hs-dark'
                : 'bg-slate-700 text-gray-500 cursor-not-allowed'
            }`}
          >
            Continue with Uploaded Data
          </button>
        </div>
      )}
    </div>
  )
}
