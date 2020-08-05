from pydantic import BaseModel
from fastapi import APIRouter


router = APIRouter()


class StatusResponse(BaseModel):
    ok: bool


@router.get("/api/v1beta/status/", tags=["status"], response_model=StatusResponse)
async def status():
    return StatusResponse(ok=True)
