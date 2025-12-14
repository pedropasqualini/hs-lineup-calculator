# Hearthstone Lineup Calculator - Web Application

## Architecture

This web application transforms the command-line lineup calculator into an interactive web interface.

### Structure

```
web/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI routes and WebSocket endpoints
│   │   ├── config.py        # Configuration and environment variables
│   │   ├── models.py        # Pydantic models for validation
│   │   ├── crawler.py       # HSReplay API integration
│   │   └── calculator.py    # Core calculation engine
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React + Vite frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx          # Main application
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf           # Production nginx config
└── docker-compose.yml       # Container orchestration
```

## Quick Start

### Development Mode

**Backend:**
```bash
cd web/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd web/frontend
npm install
npm run dev
```

Access at http://localhost:5173

### Production Mode (Docker)

```bash
cd web
# Optional: Set HSReplay cookies for premium features
export COOKIES='your_hsreplay_cookies_here'

docker-compose up --build
```

Access at http://localhost

## Key Design Decisions

### 1. WebSocket for Long-Running Operations

The crawler and calculator can take significant time. Instead of HTTP requests that could timeout, we use WebSockets to:
- Stream real-time progress updates
- Allow the UI to show detailed progress bars
- Handle long calculations without connection issues

### 2. Preserved Algorithm Integrity

The calculation engine (`calculator.py`) preserves the EXACT algorithms from the original:
- **Lemke-Howson algorithm** for Nash equilibrium in ban phase
- **Conquest Bo5 probability calculation** with all game states
- **Field generation** using iterative bell-curve approximation

No mathematical changes were made - only structural refactoring for web integration.

### 3. Editable Matchups

Users can now:
1. Fetch data from HSReplay with custom filters
2. Edit any matchup value in the matrix
3. See color-coded cells (favorable/unfavorable)
4. View average win rates per deck

This allows for:
- Correcting perceived errors in HSReplay data
- Adjusting for local meta differences
- Testing "what if" scenarios

### 4. Flexible Field Configuration

The field editor:
- Shows all decks grouped by class
- Allows manual frequency adjustment
- Has quick actions for normalization
- Validates that deck names match the matchup matrix

### 5. Class Detection from Deck Names

Deck names MUST include the class name (e.g., "Control Warrior", "Aggro Demon Hunter"). This is consistent with HSReplay naming and enables:
- Lineup validation (4 different classes required)
- Visual class coloring in results
- Proper grouping in the field editor

## API Endpoints

### REST

- `GET /` - Health check
- `GET /api/options` - Get available crawler options
- `POST /api/upload/matchups` - Upload matchups CSV
- `POST /api/upload/field` - Upload field CSV

### WebSocket

- `WS /ws/crawl` - Crawl HSReplay with progress
- `WS /ws/calculate` - Calculate lineups with progress

## Performance Considerations

- The calculator uses Python's multiprocessing for parallel lineup evaluation
- Field generation runs in a separate thread to not block the event loop
- Frontend limits results display to top 100 for responsiveness
- Progress updates are throttled to prevent message flooding

## Limitations

- Currently only supports Conquest Bo5 with ban format
- Requires deck names to include class names
- No authentication/user accounts (single-user design)
- Calculation time scales with deck count and field size
