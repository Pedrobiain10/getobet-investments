"""Adaptador para The Odds API (https://the-odds-api.com), v4.

Coste: cada llamada a /odds consume (nº mercados × nº regiones) créditos.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from getobet.models import OddsSnapshot

BASE_URL = "https://api.the-odds-api.com/v4"


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_odds_response(
    payload: list[dict], captured_at: datetime, source: str = "the_odds_api"
) -> list[OddsSnapshot]:
    """Convierte la respuesta JSON de /odds en OddsSnapshot (una por selección y casa)."""
    snapshots: list[OddsSnapshot] = []
    for event in payload:
        commence = _parse_ts(event["commence_time"])
        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                updated = _parse_ts(market.get("last_update") or bookmaker.get("last_update"))
                for outcome in market.get("outcomes", []):
                    snapshots.append(
                        OddsSnapshot(
                            captured_at=captured_at,
                            source=source,
                            event_id=event["id"],
                            sport_key=event["sport_key"],
                            commence_time=commence,
                            home_team=event.get("home_team", ""),
                            away_team=event.get("away_team", ""),
                            bookmaker=bookmaker["key"],
                            market=market["key"],
                            selection=outcome["name"],
                            price=float(outcome["price"]),
                            point=outcome.get("point"),
                            source_updated_at=updated,
                        )
                    )
    return snapshots


class TheOddsAPI:
    name = "the_odds_api"

    def __init__(self, api_key: str, regions: str = "eu", timeout: float = 30.0):
        if not api_key:
            raise ValueError("Falta ODDS_API_KEY (ver .env.example)")
        self.api_key = api_key
        self.regions = regions
        self.timeout = timeout
        self.last_quota: dict[str, str | None] = {}

    def _get(self, path: str, **params: str) -> list[dict]:
        params["apiKey"] = self.api_key
        url = f"{BASE_URL}{path}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=self.timeout) as resp:
            self.last_quota = {
                "remaining": resp.headers.get("x-requests-remaining"),
                "used": resp.headers.get("x-requests-used"),
                "last_cost": resp.headers.get("x-requests-last"),
            }
            return json.loads(resp.read().decode("utf-8"))

    def list_sports(self) -> list[dict]:
        """Gratis: no consume créditos."""
        return self._get("/sports")

    def fetch_odds(self, sport_key: str, markets: list[str]) -> list[OddsSnapshot]:
        captured_at = datetime.now(timezone.utc)
        payload = self._get(
            f"/sports/{sport_key}/odds",
            regions=self.regions,
            markets=",".join(markets),
            oddsFormat="decimal",
            dateFormat="iso",
        )
        return parse_odds_response(payload, captured_at, source=self.name)
