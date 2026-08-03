"""
Data Storage and Import Layer for MomentoFresh

Handles data ingestion, retrieval, and caching.
"""

import csv
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, or_

from .config import settings
from .db import Round, Source, get_session, session_scope, table_exists
from .analysis import analyze_rounds, AnalysisPayload

logger = logging.getLogger(__name__)

# Analysis payload cache
_analysis_cache: Dict[str, Tuple[AnalysisPayload, datetime]] = {}


def seed_initial_data():
    """Seed initial data if the database is empty."""
    with session_scope() as session:
        # Check if sources exist
        count = session.query(Source).count()
        if count == 0:
            # Add default sources
            default_sources = [
                {"name": "aviator", "display_name": "Aviator", "active": True},
                {"name": "skyward", "display_name": "Skyward", "active": True},
                {"name": "jetx", "display_name": "JetX", "active": True},
            ]
            for source_data in default_sources:
                source = Source(**source_data)
                session.add(source)
            logger.info(f"Seeded {len(default_sources)} default sources")


def ingest_round(data: Dict[str, Any], source: Optional[str] = None) -> Round:
    """
    Ingest a single round into the database.
    
    Args:
        data: Round data dictionary
        source: Optional source override
        
    Returns:
        The created Round object
    """
    with session_scope() as session:
        # Normalize data
        round_data = {
            "source": source or data.get("source", "unknown"),
            "timestamp": data.get("timestamp") or data.get("time") or datetime.utcnow(),
            "multiplier": float(data.get("multiplier") or data.get("multi") or 1.0),
            "color": data.get("color"),
            "band": data.get("band"),
            "points": data.get("points"),
            "source_file": data.get("source_file"),
            "ingest_method": data.get("ingest_method", "api"),
        }
        
        # Check for duplicate
        existing = session.query(Round).filter(
            and_(
                Round.source == round_data["source"],
                Round.timestamp == round_data["timestamp"],
                Round.multiplier == round_data["multiplier"],
            )
        ).first()
        
        if existing:
            logger.debug(f"Duplicate round found, skipping: {round_data}")
            return existing
        
        # Create new round
        round_obj = Round(**round_data)
        session.add(round_obj)
        logger.debug(f"Ingested round: source={round_data['source']}, multiplier={round_data['multiplier']}")
        
        return round_obj


def ingest_rounds_batch(rounds_data: List[Dict[str, Any]], source: Optional[str] = None) -> int:
    """
    Ingest multiple rounds in a batch.
    
    Args:
        rounds_data: List of round data dictionaries
        source: Optional source override
        
    Returns:
        Number of rounds ingested
    """
    count = 0
    with session_scope() as session:
        for data in rounds_data:
            try:
                round_data = {
                    "source": source or data.get("source", "unknown"),
                    "timestamp": data.get("timestamp") or data.get("time") or datetime.utcnow(),
                    "multiplier": float(data.get("multiplier") or data.get("multi") or 1.0),
                    "color": data.get("color"),
                    "band": data.get("band"),
                    "points": data.get("points"),
                    "source_file": data.get("source_file"),
                    "ingest_method": data.get("ingest_method", "batch"),
                }
                
                # Check for duplicate
                existing = session.query(Round).filter(
                    and_(
                        Round.source == round_data["source"],
                        Round.timestamp == round_data["timestamp"],
                        Round.multiplier == round_data["multiplier"],
                    )
                ).first()
                
                if not existing:
                    round_obj = Round(**round_data)
                    session.add(round_obj)
                    count += 1
            except Exception as e:
                logger.error(f"Error ingesting round: {e}")
                continue
    
    logger.info(f"Ingested {count} rounds in batch")
    return count


def get_rounds(
    source: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Round]:
    """
    Get rounds from the database.
    
    Args:
        source: Filter by source
        limit: Maximum number of rounds
        offset: Offset for pagination
        start_date: Filter by start date
        end_date: Filter by end date
        
    Returns:
        List of Round objects
    """
    with session_scope() as session:
        query = session.query(Round).order_by(Round.timestamp.desc())
        
        if source:
            query = query.filter(Round.source == source)
        
        if start_date:
            query = query.filter(Round.timestamp >= start_date)
        
        if end_date:
            query = query.filter(Round.timestamp <= end_date)
        
        query = query.offset(offset).limit(limit)
        return query.all()


def get_latest_round(source: Optional[str] = None) -> Optional[Round]:
    """Get the latest round for a source."""
    with session_scope() as session:
        query = session.query(Round).order_by(Round.timestamp.desc())
        if source:
            query = query.filter(Round.source == source)
        return query.first()


def get_round_stats(source: Optional[str] = None, limit: int = 1000) -> Dict[str, Any]:
    """Get statistics for rounds."""
    rounds = get_rounds(source, limit)
    if not rounds:
        return {}
    
    multipliers = [r.multiplier for r in rounds]
    
    return {
        "count": len(rounds),
        "min_multiplier": min(multipliers) if multipliers else 0,
        "max_multiplier": max(multipliers) if multipliers else 0,
        "avg_multiplier": sum(multipliers) / len(multipliers) if multipliers else 0,
        "sources": list(set(r.source for r in rounds)),
    }


def get_analysis_payload_cached(source: str, limit: Optional[int] = None) -> AnalysisPayload:
    """
    Get analysis payload with caching.
    
    Args:
        source: The game source
        limit: Maximum rounds to analyze
        
    Returns:
        AnalysisPayload with cached results
    """
    cache_key = f"{source}:{limit}"
    cached = _analysis_cache.get(cache_key)
    
    if cached and (datetime.utcnow() - cached[1]).total_seconds() < settings.analysis_cache_ttl:
        return cached[0]
    
    payload = analyze_rounds(source, limit or settings.default_round_limit)
    _analysis_cache[cache_key] = (payload, datetime.utcnow())
    
    return payload


def ingest_from_csv(file_path: str, source: Optional[str] = None) -> int:
    """
    Ingest rounds from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        source: Optional source override
        
    Returns:
        Number of rounds ingested
    """
    count = 0
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                data = {
                    "timestamp": row.get("timestamp") or row.get("time"),
                    "multiplier": float(row.get("multiplier") or row.get("multi") or 1.0),
                    "source": source or row.get("source", "unknown"),
                }
                ingest_round(data)
                count += 1
            except Exception as e:
                logger.error(f"Error parsing CSV row: {e}")
                continue
    
    logger.info(f"Ingested {count} rounds from {file_path}")
    return count


def ingest_from_json(file_path: str, source: Optional[str] = None) -> int:
    """
    Ingest rounds from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        source: Optional source override
        
    Returns:
        Number of rounds ingested
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return ingest_rounds_batch(data, source)
    elif isinstance(data, dict):
        return ingest_rounds_batch([data], source)
    else:
        logger.error(f"Unsupported JSON format in {file_path}")
        return 0