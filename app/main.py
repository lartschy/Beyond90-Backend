from fastapi import FastAPI
from app.api import routes_league, routes_team, routes_fixtures, routes_predict_match, routes_predict_league

# create FastAPI application
app = FastAPI()

app.include_router(routes_league.router, prefix="/api", tags=["league"])
app.include_router(routes_team.router, prefix="/api", tags=["team"])
app.include_router(routes_fixtures.router, prefix="/api", tags=["fixtures"])
app.include_router(routes_predict_match.router, prefix="/api", tags=["match"])
app.include_router(routes_predict_league.router, prefix="/api", tags=["league"])

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}



