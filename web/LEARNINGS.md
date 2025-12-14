# Development Learnings & Notes

This document captures key insights from developing the web interface for the Hearthstone Lineup Calculator.

## Algorithm Understanding

### Conquest Bo5 Probability Calculation

The `conquest_bo5` function calculates the exact probability of winning a Best of 5 Conquest match after bans are determined. It uses dynamic programming concepts:

1. **State Variables**: A, B, C represent hero deck contributions; D, E, F represent villain deck contributions
2. **Game Progression**: Variables like AB, ABC, ABCD track cumulative probabilities through game states
3. **Final Calculation**: Sums all winning terminal states (3 wins before opponent gets 3)

The formula accounts for all possible game sequences and deck selections, assuming random deck choice when multiple options exist.

### Lemke-Howson Algorithm

The `solve` function implements a fictitious play variant of Nash equilibrium finding:

1. Players alternate "best responses" to cumulative opponent strategies
2. Converges to Nash equilibrium over iterations
3. Returns the value of the game (expected win rate with optimal play from both sides)

This is used during the ban phase to determine optimal ban strategies.

### Field Generation

The artificial field generator creates ~400 lineups based on deck frequencies:

1. Each deck has a target representation based on its frequency
2. Lineups are randomly adjusted to match targets
3. The process iterates to approximate a realistic tournament field

The `RANDOM_TARGET` parameter (default 40) controls how strictly the distribution is enforced.

## Web Development Decisions

### Why FastAPI + React?

- **FastAPI**: Async support, built-in WebSocket, automatic OpenAPI docs, type validation
- **React**: Component reusability, state management, rich ecosystem
- **Vite**: Fast HMR during development, optimized production builds

### WebSocket Protocol Design

Messages follow a consistent structure:
```json
{
  "phase": "string",
  "progress": 0.0-1.0,
  "message": "human readable status",
  "completed": false,
  "data": {}  // phase-specific data
}
```

This allows the frontend to:
- Show phase-specific UI
- Display accurate progress bars
- Handle completion/error states uniformly

### Multiprocessing in Async Context

The calculation uses Python's multiprocessing Pool, which doesn't play directly with asyncio. Solution:

1. Run the Pool in a ThreadPoolExecutor
2. Use an asyncio Queue to bridge sync callbacks to async
3. Poll the queue with timeouts to send WebSocket updates

This maintains responsiveness while leveraging all CPU cores.

## UI/UX Insights

### Step-Based Flow

Breaking the process into discrete steps (Data → Matchups → Field → Calculate → Results) provides:
- Clear user mental model
- Ability to go back and edit
- Progress persistence across steps

### Color-Coded Matchups

Visual feedback (green/red/gray) immediately shows favorable vs unfavorable matchups, making large matrices scannable.

### Class Grouping

Grouping decks by class in the field editor reduces cognitive load and matches how players think about lineups.

## Potential Improvements

1. **Caching**: Store crawled data for reuse
2. **Presets**: Save/load field configurations
3. **Comparison**: Compare multiple lineups side-by-side
4. **Simulation**: Monte Carlo simulation against specific opponent lineups
5. **Authentication**: Multi-user support with saved calculations
6. **Other Formats**: Last Hero Standing, Bo7, specialized formats

## Testing Notes

When testing the application:

1. Start with a small MIN_GAMES value to get fewer decks (faster testing)
2. Use the example CSVs in `data/` as reference for manual upload format
3. Check that deck names include class names (e.g., "Control Warrior" not just "Control")
4. The calculation can take 30-60 seconds with ~20 decks; be patient
