from __future__ import annotations

"""Utilities for managing Grateful Dead concert data.

This module creates a SQLite database describing Grateful Dead shows and
recordings and mirrors that structure on disk.  Each concert date can have
multiple recordings (e.g. "SBD" or "AUD" sources) which are stored in a
separate table and represented as subdirectories beneath a date directory.
"""

from dataclasses import dataclass
from pathlib import Path
import csv
import sqlite3
from typing import Iterable, List


@dataclass(frozen=True)
class Show:
    """A single Grateful Dead performance."""

    date: str  # YYYY-MM-DD
    venue: str


@dataclass(frozen=True)
class Recording:
    """A particular recording of a show."""

    date: str  # link to :class:`Show` via its date
    source: str  # e.g. "SBD", "AUD"


class GratefulDeadDB:
    """SQLite wrapper storing shows and recordings."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def init_schema(self) -> None:
        """Create database tables if they do not already exist."""

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS shows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE,
                    venue TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS recordings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    show_id INTEGER,
                    source TEXT,
                    FOREIGN KEY(show_id) REFERENCES shows(id)
                )
                """
            )

    def add_show(self, show: Show) -> None:
        """Insert a show into the database."""

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO shows(date, venue) VALUES (?, ?)",
                (show.date, show.venue),
            )

    def add_recording(self, recording: Recording) -> None:
        """Insert a recording linked to an existing show."""

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT id FROM shows WHERE date = ?", (recording.date,))
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Show for date {recording.date} not found")
            (show_id,) = row
            conn.execute(
                "INSERT OR IGNORE INTO recordings(show_id, source) VALUES (?, ?)",
                (show_id, recording.source),
            )


def load_shows(csv_path: Path) -> List[Show]:
    """Load show information from a CSV file."""

    shows: List[Show] = []
    with Path(csv_path).open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            shows.append(Show(date=row["date"], venue=row["venue"]))
    return shows


def load_recordings(csv_path: Path) -> List[Recording]:
    """Load recording information from a CSV file."""

    recordings: List[Recording] = []
    with Path(csv_path).open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            recordings.append(Recording(date=row["date"], source=row["source"]))
    return recordings


def mirror_file_structure(base_path: Path, recordings: Iterable[Recording]) -> None:
    """Create directories for recordings mirroring the database structure."""

    for rec in recordings:
        dir_path = Path(base_path) / rec.date / rec.source
        dir_path.mkdir(parents=True, exist_ok=True)


def build_database_and_files(
    db_path: Path,
    base_path: Path,
    shows_csv: Path,
    recordings_csv: Path,
) -> None:
    """Populate the database and mirror directories for Grateful Dead shows.

    Parameters
    ----------
    db_path:
        Location for the SQLite database.
    base_path:
        Root directory where the file structure should be created.
    shows_csv:
        CSV containing ``date`` and ``venue`` columns for each show.
    recordings_csv:
        CSV containing ``date`` and ``source`` columns for each recording.
    """

    shows = load_shows(shows_csv)
    recordings = load_recordings(recordings_csv)

    db = GratefulDeadDB(db_path)
    db.init_schema()
    for show in shows:
        db.add_show(show)
    for recording in recordings:
        db.add_recording(recording)

    mirror_file_structure(base_path, recordings)
