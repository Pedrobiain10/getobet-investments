"""Modelo de datos normalizado, común a todos los proveedores."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OddsSnapshot:
    """Una cuota concreta capturada en un momento concreto.

    Cada captura es una fila nueva: nunca se sobrescribe, así se reconstruye
    la serie temporal de cómo se ha movido la cuota.
    """

    captured_at: datetime  # cuándo la capturamos nosotros (UTC)
    source: str  # proveedor de datos, p. ej. "the_odds_api"
    event_id: str  # id del evento en la fuente
    sport_key: str  # p. ej. "soccer_spain_la_liga"
    commence_time: datetime  # hora de inicio del evento (UTC)
    home_team: str
    away_team: str
    bookmaker: str  # casa de apuestas, p. ej. "bet365"
    market: str  # p. ej. "h2h" (1X2)
    selection: str  # p. ej. nombre del equipo o "Draw"
    price: float  # cuota decimal
    point: float | None = None  # línea en hándicap / totales
    source_updated_at: datetime | None = None  # última actualización según la fuente
