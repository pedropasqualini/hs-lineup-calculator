"""
FastAPI main application.
Provides REST API and WebSocket endpoints for the lineup calculator.
"""
import asyncio
import json
import io
import csv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd

from .config import (
    LEAGUE_RANK_OPTIONS,
    GAME_TYPE_OPTIONS,
    REGION_OPTIONS,
    TIME_RANGE_OPTIONS,
    DEFAULT_LEAGUE_RANK_RANGE,
    DEFAULT_GAME_TYPE,
    DEFAULT_REGION,
    DEFAULT_TIME_RANGE,
    DEFAULT_MIN_GAMES,
)
from .models import (
    CrawlerOptions,
    MatchupMatrix,
    FieldData,
    FieldEntry,
    CalculateRequest,
    LineupResult,
)
from .crawler import crawl_data, get_class_archetypes, possible_lineups
from .calculator import generate_field, calculate_lineups

app = FastAPI(
    title="Hearthstone Lineup Calculator",
    description="Calculate optimal deck lineups for Hearthstone tournaments",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Hearthstone Lineup Calculator API"}


@app.get("/api/options")
async def get_options():
    """Get available crawler options for the UI."""
    return {
        "league_rank_range": LEAGUE_RANK_OPTIONS,
        "game_type": GAME_TYPE_OPTIONS,
        "region": REGION_OPTIONS,
        "time_range": TIME_RANGE_OPTIONS,
        "defaults": {
            "league_rank_range": DEFAULT_LEAGUE_RANK_RANGE,
            "game_type": DEFAULT_GAME_TYPE,
            "region": DEFAULT_REGION,
            "time_range": DEFAULT_TIME_RANGE,
            "min_games": DEFAULT_MIN_GAMES,
        }
    }


@app.post("/api/upload/matchups")
async def upload_matchups(file: UploadFile = File(...)):
    """
    Upload a matchups CSV file.
    Expected format: deck names as row/column headers, percentages as values.
    """
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(decoded), index_col=0)
        
        # Validate it's a square matrix
        if len(df.index) != len(df.columns):
            raise HTTPException(status_code=400, detail="Matchup matrix must be square")
        
        # Validate all values are numeric
        if not df.apply(lambda x: pd.to_numeric(x, errors='coerce')).notna().all().all():
            raise HTTPException(status_code=400, detail="All matchup values must be numeric")
        
        deck_names = df.index.tolist()
        values = df.values.tolist()
        
        return {
            "success": True,
            "matchups": {
                "deck_names": deck_names,
                "values": values
            }
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")


@app.post("/api/upload/field")
async def upload_field(file: UploadFile = File(...)):
    """
    Upload a field CSV file.
    Expected format: deck column and pct column.
    """
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(decoded), index_col=0)
        
        if 'pct' not in df.columns:
            raise HTTPException(status_code=400, detail="Field CSV must have 'pct' column")
        
        entries = [
            {"deck": str(deck), "pct": float(pct)}
            for deck, pct in df['pct'].items()
        ]
        
        return {
            "success": True,
            "field": {"entries": entries}
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")


@app.websocket("/ws/crawl")
async def websocket_crawl(websocket: WebSocket):
    """
    WebSocket endpoint for crawling HSReplay data with progress updates.
    """
    await websocket.accept()
    
    try:
        # Receive crawler options
        data = await websocket.receive_json()
        options = CrawlerOptions(**data)
        
        async def send_progress(phase: str, progress: float, message: str):
            await websocket.send_json({
                "phase": phase,
                "progress": progress,
                "message": message,
                "completed": False
            })
        
        # Run crawler in thread pool to not block
        loop = asyncio.get_event_loop()
        
        # Progress tracking with asyncio
        progress_queue = asyncio.Queue()
        
        def sync_progress_callback(phase: str, progress: float, message: str):
            # Put progress in queue (sync -> async bridge)
            asyncio.run_coroutine_threadsafe(
                progress_queue.put((phase, progress, message)),
                loop
            )
        
        # Start crawler in executor
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                crawl_data,
                options.league_rank_range,
                options.game_type,
                options.region,
                options.time_range,
                options.min_games,
                sync_progress_callback
            )
            
            # Send progress updates while waiting
            while not future.done():
                try:
                    phase, progress, message = await asyncio.wait_for(
                        progress_queue.get(),
                        timeout=0.1
                    )
                    await send_progress(phase, progress, message)
                except asyncio.TimeoutError:
                    continue
            
            # Get result
            matchups, deck_pct, archetypes, lineups = future.result()
        
        # Convert to response format
        deck_names = matchups.columns.tolist()
        matchup_values = matchups.values.tolist()
        
        field_entries = [
            {"deck": str(deck), "pct": float(pct)}
            for deck, pct in deck_pct.items()
        ]
        
        await websocket.send_json({
            "phase": "completed",
            "progress": 1.0,
            "message": f"Done! Found {len(deck_names)} decks, {len(lineups)} possible lineups",
            "completed": True,
            "matchups": {
                "deck_names": deck_names,
                "values": matchup_values
            },
            "field": {"entries": field_entries}
        })
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "phase": "error",
            "progress": 0,
            "message": str(e),
            "completed": True,
            "error": str(e)
        })
    finally:
        await websocket.close()


