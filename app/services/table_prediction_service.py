import requests
from app.core.config import BASE_URL


def fetch_current_table(league_id: str):
    url = f"{BASE_URL}/lookuptable.php?l={league_id}"
    resp = requests.get(url)
    resp.raise_for_status()

    data = resp.json().get("table", [])
    return data


def fetch_season_table(league_id: str, season: str):
    url = f"{BASE_URL}/lookuptable.php?l={league_id}&s={season}"
    resp = requests.get(url)
    resp.raise_for_status()

    data = resp.json().get("table", [])
    return data


