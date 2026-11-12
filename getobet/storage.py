"""Almacenamiento append-only de capturas de cuotas en SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from getobet.models import OddsSnapshot

SCHEMA = """
CREATE TABLE IF NOT EXISTS odds_snapshots (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at       TEXT NOT NULL,
    source            TEXT NOT NULL,
    event_id          TEXT NOT NULL,
    sport_key         TEXT NOT NULL,
    commence_time     TEXT NOT NULL,
    home_team         TEXT,
    away_team         TEXT,
    bookmaker         TEXT NOT NULL,
    market            TEXT NOT NULL,
    selection         TEXT NOT NULL,
    price             REAL NOT NULL,
    point             REAL,
    source_updated_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_odds_series
    ON odds_snapshots (event_id, market, selection, bookmaker, captured_at);
CREATE INDEX IF NOT EXISTS ix_odds_commence ON odds_snapshots (commence_time);
"""


def _iso(dt):
    return dt.isoformat() if dt else None


class OddsStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)

    def save(self, snapshots: list[OddsSnapshot]) -> int:
        rows = [
            (
                _iso(s.captured_at), s.source, s.event_id, s.sport_key,
                _iso(s.commence_time), s.home_team, s.away_team, s.bookmaker,
                s.market, s.selection, s.price, s.point, _iso(s.source_updated_at),
            )
            for s in snapshots
        ]
        with self.conn:
            self.conn.executemany(
                """INSERT INTO odds_snapshots (
                    captured_at, source, event_id, sport_key, commence_time,
                    home_team, away_team, bookmaker, market, selection, price,
                    point, source_updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                rows,
            )
        return len(rows)

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM odds_snapshots").fetchone()[0]

    def close(self) -> None:
        self.conn.close()
