from curl_cffi import requests
import pandas as pd
import math
import itertools
from tqdm import tqdm
from loguru import logger
from configuration import COOKIES, LEAGUE_RANK_RANGE, GAME_TYPE, REGION, TIME_RANGE, MIN_GAMES, MATCHUPS_PATH, FIELD_PATH, USER_INPUT

logger.remove()
logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)

# Headers to mimic a real browser (bypass Cloudflare)
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def request_matchup_stats():
    url = "https://hsreplay.net/analytics/query/head_to_head_archetype_matchups_v2/"
    querystring = {
        "GameType":GAME_TYPE,
        "LeagueRankRange":LEAGUE_RANK_RANGE,
        "Region":REGION,
        "TimeRange":TIME_RANGE,
    }
    headers = DEFAULT_HEADERS.copy()
    if COOKIES:
        headers["cookie"] = COOKIES
    response = requests.get(url, headers=headers, params=querystring, impersonate="chrome110")
    if response.status_code != 200:
        logger.error(f"Request matchup data got status code {response.status_code}")
        logger.error(f"Response: {response.text}")
        exit(1)
    struct = response.json()

    return struct

def request_archetypes():
    url = "https://hsreplay.net/api/v1/archetypes/?format=json"
    headers = DEFAULT_HEADERS.copy()
    headers["format"] = "json"
    response = requests.get(url, headers=headers, impersonate="chrome110")
    if response.status_code != 200:
        logger.error(f"Request archetype data got status code {response.status_code}")
        logger.error(f"Response: {response.text}")
        exit(1)
    struct = response.json()
    return struct

def struct_to_dataframe(struct):
    data = pd.DataFrame(struct['series']['data'])
    data.index = data.index.astype(int)
    data.columns = data.columns.astype(int)
    data = data.drop(data[data.index < 0].index)
    data = data.drop(data.loc[:, data.columns < 0].columns, axis=1)
    return data

def filter_field(element, field):
    if type(element) is float:
        return math.nan
    else:
        return element[field]

def get_class_archetypes(archetypes):
    return archetypes.groupby('player_class_name')['name'].apply(list).to_dict()
    
def possible_lineups(classes):
    all_classes = [c for c in classes.keys()]
    lineups = []
    combos = list(itertools.combinations(all_classes, 4))
    for combo in combos:
        for lineup in itertools.product(*(classes[c] for c in combo)):
            lineups.append(list(lineup))
    return lineups

def get_user_input(archetypes):
    matchups = pd.read_csv(MATCHUPS_PATH, index_col=0)
    archetypes = archetypes[archetypes['name'].isin(matchups.index)]
    matchups = matchups.loc[archetypes['name'], archetypes['name']]
    deck_pct = pd.read_csv(FIELD_PATH, index_col=0)['pct'].sort_values(ascending=False)
    return matchups, archetypes, deck_pct

def request_all_data():
    matchup_data = struct_to_dataframe(request_matchup_stats())
    archetypes = pd.DataFrame(request_archetypes())
    archetypes = archetypes[(archetypes['player_class_name'] != 'WHIZBANG') & (archetypes['player_class_name'] != 'NEUTRAL')]
    archetypes = archetypes[["id", "name", "player_class_name"]]
    
    id_to_name = archetypes[['id', 'name']].set_index('id', drop=True).to_dict()['name']
    matchup_data = matchup_data.rename(mapper=id_to_name, axis=0)
    matchup_data = matchup_data.rename(mapper=id_to_name, axis=1)
    
    total_games = matchup_data.copy()
    for column in matchup_data.columns:
        matchup_data[column] = matchup_data[column].apply(filter_field, field="win_rate")
    for column in total_games.columns:
        total_games[column] = total_games[column].apply(filter_field, field="total_games")
    
    archetypes = archetypes[archetypes['name'].isin(total_games.sum()[total_games.sum() > MIN_GAMES].index)]
    archetypes = archetypes.sort_values(["player_class_name", "name"])

    ## Using input
    if USER_INPUT:
        matchups, archetypes, deck_pct = get_user_input(archetypes)
    ## Using HSR
    else:
        matchups = matchup_data.loc[archetypes['name'], archetypes['name']].T
        total_games_refined = total_games.sum().loc[archetypes['name']].astype(int)
        deck_pct = (total_games_refined / total_games_refined.sum() * 400).sort_values(ascending=False)

    archetypes = archetypes.reset_index(drop=True)
    logger.info(f"Analyzing decks with minimum of {MIN_GAMES} games.")
    logger.info(f"Got {len(archetypes)} decks.")
    classes = get_class_archetypes(archetypes)
    lineups = possible_lineups(classes)
    logger.info(f"Got {len(lineups)} possible lineups.")
    return matchups, lineups, deck_pct, archetypes
    
## DEBUG
def main():
    matchups, lineups, deck_pct, archetypes = request_all_data()
    print("Matchups:")
    print(matchups[:5])
    print("Lineups:")
    print(lineups[:5])
    print("Field:")
    print(deck_pct[:5])
    print("Archetypes:")
    print(archetypes[:5])

if __name__ == '__main__':
    main()
    