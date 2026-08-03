"""Analysis API routes"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..deps import verify_api_key
from ....analysis import get_analysis_payload, AnalysisPayload
from ....linguistics import analyze_linguistics

router = APIRouter(prefix="/analysis")


@router.get("")
async def get_analysis(
    source: str = Query(..., description="Game source to analyze"),
    limit: Optional[int] = Query(None, description="Maximum rounds to analyze"),
    include: str = Query("", description="Comma-separated list of features to include"),
    api_key: str = Depends(verify_api_key)
):
    payload = get_analysis_payload(source, limit)
    
    # Add optional features
    features = include.split(",") if include else []
    
    if "linguistics" in features:
        linguistics = analyze_linguistics(source, limit)
        payload.linguistics = linguistics.to_dict()
    
    return payload.to_dict()


@router.get("/state")
async def get_state(
    source: str = Query(..., description="Game source"),
    limit: Optional[int] = Query(None, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    payload = get_analysis_payload(source, limit)
    return {
        "source": source,
        "count": payload.count,
        "latest_multiplier": payload.multipliers[0] if payload.multipliers else None,
        "stats": payload.stats,
        "patterns": payload.patterns,
    }


@router.get("/signals")
async def get_signals(
    source: str = Query(..., description="Game source"),
    limit: Optional[int] = Query(None, description="Maximum rounds"),
    api_key: str = Depends(verify_api_key)
):
    payload = get_analysis_payload(source, limit)
    return {
        "signals": payload.signals or [],
        "source": source,
        "count": payload.count,
    }