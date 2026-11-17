import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("THESPORTSDB_KEY")

if not API_KEY:
    raise RuntimeError("THESPORTSDB_KEY is missing from .env")

BASE_URL = "https://www.thesportsdb.com/api/v2/json"

HEADERS = {
    "X-API-KEY": API_KEY
}

# Leagues displayed by the /api/leagues endpoint
ALLOWED_LEAGUES = {
    "4328",  # English Premier League
    "4329",  # English League Championship
    "4331",  # German Bundesliga
    "4332",  # Italian Serie A
    "4334",  # French Ligue 1
    "4335",  # Spanish La Liga
    "4337",  # Dutch Eredivisie
    "4338",  # Belgian Pro League
    "4339",  # Turkish Super Lig
    "4344",  # Portuguese Primeira Liga
    "4346",  # American Major League Soccer
    "4429",  # FIFA World Cup
    "4480",  # UEFA Champions League
    "4481",  # UEFA Europa League
    "4565",  # FIFA Women's World Cup
    "4889",  # UEFA Women's Champions League
    "4690",  # Hungarian NB I
}

# Leagues available for match predictions
PREDICTION_LEAGUES = {
    "4328",  # English Premier League
    "4331",  # German Bundesliga
    "4332",  # Italian Serie A
    "4334",  # French Ligue 1
    "4335",  # Spanish La Liga
    "4480",  # UEFA Champions League
}