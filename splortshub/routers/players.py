from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Iterable, Generator, Any

from splortshub.client import get_client

router = APIRouter()


class Player(BaseModel):
    id: str
    anticapitalism: float
    base_thirst: float
    buoyancy: float
    chasiness: float
    coldness: float
    continuation: float
    divinity: float
    ground_friction: float
    indulgence: float
    laserlikeness: float
    martyrdom: float
    moxie: float
    musclitude: float
    name: str
    bat: str
    omniscience: float
    overpowerment: float
    patheticism: float
    ruthlessness: float
    shakespearianism: float
    suppression: float
    tenaciousness: float
    thwackability: float
    tragicness: float
    unthwackability: float
    watchfulness: float
    pressurization: float
    total_fingers: int
    soul: int
    deceased: bool
    peanut_allergy: bool
    cinnamon: float
    fate: int


class PlayersResponse(BaseModel):
    players: List[Player]


@router.get("/api/v1beta/players", tags=["players"], response_model=PlayersResponse)
async def players():
    client = get_client()
    results = await client.all_players()
    return PlayersResponse(players=[_dict_to_player(player) for player in results])


@router.get("/api/v1beta/players/search/", tags=["players"], response_model=Player)
async def player_search(name: str = "") -> Player:
    client = get_client()
    results: Iterable[dict] = await client.all_players()
    if name != "":
        results = _query_filter(results, "name", name)
    collapsed_list = list(results)
    if not collapsed_list:
        raise HTTPException(status_code=404, detail="Player not found")
    player = collapsed_list[0]
    return _dict_to_player(player)


@router.get("/api/v1beta/player/{player_id}", tags=["players"], response_model=Player)
async def player(player_id: str) -> Player:
    client = get_client()
    results = await client.player(player_id)
    return _dict_to_player(results)


def _query_filter(
    stream: Iterable[dict], field: str, value: Any
) -> Generator[dict, None, None]:
    for item in stream:
        if item[field] == value:
            yield item


def _dict_to_player(player: dict) -> Player:
    return Player(
        id=player["_id"],
        anticapitalism=player["anticapitalism"],
        base_thirst=player["baseThirst"],
        buoyancy=player["buoyancy"],
        chasiness=player["chasiness"],
        coldness=player["coldness"],
        continuation=player["continuation"],
        divinity=player["divinity"],
        ground_friction=player["groundFriction"],
        indulgence=player["indulgence"],
        laserlikeness=player["laserlikeness"],
        martyrdom=player["martyrdom"],
        moxie=player["moxie"],
        musclitude=player["musclitude"],
        name=player["name"],
        bat=player["bat"],
        omniscience=player["omniscience"],
        overpowerment=player["overpowerment"],
        patheticism=player["patheticism"],
        ruthlessness=player["ruthlessness"],
        shakespearianism=player["shakespearianism"],
        suppression=player["suppression"],
        tenaciousness=player["tenaciousness"],
        thwackability=player["thwackability"],
        tragicness=player["tragicness"],
        unthwackability=player["unthwackability"],
        watchfulness=player["watchfulness"],
        pressurization=player["pressurization"],
        total_fingers=player["totalFingers"],
        soul=player["soul"],
        deceased=player["deceased"],
        peanut_allergy=player["peanutAllergy"],
        cinnamon=player["cinnamon"],
        fate=player["fate"],
    )
