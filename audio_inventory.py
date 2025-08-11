from __future__ import annotations

"""Audio inventory utilities for scanning directories and storing metadata."""

from dataclasses import dataclass
from pathlib import Path
import hashlib
import sqlite3
from typing import Iterable, List

# List of supported audio file extensions. This can be customised per instance
# but is defined here for easy reuse and configuration.
DEFAULT_FORMATS = [".mp3", ".shn", ".aiff", ".wav", ".m4a", ".flac"]


@dataclass
class AudioFile:
    """Represents a single audio file discovered on disk."""

    name: str
    parent: str
    path: Path
    extension: str
    filehash: str


def file_hash(path: Path, chunk_size: int = 1024) -> str:
    """Return a SHA-1 hash for ``path``.

    Parameters
    ----------
    path:
        Path to the file whose contents should be hashed.
    chunk_size:
        Number of bytes to read per iteration. Defaults to 1024.
    """

    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


class AudioScanner:
    """Scan a directory tree for audio files.

    Parameters
    ----------
    root:
        Root directory to search.
    formats:
        Iterable of file extensions to include. Extensions are compared in a
        case-insensitive manner.
    """

    def __init__(self, root: Path, formats: Iterable[str] = DEFAULT_FORMATS) -> None:
        self.root = Path(root)
        self.formats = [f.lower() for f in formats]

    def scan(self) -> List[AudioFile]:
        """Return a list of :class:`AudioFile` instances found beneath ``root``."""

        audio_files: List[AudioFile] = []
        for path in self.root.rglob("*"):
            if path.is_file() and path.suffix.lower() in self.formats:
                parent = path.parent.name
                audio_files.append(
                    AudioFile(
                        name=path.name,
                        parent=parent,
                        path=path,
                        extension=path.suffix.lower(),
                        filehash=file_hash(path),
                    )
                )
        return audio_files


class AudioRepository:
    """Persist ``AudioFile`` objects in an SQLite database."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection | None = None

    def __enter__(self) -> "AudioRepository":
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        assert self.conn is not None
        self.conn.close()

    def create_schema(self) -> None:
        """Create the ``audiofiles`` table if it does not already exist."""

        assert self.conn is not None, "Database connection is not initialised"
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audiofiles (
                    name TEXT,
                    parent TEXT,
                    path TEXT PRIMARY KEY,
                    extension TEXT,
                    filehash TEXT
                )
                """
            )

    def add_files(self, files: Iterable[AudioFile], overwrite: bool = False) -> None:
        """Insert ``files`` into the database.

        Parameters
        ----------
        files:
            Iterable of :class:`AudioFile` instances to be stored.
        overwrite:
            If ``True``, existing rows with matching paths will be replaced.
            Otherwise, duplicates are ignored.
        """

        assert self.conn is not None, "Database connection is not initialised"
        with self.conn:
            for f in files:
                if overwrite:
                    self.conn.execute(
                        "REPLACE INTO audiofiles VALUES (?, ?, ?, ?, ?)",
                        (f.name, f.parent, str(f.path), f.extension, f.filehash),
                    )
                else:
                    self.conn.execute(
                        "INSERT OR IGNORE INTO audiofiles VALUES (?, ?, ?, ?, ?)",
                        (f.name, f.parent, str(f.path), f.extension, f.filehash),
                    )


class AudioInventory:
    """Convenience facade combining scanning and database persistence."""

    def __init__(self, root: Path, db_path: Path, formats: Iterable[str] = DEFAULT_FORMATS) -> None:
        self.scanner = AudioScanner(root, formats=formats)
        self.db_path = Path(db_path)

    def run(self, overwrite: bool = False) -> None:
        """Scan ``root`` and store results in ``db_path``."""

        files = self.scanner.scan()
        with AudioRepository(self.db_path) as repo:
            repo.create_schema()
            repo.add_files(files, overwrite=overwrite)
