from fastapi import APIRouter
from app.services.matches_pred.service import MatchService

router = APIRouter()
service = MatchService()


@router.get("/predict_match")
def predict_match(team1: str, team2: str):

    try:
        print("INPUT:", team1, team2)

        if service.stats is None:
            print("MODEL NOT TRAINED")
            return {"error": "Model not trained"}

        result = service.predict_match(team1, team2)

        print("OUTPUT:", result)

        return result

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {"error": str(e)}

@router.get("/train")
async def train():
    await service.prepare()
    return {"status": "trained"}