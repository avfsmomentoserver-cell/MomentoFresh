"""
Database Layer for MomentoFresh

SQLAlchemy ORM models and database operations for the Momento platform.
"""

import logging
import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from .config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()
_engine = None
_Session = None


class Round(Base):
    __tablename__ = "rounds"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    multiplier = Column(Float, nullable=False)
    color = Column(String(20))
    band = Column(String(20), index=True)
    points = Column(Float)
    source_file = Column(String(255))
    ingest_method = Column(String(20), nullable=False, default="api", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = ({"sqlite_autoincrement": True},)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "multiplier": self.multiplier,
            "color": self.color,
            "band": self.band,
            "points": self.points,
            "source_file": self.source_file,
            "ingest_method": self.ingest_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Forecast(Base):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)
    round_id = Column(Integer, index=True)
    multiplier = Column(Float)
    predicted_min = Column(Float)
    predicted_max = Column(Float)
    confidence = Column(Float)
    state = Column(String(50))
    explanation = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    scored_at = Column(DateTime)
    accuracy = Column(Float)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "round_id": self.round_id,
            "multiplier": self.multiplier,
            "predicted_min": self.predicted_min,
            "predicted_max": self.predicted_max,
            "confidence": self.confidence,
            "state": self.state,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "scored_at": self.scored_at.isoformat() if self.scored_at else None,
            "accuracy": self.accuracy,
        }


class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    source = Column(String(50), nullable=False, index=True)
    config = Column(Text)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(20), default="pending")
    results = Column(Text)
    metrics = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "config": self.config,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "results": self.results,
            "metrics": self.metrics,
        }


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    display_name = Column(String(100))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text)
    category = Column(String(50), index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PressureState(Base):
    __tablename__ = "pressure_states"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    ceiling_value = Column(Float, nullable=False)
    pressure_score = Column(Float, default=0.0)
    gap_energy = Column(Float, default=0.0)
    arch_type = Column(String(20))
    is_verified = Column(Boolean, default=False)
    imminence = Column(String(20))
    release_probability = Column(Float, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ceiling_value": self.ceiling_value,
            "pressure_score": self.pressure_score,
            "gap_energy": self.gap_energy,
            "arch_type": self.arch_type,
            "is_verified": self.is_verified,
            "imminence": self.imminence,
            "release_probability": self.release_probability,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def init_database():
    global _engine, _Session
    db_path = settings.database_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite+pysqlite:///{db_path}?check_same_thread=False"
    _engine = create_engine(
        database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    @event.listens_for(_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA cache_size=-20000")
        cursor.close()

    Base.metadata.create_all(_engine)
    _Session = scoped_session(sessionmaker(bind=_engine, autocommit=False, autoflush=False))
    logger.info(f"Database initialized at {db_path}")


def get_engine():
    if _engine is None:
        init_database()
    return _engine


def get_session():
    if _Session is None:
        init_database()
    return _Session()


@contextmanager
def session_scope():
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        session.close()


def query(sql: str, params: Tuple = (), one: bool = False) -> Union[List[Tuple], Tuple, None]:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(sql, params)
        if one:
            return result.fetchone()
        return result.fetchall()


def query_one(sql: str, params: Tuple = ()) -> Optional[Tuple]:
    return query(sql, params, one=True)


def execute(sql: str, params: Tuple = ()) -> int:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(sql, params)
        conn.commit()
        return result.rowcount


def rows_to_dicts(rows: List[Tuple], columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    if not rows:
        return []
    if columns is None:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT * FROM rounds WHERE 1=0")
            columns = [desc[0] for desc in result.description]
    return [dict(zip(columns, row)) for row in rows]


def get_table_columns(table_name: str) -> List[str]:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in result.fetchall()]


def table_exists(table_name: str) -> bool:
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return result.fetchone() is not None


def count_rows(table_name: str, where: str = "", params: Tuple = ()) -> int:
    sql = f"SELECT COUNT(*) FROM {table_name}"
    if where:
        sql += f" WHERE {where}"
    result = query_one(sql, params)
    return result[0] if result else 0