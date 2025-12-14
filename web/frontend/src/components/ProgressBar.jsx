export default function ProgressBar({ progress }) {
  const { phase, progress: progressValue, message } = progress

  const getPhaseLabel = () => {
    switch (phase) {
      case 'fetching_matchups':
        return 'Fetching Matchups'
      case 'fetching_archetypes':
        return 'Fetching Archetypes'
      case 'processing':
        return 'Processing Data'
      case 'generating_lineups':
        return 'Generating Lineups'
      case 'generating_field':
        return 'Generating Field'
      case 'calculating':
        return 'Calculating Win Rates'
      case 'finalizing':
        return 'Finalizing'
      case 'completed':
        return 'Completed'
      case 'error':
        return 'Error'
      default:
        return phase || 'Processing'
    }
  }

  const percentage = Math.round(progressValue * 100)

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm text-gray-400 mb-2">
        <span>{getPhaseLabel()}</span>
        <span>{percentage}%</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            phase === 'error' ? 'bg-red-500' : 'bg-hs-gold'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {message && (
        <p className="text-sm text-gray-400 mt-2">{message}</p>
      )}
    </div>
  )
}
