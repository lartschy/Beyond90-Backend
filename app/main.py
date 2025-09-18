from fastapi import FastAPI
from app.api import routes_team

# create FastAPI application
app = FastAPI()

app.include_router(routes_team.router, prefix="/api", tags=["team"])

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}
