
from fastapi import HTTPException, APIRouter
import asyncio
import httpx

from app.core.config import BASE_URL, HEADERS, PREDICTION_LEAGUES

router = APIRouter()


async def fetch_thesportsdb(url: str):
    """Send an authenticated request to TheSportsDB V2."""
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        print(f"TheSportsDB status: {e.response.status_code}")
        print(f"TheSportsDB response: {e.response.text}")
        raise HTTPException(
            status_code=502,
            detail="TheSportsDB request failed"
        ) from e

    except httpx.RequestError as e:
        print(f"TheSportsDB connection error: {e!r}")
        raise HTTPException(
            status_code=502,
            detail="Could not connect to TheSportsDB"
        ) from e


def validate_prediction_league(league_id: str):
    """Allow schedule requests only for prediction leagues."""
    if league_id not in PREDICTION_LEAGUES:
        raise HTTPException(
            status_code=400,
            detail="This league is not available for predictions"
        )


@router.get("/search_match")
async def search_match(team1: str, team2: str):
    """Search for a match using TheSportsDB V2."""
    event_slug = f"{team1}_vs_{team2}".replace(" ", "_")
    url = f"{BASE_URL}/search/event/{event_slug}"
    return await fetch_thesportsdb(url)


@router.get("/upcoming_matches/{league_id}")
async def upcoming_matches(league_id: str):
    """Fetch upcoming matches for one supported prediction league."""
    validate_prediction_league(league_id)
    url = f"{BASE_URL}/schedule/next/league/{league_id}"
    return await fetch_thesportsdb(url)


@router.get("/past_matches/{league_id}")
async def past_matches(league_id: str):
    """Fetch past matches for one supported prediction league."""
    validate_prediction_league(league_id)
    url = f"{BASE_URL}/schedule/previous/league/{league_id}"
    return await fetch_thesportsdb(url)


async def fetch_league_schedule(league_id: str, schedule_type: str):
    """Fetch a schedule for one of the supported prediction leagues."""
    url = f"{BASE_URL}/schedule/{schedule_type}/league/{league_id}"

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.json()

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        print(f"Schedule request failed for league {league_id}: {e}")
        return {}


async def fetch_all_prediction_matches(schedule_type: str):
    """Fetch schedules for all supported prediction leagues concurrently."""
    results = await asyncio.gather(
        *[
            fetch_league_schedule(league_id, schedule_type)
            for league_id in PREDICTION_LEAGUES
        ]
    )

    combined_matches = []
    seen_ids = set()

    for result in results:
        # TheSportsDB schedule response commonly uses "schedule".
        events = result.get("schedule", [])

        if not isinstance(events, list):
            continue

        for event in events:
            event_id = event.get("idEvent")

            if event_id and event_id not in seen_ids:
                seen_ids.add(event_id)
                combined_matches.append(event)

    return {"schedule": combined_matches}


@router.get("/upcoming_matches")
async def all_upcoming_matches():
    """Fetch upcoming matches for all six prediction leagues."""
    return await fetch_all_prediction_matches("next")


@router.get("/past_matches")
async def all_past_matches():
    """Fetch past matches for all six prediction leagues."""
    return await fetch_all_prediction_matches("previous")
