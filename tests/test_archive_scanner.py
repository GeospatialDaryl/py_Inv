from pathlib import Path
import sys

# Ensure repository root on path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from archive_scanner import fetch_archive_shows, SEARCH_URL


def test_fetch_archive_shows_parses_response() -> None:
    """fetch_archive_shows should parse JSON data into ArchiveShow objects."""

    calls = []

    class DummyResponse:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self._data

    def dummy_get(url, params=None, timeout=None):
        calls.append((url, params, timeout))
        data = {
            "response": {
                "docs": [
                    {"title": "GD 1965-01-01", "identifier": "gd1965-01-01"},
                    {"title": "GD 1965-01-02", "identifier": "gd1965-01-02"},
                ]
            }
        }
        return DummyResponse(data)

    shows = fetch_archive_shows(1965, 1965, request_get=dummy_get)
    assert len(shows) == 2
    assert shows[0].title == "GD 1965-01-01"
    assert calls[0][0] == SEARCH_URL
    assert "collection:GratefulDead" in calls[0][1]["q"]
    assert "year:[1965 TO 1965]" in calls[0][1]["q"]
