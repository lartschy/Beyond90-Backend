from fastapi import APIRouter
from app.services.football_api import get_last_matches

router = APIRouter()

@router.get("/team/{team_id}/last_matches")
def last_matches(team_id: int):
    data = get_last_matches(team_id)
    return data
