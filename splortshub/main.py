import beeline
from fastapi import FastAPI, Request
from pydantic import BaseSettings
from typing import Optional

from splortshub.routers import status, teams, players
from splortshub.client import initialize
from splortshub.tracing import HoneycombMiddleware


class Settings(BaseSettings):
    blaseball_auth_cookie: str
    honey_api_key: Optional[str]
    honey_dataset: str = "splortshub-api"
    honey_debug: bool = False


settings = Settings()
initialize(settings.blaseball_auth_cookie)
app = FastAPI()
app.include_router(status.router)
app.include_router(teams.router)
app.include_router(players.router)
app.add_middleware(HoneycombMiddleware)

if settings.honey_api_key:
    beeline.init(
        writekey=settings.honey_api_key,
        dataset=settings.honey_dataset,
        debug=settings.honey_debug,
    )


@app.get("/")
async def root():
    return {"splorts": True}
