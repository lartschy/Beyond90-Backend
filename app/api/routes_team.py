from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

@router.get("/teams/{league_name}")
async def get_teams(league_name: str):
    url = f"https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php"
    params = {"l": league_name}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching teams")

    data = response.json()

    if not data or "teams" not in data or data["teams"] is None:
        return {"teams": []}

    return data

