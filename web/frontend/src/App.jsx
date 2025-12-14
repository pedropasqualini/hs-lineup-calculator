import { useState } from 'react'
import DataSourceStep from './components/DataSourceStep'
import MatchupsEditor from './components/MatchupsEditor'
import FieldEditor from './components/FieldEditor'
import CalculateStep from './components/CalculateStep'
import Results from './components/Results'
import ProgressBar from './components/ProgressBar'

const STEPS = {
  DATA_SOURCE: 0,
  MATCHUPS: 1,
  FIELD: 2,
  CALCULATE: 3,
  RESULTS: 4,
}

function App() {
  const [currentStep, setCurrentStep] = useState(STEPS.DATA_SOURCE)
  const [matchups, setMatchups] = useState(null)
  const [field, setField] = useState(null)
  const [results, setResults] = useState(null)
  const [progress, setProgress] = useState({ phase: '', progress: 0, message: '' })
  const [isLoading, setIsLoading] = useState(false)

  const stepNames = ['Data Source', 'Matchups', 'Field', 'Calculate', 'Results']

  const goToStep = (step) => {
    if (step <= currentStep || (step === currentStep + 1 && canProceed())) {
      setCurrentStep(step)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case STEPS.DATA_SOURCE:
        return matchups !== null
      case STEPS.MATCHUPS:
        return matchups !== null
      case STEPS.FIELD:
        return field !== null
      case STEPS.CALCULATE:
        return results !== null
      default:
        return true
    }
  }

  const handleDataLoaded = (loadedMatchups, loadedField) => {
    setMatchups(loadedMatchups)
    setField(loadedField)
    setCurrentStep(STEPS.MATCHUPS)
  }

  const handleMatchupsConfirmed = (confirmedMatchups) => {
    setMatchups(confirmedMatchups)
    setCurrentStep(STEPS.FIELD)
  }

  const handleFieldConfirmed = (confirmedField) => {
    setField(confirmedField)
    setCurrentStep(STEPS.CALCULATE)
  }

  const handleCalculationComplete = (calculatedResults) => {
    setResults(calculatedResults)
    setCurrentStep(STEPS.RESULTS)
  }

  const handleReset = () => {
    setCurrentStep(STEPS.DATA_SOURCE)
    setMatchups(null)
    setField(null)
    setResults(null)
    setProgress({ phase: '', progress: 0, message: '' })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-hs-dark via-slate-900 to-hs-dark text-white">
      {/* Header */}
      <header className="border-b border-hs-brown/30 bg-hs-dark/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-hs-gold">
              ⚔️ Hearthstone Lineup Calculator
            </h1>
            <button
              onClick={handleReset}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              Start Over
            </button>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-center mb-8">
          {stepNames.map((name, index) => (
            <div key={index} className="flex items-center">
              <button
                onClick={() => goToStep(index)}
                className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium transition-all ${
                  index === currentStep
                    ? 'bg-hs-gold text-hs-dark'
                    : index < currentStep
                    ? 'bg-green-600 text-white cursor-pointer hover:bg-green-500'
                    : 'bg-gray-700 text-gray-400'
                }`}
              >
                {index < currentStep ? '✓' : index + 1}
              </button>
              <span
                className={`ml-2 text-sm ${
                  index === currentStep ? 'text-hs-gold' : 'text-gray-400'
                }`}
              >
                {name}
              </span>
              {index < stepNames.length - 1 && (
                <div
                  className={`w-12 h-0.5 mx-4 ${
                    index < currentStep ? 'bg-green-600' : 'bg-gray-700'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Progress bar for async operations */}
        {isLoading && (
          <div className="mb-6">
            <ProgressBar progress={progress} />
          </div>
        )}

        {/* Step Content */}
        <main className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          {currentStep === STEPS.DATA_SOURCE && (
            <DataSourceStep
              onDataLoaded={handleDataLoaded}
              setProgress={setProgress}
              setIsLoading={setIsLoading}
            />
          )}
          {currentStep === STEPS.MATCHUPS && (
            <MatchupsEditor
              matchups={matchups}
              onConfirm={handleMatchupsConfirmed}
              onBack={() => setCurrentStep(STEPS.DATA_SOURCE)}
            />
          )}
          {currentStep === STEPS.FIELD && (
            <FieldEditor
              field={field}
              deckNames={matchups?.deck_names || []}
              onConfirm={handleFieldConfirmed}
              onBack={() => setCurrentStep(STEPS.MATCHUPS)}
            />
          )}
          {currentStep === STEPS.CALCULATE && (
            <CalculateStep
              matchups={matchups}
              field={field}
              onComplete={handleCalculationComplete}
              onBack={() => setCurrentStep(STEPS.FIELD)}
              setProgress={setProgress}
              setIsLoading={setIsLoading}
            />
          )}
          {currentStep === STEPS.RESULTS && (
            <Results
              results={results}
              onBack={() => setCurrentStep(STEPS.CALCULATE)}
              onReset={handleReset}
            />
          )}
        </main>

        {/* Footer */}
        <footer className="mt-8 text-center text-gray-500 text-sm">
          <p>
            Conquest Bo5 with Ban • Game Theory Optimal Lineups
          </p>
          <p className="mt-1">
            Built for champions, by champions 🏆
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
