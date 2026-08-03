"""Rounds API routes"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from ..deps import verify_api_key
from ....db import Round, get_session
from ....store import get_rounds, get_latest_round, get_round_stats

router = APIRouter(prefix="/rounds")


@router.get("")
async def list_rounds(
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(100, description="Maximum number of rounds"),
    offset: int = Query(0, description="Offset for pagination"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    api_key: str = Depends(verify_api_key)
):
    rounds_list = get_rounds(source, limit, offset, start_date, end_date)
    return [r.to_dict() for r in rounds_list]


@router.get("/latest")
async def get_latest(
    source: Optional[str] = Query(None, description="Filter by source"),
    api_key: str = Depends(verify_api_key)
):
    round_obj = get_latest_round(source)
    if round_obj is None:
        raise HTTPException(status_code=404, detail="No rounds found")
    return round_obj.to_dict()


@router.get("/stats")
async def get_stats(
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(1000, description="Maximum number of rounds"),
    api_key: str = Depends(verify_api_key)
):
    return get_round_stats(source, limit)


@router.get("/sources/{source}/stats")
async def get_source_stats(
    source: str,
    limit: int = Query(1000, description="Maximum number of rounds"),
    api_key: str = Depends(verify_api_key)
):
    return get_round_stats(source, limit)