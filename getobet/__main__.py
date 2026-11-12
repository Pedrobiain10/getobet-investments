"""CLI de getobet.

    python -m getobet sports                         # lista competiciones (gratis)
    python -m getobet snapshot soccer_spain_la_liga  # captura cuotas y las guarda
"""

from __future__ import annotations

import argparse

from getobet import config
from getobet.providers.the_odds_api import TheOddsAPI
from getobet.storage import OddsStore


def cmd_sports(args) -> None:
    api = TheOddsAPI(config.ODDS_API_KEY, regions=config.ODDS_API_REGIONS)
    for s in api.list_sports():
        if args.all or s.get("active"):
            print(f"{s['key']:<45} {s['title']}")


def cmd_snapshot(args) -> None:
    api = TheOddsAPI(config.ODDS_API_KEY, regions=config.ODDS_API_REGIONS)
    store = OddsStore(config.DB_PATH)
    total = 0
    for sport in args.sport:
        snaps = api.fetch_odds(sport, args.markets.split(","))
        saved = store.save(snaps)
        events = len({s.event_id for s in snaps})
        total += saved
        print(f"{sport}: {events} eventos, {saved} cuotas guardadas")
    print(f"Total en BD: {store.count()} | Créditos API: {api.last_quota}")
    store.close()


def main() -> None:
    parser = argparse.ArgumentParser(prog="getobet")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sports", help="Lista deportes/competiciones disponibles")
    p.add_argument("--all", action="store_true", help="Incluir inactivos")
    p.set_defaults(func=cmd_sports)

    p = sub.add_parser("snapshot", help="Captura cuotas actuales y las guarda")
    p.add_argument("sport", nargs="+", help="sport_key, p. ej. soccer_spain_la_liga")
    p.add_argument("--markets", default="h2h", help="Mercados separados por coma (h2h,totals,spreads)")
    p.set_defaults(func=cmd_snapshot)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
