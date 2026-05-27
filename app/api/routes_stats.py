from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

router = APIRouter()
BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"

class TeamsRequest(BaseModel):
    team1: str
    team2: str

@router.post("/stats")
async def get_stats(data: TeamsRequest):
    team1, team2 = data.team1, data.team2

    async with httpx.AsyncClient() as client:
        # Első próbálkozás: team1 vs team2
        url = f"{BASE_URL}/searchevents.php"
        params = {"e": f"{team1} vs {team2}"}
        response = await client.get(url, params=params)
        data_api = response.json()
        matches = data_api.get("event", [])

        # Ha nem találja, próbáljuk fordítva
        if not matches:
            params = {"e": f"{team2} vs {team1}"}
            response = await client.get(url, params=params)
            data_api = response.json()
            matches = data_api.get("event", [])

    if not matches:
        raise HTTPException(status_code=404, detail="No matches found")

    team1_wins, team2_wins, draws = 0, 0, 0

    for match in matches:
        try:
            home = match.get("strHomeTeam")
            away = match.get("strAwayTeam")
            home_score = match.get("intHomeScore")
            away_score = match.get("intAwayScore")

            if not home_score or not away_score:
                continue

            home_score = int(home_score)
            away_score = int(away_score)

            if home_score > away_score:
                winner = home
            elif away_score > home_score:
                winner = away
            else:
                winner = "Draw"

            if winner == "Draw":
                draws += 1
            elif winner == team1:
                team1_wins += 1
            elif winner == team2:
                team2_wins += 1
        except Exception:
            continue

    return {
        "team1": team1,
        "team2": team2,
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "draws": draws,
        "total_matches": len(matches)
    }
