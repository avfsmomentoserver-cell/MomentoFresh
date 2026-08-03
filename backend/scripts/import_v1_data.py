"""
Data Import Script for MomentoFresh

Imports deduplicated and converted rounds from old Momento system v1 to v4.
"""

import csv
import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from momento.config import settings
from momento.db import Round, get_session, session_scope
from momento.store import ingest_rounds_batch

logger = logging.getLogger(__name__)


class V1Importer:
    """Imports data from Momento v1 database."""

    def __init__(self, v1_db_path: str):
        self.v1_db_path = v1_db_path
        self._v1_conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Connect to v1 database."""
        if self._v1_conn is None:
            self._v1_conn = sqlite3.connect(self.v1_db_path)
            self._v1_conn.row_factory = sqlite3.Row
        return self._v1_conn

    def close(self):
        """Close v1 database connection."""
        if self._v1_conn:
            self._v1_conn.close()
            self._v1_conn = None

    def get_rounds(
        self,
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get rounds from v1 database."""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM rounds"
        params: List[Any] = []

        if start_date:
            query += " WHERE timestamp >= ?"
            params.append(start_date)
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
        elif end_date:
            query += " WHERE timestamp <= ?"
            params.append(end_date)

        query += " ORDER BY timestamp DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def convert_round(self, v1_round: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v1 round format to v4 format."""
        return {
            "source": v1_round.get("source", "unknown"),
            "timestamp": v1_round.get("timestamp") or v1_round.get("time"),
            "multiplier": float(v1_round.get("multiplier") or v1_round.get("multi") or 1.0),
            "color": v1_round.get("color"),
            "ingest_method": "v1_import",
            "source_file": "v1_database",
        }

    def deduplicate(self, rounds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate rounds."""
        seen: Dict[str, bool] = {}
        unique_rounds = []

        for round_data in rounds:
            key = f"{round_data.get('source')}:{round_data.get('timestamp')}:{round_data.get('multiplier')}"
            if key not in seen:
                seen[key] = True
                unique_rounds.append(round_data)

        return unique_rounds

    def validate(self, round_data: Dict[str, Any]) -> bool:
        """Validate round data."""
        required_fields = ["source", "timestamp", "multiplier"]
        for field in required_fields:
            if field not in round_data or round_data[field] is None:
                return False

        try:
            float(round_data["multiplier"])
        except (ValueError, TypeError):
            return False

        return True

    def import_rounds(
        self,
        limit: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        source: Optional[str] = None,
    ) -> int:
        """
        Import rounds from v1 database.

        Args:
            limit: Maximum number of rounds to import
            start_date: Start date filter
            end_date: End date filter
            source: Source filter

        Returns:
            Number of rounds imported
        """
        # Get rounds from v1
        v1_rounds = self.get_rounds(limit, start_date, end_date)

        # Filter by source
        if source:
            v1_rounds = [r for r in v1_rounds if r.get("source") == source]

        logger.info(f"Found {len(v1_rounds)} rounds in v1 database")

        # Convert format
        converted = [self.convert_round(r) for r in v1_rounds]

        # Validate
        valid = [r for r in converted if self.validate(r)]
        invalid_count = len(converted) - len(valid)
        if invalid_count > 0:
            logger.warning(f"Skipped {invalid_count} invalid rounds")

        # Deduplicate
        unique = self.deduplicate(valid)
        duplicate_count = len(valid) - len(unique)
        if duplicate_count > 0:
            logger.warning(f"Removed {duplicate_count} duplicate rounds")

        # Ingest
        count = ingest_rounds_batch(unique, source)
        logger.info(f"Imported {count} rounds from v1 database")

        return count


def import_v1_data(
    v1_db_path: str,
    limit: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = None,
) -> int:
    """
    Import data from v1 database.

    Args:
        v1_db_path: Path to v1 SQLite database
        limit: Maximum rounds to import
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)
        source: Source filter

    Returns:
        Number of rounds imported
    """
    importer = V1Importer(v1_db_path)
    try:
        count = importer.import_rounds(limit, start_date, end_date, source)
        return count
    finally:
        importer.close()


@click.command()
@click.option("--v1-db", default="v1_data/momento.db", help="Path to v1 database")
@click.option("--limit", default=None, type=int, help="Maximum rounds to import")
@click.option("--start-date", default=None, help="Start date (YYYY-MM-DD)")
@click.option("--end-date", default=None, help="End date (YYYY-MM-DD)")
@click.option("--source", default=None, help="Source filter")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(v1_db, limit, start_date, end_date, source, verbose):
    """Import data from Momento v1 database."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info(f"Starting v1 data import from {v1_db}")

    if not os.path.exists(v1_db):
        logger.error(f"v1 database not found: {v1_db}")
        return

    count = import_v1_data(v1_db, limit, start_date, end_date, source)
    logger.info(f"Import complete: {count} rounds imported")


if __name__ == "__main__":
    main()