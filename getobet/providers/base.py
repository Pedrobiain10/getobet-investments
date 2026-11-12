"""Interfaz que debe cumplir cualquier fuente de cuotas."""

from __future__ import annotations

from typing import Protocol

from getobet.models import OddsSnapshot


class OddsProvider(Protocol):
    name: str

    def list_sports(self) -> list[dict]:
        """Deportes/competiciones disponibles en la fuente."""
        ...

    def fetch_odds(self, sport_key: str, markets: list[str]) -> list[OddsSnapshot]:
        """Cuotas actuales de los próximos eventos de una competición."""
        ...
