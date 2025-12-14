import os
from dotenv import load_dotenv

########## Configuration setup ##########
# Uses .env file for request cookies if you have a premium account for advanced filters. 
load_dotenv()
COOKIES = os.getenv("COOKIES")
# LEAGUE_RANK_RANGE = "TOP_1000_LEGEND"
LEAGUE_RANK_RANGE = "BRONZE_THROUGH_GOLD"  # Standard filter without premium account
GAME_TYPE = "RANKED_STANDARD"
REGION  = "ALL"
TIME_RANGE = "LAST_7_DAYS"
# Will ignore decks that don't match the minimum number of games.
# Should aim for about ~20 archetypes for a great analysis without taking too much time.
MIN_GAMES = 30_000

########## Manual input ##########
# matchups csv file should be deck names exactly written as HSReplay and matchup percentages
# field csv file should be deck names exactly written as HSReplay and field frequencies
# Without user input, it'll use decks from HSReplay
USER_INPUT = False
MATCHUPS_PATH = "data/matchups_example.csv"
FIELD_PATH = "data/field_example.csv"
OUTPUT_PATH = "data/output.csv"

########## Artificial field configurations ##########
# Lower random target means artificial field will not be close to bell curve.
# The more iteractions, the closer it should be to bell curve for a perfect field.
# It could theoretically get into some undesirable outcomes (valleys), but >99% of the time it seems to work pretty well.
RANDOM_TARGET = 40
NUM_ITERACTIONS = 2_000
