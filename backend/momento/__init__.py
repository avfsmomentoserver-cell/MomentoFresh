"""
Momento Core Package

This package contains the core backend modules for the MomentoFresh platform.
"""

__version__ = "4.0.0"

# Import key modules for easy access
from . import config, db, store, analysis, forecast, linguistics, plugins
from .feed import LiveFeedEngine
from .watcher import start_file_watcher
from .hub import hub

__all__ = [
    "config",
    "db",
    "store",
    "analysis",
    "forecast",
    "linguistics",
    "plugins",
    "LiveFeedEngine",
    "start_file_watcher",
    "hub",
]