"""Configuración: lee variables de entorno y, si existe, el fichero .env."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv()

ODDS_API_KEY = os.environ.get("ODDS_API_KEY", "")
ODDS_API_REGIONS = os.environ.get("ODDS_API_REGIONS", "eu")
DB_PATH = Path(os.environ.get("GETOBET_DB", ROOT / "data" / "getobet.db"))
