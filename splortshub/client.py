import aiohttp
from asyncache import cached
import asyncio
import backoff
import beeline
from cachetools import TTLCache
import itertools
from typing import List, Iterable


_BLASEBALL_BASE_URL = "https://blaseball.com/"
_client = None


class BlaseballClient:
    _auth_cookie: str

    def __init__(self, auth_cookie: str):
        self._auth_cookie = auth_cookie

    @cached(TTLCache(1, 30))
    async def all_teams(self) -> List[dict]:
        with beeline.tracer("BlaseballClient/all_teams"):
            async with aiohttp.ClientSession(
                headers={"Cookie": f"connect.sid={self._auth_cookie}"}
            ) as session:
                return await _get_teams(session)

    @cached(TTLCache(1, 30))
    async def team(self, id: str) -> dict:
        with beeline.tracer("BlaseballClient/team"):
            async with aiohttp.ClientSession(
                headers={"Cookie": f"connect.sid={self._auth_cookie}"}
            ) as session:
                return await _get_team(session, id)

    @cached(TTLCache(1, 300))
    async def all_players(self) -> List[dict]:
        with beeline.tracer("BlaseballClient/all_players"):
            # note: the official API has /database/players, but it 500s if you try
            # to use it to read all players. We'll batch our requests into a few
            # smaller ones.
            async def get_players_for_team(team: dict) -> Iterable[dict]:
                sublists = await asyncio.gather(
                    self.players(team["bench"]),
                    self.players(team["lineup"]),
                    self.players(team["rotation"]),
                    self.players(team["bullpen"]),
                )

                return itertools.chain(*sublists)

            teams = await self.all_teams()
            gathered_players = [get_players_for_team(team) for team in teams]
            sublists = await asyncio.gather(*gathered_players)
            return list(itertools.chain(*sublists))

    async def players(self, ids: List[str]) -> List[dict]:
        with beeline.tracer("BlaseballClient/players"):
            async with aiohttp.ClientSession(
                headers={"Cookie": f"connect.sid={self._auth_cookie}"}
            ) as session:
                return await _get_players(session, ids)

    async def player(self, id: str) -> dict:
        players = await self.players([id])
        # super jank: return None if not found?
        return players[0]


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_time=5)
async def _get_teams(session: aiohttp.ClientSession) -> List[dict]:
    with beeline.tracer("remote/database/allTeams"):
        async with session.get(_api_route("database/allTeams")) as resp:
            resp.raise_for_status()
            return await resp.json()


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_time=5)
async def _get_team(session: aiohttp.ClientSession, id: str) -> dict:
    with beeline.tracer("remote/database/team"):
        params = {"id": id}
        async with session.get(_api_route("database/team"), params=params) as resp:
            resp.raise_for_status()
            return await resp.json()


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_time=5)
async def _get_players(session: aiohttp.ClientSession, ids: List[str]) -> List[dict]:
    with beeline.tracer("remote/database/players"):
        params = {"ids": ",".join(ids)}
        async with session.get(_api_route("database/players"), params=params) as resp:
            resp.raise_for_status()
            return await resp.json()


def _api_route(route: str) -> str:
    return _BLASEBALL_BASE_URL + route


def initialize(auth_cookie: str) -> None:
    global _client
    _client = BlaseballClient(auth_cookie)


def get_client() -> BlaseballClient:
    assert _client is not None
    return _client
