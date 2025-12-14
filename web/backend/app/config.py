"""
Configuration for the backend server.
Loads environment variables and provides default values.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# HSReplay API Configuration
COOKIES = os.getenv("COOKIES", "")

# Default crawler options
DEFAULT_LEAGUE_RANK_RANGE = "BRONZE_THROUGH_GOLD"
DEFAULT_GAME_TYPE = "RANKED_STANDARD"
DEFAULT_REGION = "ALL"
DEFAULT_TIME_RANGE = "CURRENT_PATCH"
DEFAULT_MIN_GAMES = 10000

# Field generation configuration
RANDOM_TARGET = 40
NUM_ITERATIONS = 2000

# Available options for the UI
LEAGUE_RANK_OPTIONS = [
    {"value": "BRONZE_THROUGH_GOLD", "label": "Bronze through Gold"},
    {"value": "PLATINUM_THROUGH_DIAMOND", "label": "Platinum through Diamond"},
    {"value": "TOP_1000_LEGEND", "label": "Top 1000 Legend"},
    {"value": "LEGEND", "label": "Legend"},
]

GAME_TYPE_OPTIONS = [
    {"value": "RANKED_STANDARD", "label": "Ranked Standard"},
    {"value": "RANKED_WILD", "label": "Ranked Wild"},
]

REGION_OPTIONS = [
    {"value": "ALL", "label": "All Regions"},
    {"value": "REGION_US", "label": "Americas"},
    {"value": "REGION_EU", "label": "Europe"},
    {"value": "REGION_KR", "label": "Asia"},
]

TIME_RANGE_OPTIONS = [
    {"value": "LAST_7_DAYS", "label": "Last 7 Days"},
    {"value": "LAST_3_DAYS", "label": "Last 3 Days"},
    {"value": "LAST_1_DAY", "label": "Last 1 Day"},
]
