"""
HSReplay API crawler module.
Fetches matchup data and archetypes from HSReplay.
"""
from curl_cffi import requests
import pandas as pd
import math
import itertools
from typing import Callable, Optional

from .config import COOKIES

# Headers to mimic a real browser (bypass Cloudflare)
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}


def request_matchup_stats(
    league_rank_range: str,
    game_type: str,
    region: str,
    time_range: str,
    cookies: Optional[str] = None
) -> dict:
    """Fetch matchup statistics from HSReplay API."""
    url = "https://hsreplay.net/analytics/query/head_to_head_archetype_matchups_v2/"
    querystring = {
        "GameType": game_type,
        "LeagueRankRange": league_rank_range,
        "Region": region,
        "TimeRange": time_range,
    }
    headers = DEFAULT_HEADERS.copy()
    if cookies or COOKIES:
        headers["cookie"] = cookies or COOKIES
    
    response = requests.get(url, headers=headers, params=querystring, impersonate="chrome110")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch matchup data: {response.status_code} - {response.text}")
    
    return response.json()


def request_archetypes() -> list:
    """Fetch archetype data from HSReplay API."""
    url = "https://hsreplay.net/api/v1/archetypes/?format=json"
    headers = DEFAULT_HEADERS.copy()
    headers["format"] = "json"
    
    response = requests.get(url, headers=headers, impersonate="chrome110")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch archetype data: {response.status_code} - {response.text}")
    
    return response.json()


def struct_to_dataframe(struct: dict) -> pd.DataFrame:
    """Convert HSReplay JSON structure to pandas DataFrame."""
    data = pd.DataFrame(struct['series']['data'])
    data.index = data.index.astype(int)
    data.columns = data.columns.astype(int)
    data = data.drop(data[data.index < 0].index)
    data = data.drop(data.loc[:, data.columns < 0].columns, axis=1)
    return data


def filter_field(element, field: str):
    """Extract specific field from HSReplay data element."""
    if isinstance(element, float):
        return math.nan
    else:
        return element[field]


def get_class_archetypes(archetypes: pd.DataFrame) -> dict:
    """Group archetypes by player class."""
    return archetypes.groupby('player_class_name')['name'].apply(list).to_dict()


def possible_lineups(classes: dict) -> list:
    """Generate all possible 4-deck lineups (one per class)."""
    all_classes = [c for c in classes.keys()]
    lineups = []
    combos = list(itertools.combinations(all_classes, 4))
    for combo in combos:
        for lineup in itertools.product(*(classes[c] for c in combo)):
            lineups.append(list(lineup))
    return lineups


def crawl_data(
    league_rank_range: str,
    game_type: str,
    region: str,
    time_range: str,
    min_games: int,
    progress_callback: Optional[Callable[[str, float, str], None]] = None
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, list]:
    """
    Crawl all data from HSReplay.
    
    Args:
        league_rank_range: Rank filter
        game_type: Game type filter
        region: Region filter
        time_range: Time range filter
        min_games: Minimum games threshold
        progress_callback: Optional callback(phase, progress, message)
    
    Returns:
        Tuple of (matchups, deck_pct, archetypes, lineups)
    """
    if progress_callback:
        progress_callback("fetching_matchups", 0.1, "Fetching matchup data from HSReplay...")
    
    matchup_data = struct_to_dataframe(request_matchup_stats(
        league_rank_range, game_type, region, time_range
    ))
    
    if progress_callback:
        progress_callback("fetching_archetypes", 0.3, "Fetching archetype data...")
    
    archetypes = pd.DataFrame(request_archetypes())
    archetypes = archetypes[
        (archetypes['player_class_name'] != 'WHIZBANG') & 
        (archetypes['player_class_name'] != 'NEUTRAL')
    ]
    archetypes = archetypes[["id", "name", "player_class_name"]]
    
    if progress_callback:
        progress_callback("processing", 0.5, "Processing matchup data...")
    
    id_to_name = archetypes[['id', 'name']].set_index('id', drop=True).to_dict()['name']
    matchup_data = matchup_data.rename(mapper=id_to_name, axis=0)
    matchup_data = matchup_data.rename(mapper=id_to_name, axis=1)
    
    total_games = matchup_data.copy()
    for column in matchup_data.columns:
        matchup_data[column] = matchup_data[column].apply(filter_field, field="win_rate")
    for column in total_games.columns:
        total_games[column] = total_games[column].apply(filter_field, field="total_games")
    
    if progress_callback:
        progress_callback("processing", 0.7, "Filtering by minimum games...")
    
    archetypes = archetypes[
        archetypes['name'].isin(total_games.sum()[total_games.sum() > min_games].index)
    ]
    archetypes = archetypes.sort_values(["player_class_name", "name"])
    
    matchups = matchup_data.loc[archetypes['name'], archetypes['name']].T
    total_games_refined = total_games.sum().loc[archetypes['name']].astype(int)
    deck_pct = (total_games_refined / total_games_refined.sum() * 400).sort_values(ascending=False)
    
    archetypes = archetypes.reset_index(drop=True)
    
    if progress_callback:
        progress_callback("processing", 0.9, f"Found {len(archetypes)} decks, generating lineups...")
    
    classes = get_class_archetypes(archetypes)
    lineups = possible_lineups(classes)
    
    if progress_callback:
        progress_callback("completed", 1.0, f"Done! {len(archetypes)} decks, {len(lineups)} possible lineups")
    
    return matchups, deck_pct, archetypes, lineups
