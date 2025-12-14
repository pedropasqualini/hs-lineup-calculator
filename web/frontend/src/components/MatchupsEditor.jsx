import { useState, useMemo } from 'react'

export default function MatchupsEditor({ matchups, onConfirm, onBack }) {
  const [editedMatchups, setEditedMatchups] = useState(matchups)
  const [hoveredCell, setHoveredCell] = useState(null)

  const deckNames = editedMatchups.deck_names
  const values = editedMatchups.values

  const handleCellChange = (rowIdx, colIdx, value) => {
    const newValues = [...values.map(row => [...row])]
    const numValue = parseFloat(value) || 0
    newValues[rowIdx][colIdx] = Math.min(100, Math.max(0, numValue))
    
    // Optionally mirror the matchup (100 - value for opponent)
    // This is disabled by default as users may have asymmetric data
    // newValues[colIdx][rowIdx] = 100 - numValue
    
    setEditedMatchups({
      ...editedMatchups,
      values: newValues,
    })
  }

  const getCellClass = (value) => {
    if (value >= 55) return 'matchup-favorable'
    if (value <= 45) return 'matchup-unfavorable'
    return 'matchup-even'
  }

  const handleConfirm = () => {
    onConfirm(editedMatchups)
  }

  // Calculate average matchup for each deck
  const deckAverages = useMemo(() => {
    return deckNames.map((_, rowIdx) => {
      const sum = values[rowIdx].reduce((acc, val, colIdx) => {
        if (rowIdx === colIdx) return acc // Skip mirror matchup
        return acc + (val || 50)
      }, 0)
      return sum / (deckNames.length - 1)
    })
  }, [deckNames, values])

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-hs-gold">
            Edit Matchups
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Click any cell to edit. Values are win percentages (0-100).
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
            Confirm Matchups →
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex gap-6 mb-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded matchup-favorable" />
          <span className="text-gray-400">Favorable (≥55%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded matchup-even" />
          <span className="text-gray-400">Even (45-55%)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded matchup-unfavorable" />
          <span className="text-gray-400">Unfavorable (≤45%)</span>
        </div>
      </div>

      {/* Matchup Matrix */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th className="p-2 text-left text-gray-400 sticky left-0 bg-slate-800 z-10">
                Deck
              </th>
              <th className="p-2 text-center text-gray-400 w-12">Avg</th>
              {deckNames.map((name, idx) => (
                <th
                  key={idx}
                  className="p-2 text-center text-gray-300 min-w-[60px] max-w-[100px] truncate"
                  title={name}
                >
                  <span className="block truncate text-xs">{name}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {deckNames.map((rowName, rowIdx) => (
              <tr key={rowIdx} className="border-t border-slate-700">
                <td className="p-2 text-gray-300 sticky left-0 bg-slate-800 z-10 max-w-[150px] truncate" title={rowName}>
                  {rowName}
                </td>
                <td className="p-2 text-center text-gray-400 font-medium">
                  {deckAverages[rowIdx].toFixed(1)}%
                </td>
                {deckNames.map((_, colIdx) => (
                  <td
                    key={colIdx}
                    className={`p-1 text-center ${
                      rowIdx === colIdx ? 'bg-slate-900' : getCellClass(values[rowIdx][colIdx])
                    }`}
                    onMouseEnter={() => setHoveredCell({ row: rowIdx, col: colIdx })}
                    onMouseLeave={() => setHoveredCell(null)}
                  >
                    {rowIdx === colIdx ? (
                      <span className="text-gray-600">-</span>
                    ) : (
                      <input
                        type="number"
                        value={values[rowIdx][colIdx] || ''}
                        onChange={(e) => handleCellChange(rowIdx, colIdx, e.target.value)}
                        className="w-12 bg-transparent text-center text-white focus:bg-slate-700 focus:outline-none rounded"
                        min={0}
                        max={100}
                      />
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Hovered cell info */}
      {hoveredCell && hoveredCell.row !== hoveredCell.col && (
        <div className="fixed bottom-4 right-4 bg-slate-800 border border-slate-600 rounded-lg p-4 shadow-lg">
          <p className="text-white font-medium">
            {deckNames[hoveredCell.row]} vs {deckNames[hoveredCell.col]}
          </p>
          <p className="text-hs-gold text-lg">
            {values[hoveredCell.row][hoveredCell.col]}%
          </p>
        </div>
      )}
    </div>
  )
}
