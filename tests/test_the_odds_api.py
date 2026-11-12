import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from getobet.providers.the_odds_api import parse_odds_response
from getobet.storage import OddsStore

SAMPLE = [
    {
        "id": "evt1",
        "sport_key": "soccer_spain_la_liga",
        "sport_title": "La Liga - Spain",
        "commence_time": "2026-11-15T20:00:00Z",
        "home_team": "Real Betis",
        "away_team": "Sevilla",
        "bookmakers": [
            {
                "key": "bet365",
                "title": "Bet365",
                "last_update": "2026-11-12T16:00:00Z",
                "markets": [
                    {
                        "key": "h2h",
                        "last_update": "2026-11-12T16:00:00Z",
                        "outcomes": [
                            {"name": "Real Betis", "price": 2.1},
                            {"name": "Sevilla", "price": 3.4},
                            {"name": "Draw", "price": 3.25},
                        ],
                    }
                ],
            }
        ],
    }
]


class ParseTest(unittest.TestCase):
    def test_parse_and_store(self):
        now = datetime(2026, 11, 12, 17, 0, tzinfo=timezone.utc)
        snaps = parse_odds_response(SAMPLE, now)
        self.assertEqual(len(snaps), 3)
        betis = next(s for s in snaps if s.selection == "Real Betis")
        self.assertEqual(betis.price, 2.1)
        self.assertEqual(betis.bookmaker, "bet365")
        self.assertEqual(betis.commence_time.year, 2026)

        with tempfile.TemporaryDirectory() as tmp:
            store = OddsStore(Path(tmp) / "t.db")
            store.save(snaps)
            store.save(snaps)  # segunda captura: se añade, no se sobrescribe
            self.assertEqual(store.count(), 6)
            store.close()


if __name__ == "__main__":
    unittest.main()
