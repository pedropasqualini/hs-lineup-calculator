import { useState, useMemo } from 'react'

export default function FieldEditor({ field, deckNames, onConfirm, onBack }) {
  const [editedField, setEditedField] = useState(() => {
    // Ensure all deck names from matchups are in the field
    const existingDecks = new Set(field.entries.map(e => e.deck))
    const entries = [...field.entries]
    
    // Add missing decks with 0 frequency
    for (const deck of deckNames) {
      if (!existingDecks.has(deck)) {
        entries.push({ deck, pct: 0 })
      }
    }
    
    // Filter out decks not in matchups
    return {
      entries: entries.filter(e => deckNames.includes(e.deck))
    }
  })

  const handlePctChange = (deck, value) => {
    const numValue = parseFloat(value) || 0
    setEditedField(prev => ({
      entries: prev.entries.map(e =>
        e.deck === deck ? { ...e, pct: Math.max(0, numValue) } : e
      )
    }))
  }

  const totalPct = useMemo(() => {
    return editedField.entries.reduce((sum, e) => sum + e.pct, 0)
  }, [editedField])

  const sortedEntries = useMemo(() => {
    return [...editedField.entries].sort((a, b) => b.pct - a.pct)
  }, [editedField])

  const handleNormalize = () => {
    if (totalPct === 0) return
    setEditedField(prev => ({
      entries: prev.entries.map(e => ({
        ...e,
        pct: (e.pct / totalPct) * 400 // Normalize to ~400 total
      }))
    }))
  }

  const handleEqualDistribution = () => {
    const equalPct = 400 / editedField.entries.length
    setEditedField(prev => ({
      entries: prev.entries.map(e => ({
        ...e,
        pct: equalPct
      }))
    }))
  }

  const handleConfirm = () => {
    // Filter out decks with 0 frequency
    const filtered = {
      entries: editedField.entries.filter(e => e.pct > 0)
    }
    if (filtered.entries.length === 0) {
      alert('At least one deck must have a frequency greater than 0')
      return
    }
    onConfirm(filtered)
  }

  // Group by class for better visualization
  const decksByClass = useMemo(() => {
    const classMap = {
      'Warrior': [], 'Paladin': [], 'Hunter': [], 'Rogue': [],
      'Priest': [], 'Shaman': [], 'Mage': [], 'Warlock': [],
      'Druid': [], 'Demon Hunter': [], 'Death Knight': [], 'Other': []
    }
    
    for (const entry of sortedEntries) {
      let assigned = false
      for (const className of Object.keys(classMap)) {
        if (className !== 'Other' && entry.deck.includes(className)) {
          classMap[className].push(entry)
          assigned = true
          break
        }
      }
      if (!assigned) {
        classMap['Other'].push(entry)
      }
    }
    
    return Object.entries(classMap).filter(([, entries]) => entries.length > 0)
  }, [sortedEntries])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-hs-gold">
            Edit Field Frequencies
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Set the expected frequency of each deck in the tournament field.
            Higher values = more common.
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
            onClick={handleConfirm}
            className="px-6 py-2 bg-hs-gold hover:bg-yellow-500 text-hs-dark font-semibold rounded-lg transition-colors"
          >
            Confirm Field →
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={handleNormalize}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white transition-colors"
        >
          Normalize to 400
        </button>
        <button
          onClick={handleEqualDistribution}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white transition-colors"
        >
          Equal Distribution
        </button>
        <div className="flex-1" />
        <div className="text-right">
          <span className="text-gray-400 text-sm">Total: </span>
          <span className={`font-medium ${
            Math.abs(totalPct - 400) < 50 ? 'text-green-400' : 'text-yellow-400'
          }`}>
            {totalPct.toFixed(1)}
          </span>
          <span className="text-gray-500 text-sm"> (target: ~400)</span>
        </div>
      </div>

      {/* Field entries by class */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {decksByClass.map(([className, entries]) => (
          <div key={className} className="bg-slate-700/50 rounded-lg p-4">
            <h3 className="text-white font-medium mb-3">{className}</h3>
            <div className="space-y-2">
              {entries.map(entry => (
                <div key={entry.deck} className="flex items-center gap-2">
                  <span className="flex-1 text-gray-300 text-sm truncate" title={entry.deck}>
                    {entry.deck.replace(className, '').trim() || entry.deck}
                  </span>
                  <input
                    type="number"
                    value={entry.pct || ''}
                    onChange={(e) => handlePctChange(entry.deck, e.target.value)}
                    className="w-20 bg-slate-800 border border-slate-600 rounded px-2 py-1 text-white text-right focus:border-hs-gold focus:outline-none"
                    min={0}
                    step={1}
                    placeholder="0"
                  />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Info */}
      <div className="mt-6 p-4 bg-slate-700/30 rounded-lg">
        <p className="text-gray-400 text-sm">
          <span className="text-hs-gold font-medium">Tip:</span> The field generator creates 
          ~400 lineups based on these frequencies. Higher numbers mean the deck appears 
          in more lineups. Set to 0 to exclude a deck from the field.
        </p>
      </div>
    </div>
  )
}
