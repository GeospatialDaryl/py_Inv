from pathlib import Path
import sqlite3
import sys

# Ensure the repository root is on the import path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from audio_inventory import AudioScanner, AudioRepository, AudioInventory


def test_scanner_finds_audio_files(tmp_path: Path) -> None:
    """AudioScanner should return only supported audio files."""
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    (music_dir / "song.mp3").write_text("data")
    (music_dir / "notes.txt").write_text("not audio")

    scanner = AudioScanner(music_dir)
    files = scanner.scan()

    assert len(files) == 1
    audio = files[0]
    assert audio.name == "song.mp3"
    assert audio.parent == "music"
    assert audio.extension == ".mp3"


def test_repository_stores_files(tmp_path: Path) -> None:
    """AudioRepository should persist AudioFile entries."""
    (tmp_path / "track.wav").write_text("data")
    scanner = AudioScanner(tmp_path)
    files = scanner.scan()

    db_path = tmp_path / "audio.db"
    with AudioRepository(db_path) as repo:
        repo.create_schema()
        repo.add_files(files)
        rows = repo.conn.execute("SELECT name, parent, path, extension, filehash FROM audiofiles").fetchall()

    assert len(rows) == 1
    row = rows[0]
    assert row[0] == "track.wav"
    assert row[3] == ".wav"


def test_audio_inventory_integration(tmp_path: Path) -> None:
    """AudioInventory should scan and write to the database."""
    (tmp_path / "mix.flac").write_text("data")
    db_path = tmp_path / "inventory.db"
    inventory = AudioInventory(tmp_path, db_path)
    inventory.run()

    with sqlite3.connect(db_path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM audiofiles").fetchone()[0]
    assert count == 1
