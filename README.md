# getobet

Automatización del análisis de cuotas pre-partido: detectar cuotas con recorrido a la baja
varios días antes del evento, entrar, y cerrar la posición con beneficio antes del inicio.

**Fase actual: acceso al dato.** Capturar y guardar la serie temporal de cuotas.
Ver [docs/01-acceso-a-datos.md](docs/01-acceso-a-datos.md).

## Puesta en marcha

Requisitos: Python 3.11+. Sin dependencias externas.

```bash
cp .env.example .env          # y pon tu ODDS_API_KEY
python -m getobet sports      # lista competiciones disponibles (no gasta créditos)
python -m getobet snapshot soccer_spain_la_liga   # captura y guarda en data/getobet.db
python -m unittest discover -s tests              # tests
```

## Estructura

```
getobet/
  models.py              OddsSnapshot: modelo común a todas las fuentes
  providers/base.py      interfaz de proveedor de cuotas
  providers/the_odds_api.py
  storage.py             SQLite append-only
  __main__.py            CLI
docs/                    diseño y decisiones
tests/
```
