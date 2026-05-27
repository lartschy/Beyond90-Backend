from fastapi import APIRouter
import requests
from app.core.config import BASE_URL

router = APIRouter()

@router.get("/leagues")
def get_leagues():
    url = f"{BASE_URL}/all_leagues.php"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json().get("leagues", [])

    leagues = [
        {
            "idLeague": l["idLeague"],
            "strLeague": l["strLeague"],
            "strSport": l["strSport"],
            "strLeagueAlternate": l.get("strLeagueAlternate"),
        }
        for l in data
        if l["strSport"] == "Soccer" and l["strLeague"] != "_No League"
    ]

    return {"leagues": leagues}
