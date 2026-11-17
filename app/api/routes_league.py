
from fastapi import APIRouter, HTTPException
import requests

from app.core.config import BASE_URL, HEADERS, ALLOWED_LEAGUES

router = APIRouter()


@router.get("/leagues")
def get_leagues():
    url = f"{BASE_URL}/all/leagues"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch leagues from TheSportsDB"
        ) from e

    # V2 returns the leagues under "all".
    leagues_data = data.get("all")

    if not isinstance(leagues_data, list):
        raise HTTPException(
            status_code=502,
            detail="Unexpected leagues response from TheSportsDB"
        )

    # Keep only the configured soccer leagues.
    leagues = [
        {
            "idLeague": league["idLeague"],
            "strLeague": league["strLeague"],
            "strSport": league["strSport"],
            "strLeagueAlternate": league.get("strLeagueAlternate"),
        }
        for league in leagues_data
        if str(league.get("idLeague", "")) in ALLOWED_LEAGUES
           and league.get("strSport") == "Soccer"
           and league.get("strLeague")
    ]

    print(f"Total leagues received: {len(leagues_data)}")
    print(f"Allowed leagues returned: {len(leagues)}")

    return {"leagues": leagues}
