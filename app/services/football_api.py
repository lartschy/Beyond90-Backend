import requests
from app.core.config import BASE_URL

def get_last_matches(team_id: int):
    url = f"{BASE_URL}/eventslast.php"
    params = {"id": team_id}

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()
