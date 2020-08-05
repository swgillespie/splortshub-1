from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from typing import List, Iterable, Any, Generator

from splortshub.client import get_client

router = APIRouter()


class Team(BaseModel):
    id: str
    full_name: str
    location: str
    nickname: str
    emoji: str
    season_shames: int
    season_shamings: int
    shame_runs: int
    total_shames: int
    total_shamings: int
    slogan: str
    championships: int
    lineup: List[str]
    rotation: List[str]
    bullpen: List[str]
    bench: List[str]


class TeamsResponse(BaseModel):
    teams: List[Team]


@router.get("/api/v1beta/teams/", tags=["teams"], response_model=TeamsResponse)
async def teams():
    client = get_client()
    results = await client.all_teams()
    teams_list = [_dict_to_team(team) for team in results]
    return TeamsResponse(teams=teams_list)


@router.get("/api/v1beta/team/{team_id}", tags=["teams"], response_model=Team)
async def team(team_id: str) -> Team:
    client = get_client()
    results = await client.team(team_id)
    return _dict_to_team(results)


@router.get("/api/v1beta/teams/search/", tags=["teams"], response_model=Team)
async def team_search(full_name: str = "") -> Team:
    client = get_client()
    results: Iterable[dict] = await client.all_teams()
    if full_name != "":
        results = _query_filter(results, "fullName", full_name)
    collapsed_list = list(results)
    if not collapsed_list:
        raise HTTPException(status_code=404, detail="Team not found")
    team = collapsed_list[0]
    return _dict_to_team(team)


def _query_filter(
    stream: Iterable[dict], field: str, value: Any
) -> Generator[dict, None, None]:
    for item in stream:
        if item[field] == value:
            yield item


def _dict_to_team(team: dict) -> Team:
    return Team(
        id=team["_id"],
        full_name=team["fullName"],
        location=team["location"],
        nickname=team["nickname"],
        emoji=team["emoji"],
        season_shames=team["seasonShames"],
        season_shamings=team["seasonShamings"],
        shame_runs=team["shameRuns"],
        total_shames=team["totalShames"],
        total_shamings=team["totalShamings"],
        slogan=team["slogan"],
        championships=team["championships"],
        lineup=team["lineup"],
        rotation=team["rotation"],
        bullpen=team["bullpen"],
        bench=team["bench"],
    )
