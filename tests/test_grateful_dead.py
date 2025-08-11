from pathlib import Path
import sqlite3
import sys

# Ensure repository root on path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from grateful_dead import build_database_and_files, load_recordings


def test_builds_database_and_directories(tmp_path: Path) -> None:
    """Database and file structure should mirror sample data."""

    db_path = tmp_path / "gd.db"
    base_path = tmp_path / "gd_files"
    shows_csv = Path(__file__).resolve().parent.parent / "data" / "gd_shows.csv"
    recordings_csv = Path(__file__).resolve().parent.parent / "data" / "gd_recordings.csv"

    build_database_and_files(db_path, base_path, shows_csv, recordings_csv)

    # Check database content
    with sqlite3.connect(db_path) as conn:
        show_count = conn.execute("SELECT COUNT(*) FROM shows").fetchone()[0]
        rec_count = conn.execute("SELECT COUNT(*) FROM recordings").fetchone()[0]
    assert show_count == 5
    assert rec_count == 10

    # Check file structure mirrors recordings
    for rec in load_recordings(recordings_csv):
        assert (base_path / rec.date / rec.source).is_dir()
