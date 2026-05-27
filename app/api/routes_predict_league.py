from fastapi import APIRouter
from app.services.league_prediction.league_service import LeagueService

router = APIRouter()
service = LeagueService()


@router.get("/predict_league")
async def predict_league(league_id: str):
    result = await service.predict_league_table(league_id)

    if not result:
        return {"error": "Could not generate prediction"}

    return result


@router.get("/debug-league/{league_id}")
async def debug_league(league_id: str):
    result = await service.predict_league_table(league_id)

    return {
        "teams_predicted": len(result["predicted_table"]) if result else 0,
        "top_team": result["predicted_table"][0] if result else None
    }