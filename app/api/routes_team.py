
from fastapi import APIRouter, HTTPException
import httpx
import re

from app.core.config import BASE_URL, HEADERS

router = APIRouter()


@router.get("/teams/{league_name}")
async def get_teams(league_name: str):
    # V2 search uses a slug, e.g. english_premier_league.
    league_slug = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        league_name
    ).strip("_").lower()

    async with httpx.AsyncClient(timeout=20.0) as client:
        # First, find the league ID.
        league_url = f"{BASE_URL}/search/league/{league_slug}"
        league_response = await client.get(
            league_url,
            headers=HEADERS
        )

        if league_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Error searching for league"
            )

        league_data = league_response.json()
        leagues = league_data.get("leagues") or []

        if not leagues:
            return {"teams": []}

        league_id = leagues[0].get("idLeague")

        if not league_id:
            raise HTTPException(
                status_code=502,
                detail="League ID missing from TheSportsDB response"
            )

        # Then, get the teams for that league.
        teams_url = f"{BASE_URL}/list/teams/{league_id}"
        teams_response = await client.get(
            teams_url,
            headers=HEADERS
        )

        if teams_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Error fetching teams"
            )

        teams_data = teams_response.json()

    return {"teams": teams_data.get("teams") or []}