@app.websocket("/ws/calculate")
async def websocket_calculate(websocket: WebSocket):
    """
    WebSocket endpoint for calculating optimal lineups with progress updates.
    """
    await websocket.accept()
    
    try:
        # Receive calculation request
        data = await websocket.receive_json()
        
        matchups_data = data.get("matchups", {})
        field_data = data.get("field", {})
        
        deck_names = matchups_data.get("deck_names", [])
        matchup_values = matchups_data.get("values", [])
        field_entries = field_data.get("entries", [])
        
        if not deck_names or not matchup_values or not field_entries:
            await websocket.send_json({
                "phase": "error",
                "progress": 0,
                "message": "Missing matchups or field data",
                "completed": True,
                "error": "Missing matchups or field data"
            })
            return
        
        async def send_progress(phase: str, progress: float, message: str):
            await websocket.send_json({
                "phase": phase,
                "progress": progress,
                "message": message,
                "completed": False
            })
        
        loop = asyncio.get_event_loop()
        
        # Create DataFrames from input
        matchups_df = pd.DataFrame(
            matchup_values,
            index=deck_names,
            columns=deck_names
        )
        
        # Create archetypes DataFrame
        # We need to infer class from deck name (HSReplay convention)
        # For now, we'll create a simple structure
        archetypes_data = []
        class_map = {
            'Warrior': 'WARRIOR', 'Paladin': 'PALADIN', 'Hunter': 'HUNTER',
            'Rogue': 'ROGUE', 'Priest': 'PRIEST', 'Shaman': 'SHAMAN',
            'Mage': 'MAGE', 'Warlock': 'WARLOCK', 'Druid': 'DRUID',
            'Demon Hunter': 'DEMONHUNTER', 'Death Knight': 'DEATHKNIGHT'
        }
        
        for i, name in enumerate(deck_names):
            player_class = 'UNKNOWN'
            for class_name, class_code in class_map.items():
                if class_name in name:
                    player_class = class_code
                    break
            archetypes_data.append({
                'id': i,
                'name': name,
                'player_class_name': player_class
            })
        
        archetypes_df = pd.DataFrame(archetypes_data)
        
        # Validate we have at least 4 different classes
        unique_classes = archetypes_df['player_class_name'].nunique()
        if unique_classes < 4:
            await websocket.send_json({
                "phase": "error",
                "progress": 0,
                "message": f"Need at least 4 different classes, found {unique_classes}. Make sure deck names include the class name (e.g., 'Control Warrior').",
                "completed": True,
                "error": "Insufficient classes"
            })
            return
        
        # Create deck_pct Series
        deck_pct = pd.Series(
            {entry["deck"]: entry["pct"] for entry in field_entries}
        )
        
        # Generate lineups
        await send_progress("generating_lineups", 0.05, "Generating possible lineups...")
        
        classes = get_class_archetypes(archetypes_df)
        lineups = possible_lineups(classes)
        
        await send_progress("generating_field", 0.1, f"Found {len(lineups)} possible lineups. Generating field...")
        
        # Generate field with progress
        progress_queue = asyncio.Queue()
        
        def field_progress_callback(progress: float, message: str):
            asyncio.run_coroutine_threadsafe(
                progress_queue.put(("generating_field", 0.1 + progress * 0.3, message)),
                loop
            )
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                generate_field,
                deck_pct,
                lineups,
                field_progress_callback
            )
            
            while not future.done():
                try:
                    phase, progress, message = await asyncio.wait_for(
                        progress_queue.get(),
                        timeout=0.1
                    )
                    await send_progress(phase, progress, message)
                except asyncio.TimeoutError:
                    continue
            
            field = future.result()
        
        await send_progress("calculating", 0.4, f"Field generated with {len(field)} lineups. Calculating win rates...")
        
        # Calculate lineups with progress
        def calc_progress_callback(progress: float, message: str):
            asyncio.run_coroutine_threadsafe(
                progress_queue.put(("calculating", 0.4 + progress * 0.55, message)),
                loop
            )
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(
                calculate_lineups,
                matchups_df,
                field,
                lineups,
                archetypes_df,
                calc_progress_callback
            )
            
            while not future.done():
                try:
                    phase, progress, message = await asyncio.wait_for(
                        progress_queue.get(),
                        timeout=0.5
                    )
                    await send_progress(phase, progress, message)
                except asyncio.TimeoutError:
                    continue
            
            results_df = future.result()
        
        await send_progress("finalizing", 0.98, "Preparing results...")
        
        # Convert results to response format
        # Results DataFrame has deck names in columns 0-3 and win_rate in column 4
        results = []
        
        for _, row in results_df.head(100).iterrows():  # Return top 100
            decks = [str(row[i]) for i in range(4)]
            results.append({
                "decks": decks,
                "win_rate": float(row[4])
            })
        
        await websocket.send_json({
            "phase": "completed",
            "progress": 1.0,
            "message": f"Done! Calculated {len(results_df)} lineups",
            "completed": True,
            "results": results
        })
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
        await websocket.send_json({
            "phase": "error",
            "progress": 0,
            "message": str(e),
            "completed": True,
            "error": str(e)
        })
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
