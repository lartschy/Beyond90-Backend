from fastapi import FastAPI, HTTPException, APIRouter
import httpx

router = APIRouter()
BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"

@router.get("/search_match")
async def search_match(team1: str, team2: str):
    url = f"{BASE_URL}/searchevents.php"
    params = {"e": f"{team1} vs {team2}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        return {"event": []}

    data = response.json()
    #print(data)
    return data
