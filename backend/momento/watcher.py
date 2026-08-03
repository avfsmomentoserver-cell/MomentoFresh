"""
File Watcher for MomentoFresh

Monitors directories for new files and triggers ingestion.
"""

import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .config import settings
from .store import ingest_from_csv, ingest_from_json

logger = logging.getLogger(__name__)


class FileIngestHandler(FileSystemEventHandler):
    """Handles file system events for ingestion."""

    def __init__(self, inbox_path: Path, callbacks: Optional[List[Callable[[str, int], None]]] = None):
        self.inbox_path = inbox_path
        self.callbacks = callbacks or []
        self._processed_files: set = set()

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            
            # Only process files in the inbox directory
            if self.inbox_path in file_path.parents:
                self._process_file(file_path)

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            
            if self.inbox_path in file_path.parents:
                # Only process if not already processed
                if file_path not in self._processed_files:
                    self._process_file(file_path)

    def _process_file(self, file_path: Path):
        """Process a single file."""
        try:
            self._processed_files.add(file_path)
            
            # Determine file type
            suffix = file_path.suffix.lower()
            
            if suffix == ".csv":
                count = ingest_from_csv(str(file_path))
            elif suffix == ".json":
                count = ingest_from_json(str(file_path))
            else:
                logger.warning(f"Unsupported file type: {suffix}")
                return
            
            logger.info(f"Ingested {count} rounds from {file_path.name}")
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    callback(str(file_path), count)
                except Exception as e:
                    logger.error(f"Error in file watcher callback: {e}")
            
            # Optionally move or delete the file after processing
            # file_path.unlink()  # Delete the file
            # or file_path.rename(file_path.with_suffix(".processed"))
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")


class FileWatcher:
    """Watches directories for file changes."""

    def __init__(self):
        self.observer: Optional[Observer] = None
        self.handler: Optional[FileIngestHandler] = None
        self._callbacks: List[Callable[[str, int], None]] = []

    def add_callback(self, callback: Callable[[str, int], None]):
        """Add a callback for file ingestion events."""
        self._callbacks.append(callback)
        if self.handler:
            self.handler.callbacks.append(callback)

    def start(self, path: Optional[Path] = None):
        """Start watching a directory."""
        watch_path = path or Path(settings.inbox_path)
        watch_path.mkdir(parents=True, exist_ok=True)
        
        # Create handler
        self.handler = FileIngestHandler(watch_path, self._callbacks)
        
        # Create observer
        self.observer = Observer()
        self.observer.schedule(self.handler, str(watch_path), recursive=True)
        self.observer.start()
        
        logger.info(f"Started watching directory: {watch_path}")

    def stop(self):
        """Stop watching."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("File watcher stopped")


# Global watcher instance
watcher: Optional[FileWatcher] = None


def start_file_watcher(path: Optional[Path] = None):
    """Start the global file watcher."""
    global watcher
    if watcher is None:
        watcher = FileWatcher()
        watcher.start(path)
    return watcher


def get_file_watcher() -> Optional[FileWatcher]:
    """Get the global file watcher."""
    return watcher