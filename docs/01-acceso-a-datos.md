# 01 · Acceso a datos

Sin un histórico fiable de cómo se mueven las cuotas desde que se publican hasta que empieza
el evento, no se pueden definir umbrales, reglas de entrada ni de salida. Este documento
fija **qué dato necesitamos, de dónde sale y cómo lo guardamos**.

## 1. Qué dato necesitamos

La estrategia es: entrar días antes a una cuota alta → salir antes del inicio cuando la
cuota ha caído. Para analizarla hace falta la **serie temporal** de cada cuota:

| Campo | Por qué |
|---|---|
| Evento (id, deporte, competición, equipos, hora de inicio) | Identificar y cruzar entre fuentes |
| Mercado (1X2, hándicap, over/under…) y selección | Qué se apuesta |
| Casa de apuestas | Cada casa mueve la cuota distinto |
| Cuota (decimal) | El dato principal |
| **Momento de captura** | Sin esto no hay serie temporal: es la clave de todo |
| Momento de última actualización según la fuente | Detectar datos "congelados" |

Más adelante (no imprescindible para empezar): resultado final, cuota de cierre (closing
line), liquidez/volumen en exchanges.

**Regla de oro:** guardamos cada captura tal cual (append-only), nunca sobrescribimos.
El análisis se hace después sobre el histórico.

## 2. Fuentes posibles

| Fuente | Qué da | Coste / acceso | Encaje |
|---|---|---|---|
| **The Odds API** (the-odds-api.com) | Cuotas pre-partido de muchas casas (región `eu` incluye varias que operan en España), formato JSON | Plan gratis: 500 créditos/mes. Pagos desde ~30 $/mes. Histórico solo en planes de pago | **Punto de partida.** API sencilla y legal, sin scraping |
| **Betfair Exchange API** | Cuotas back/lay del exchange, volumen, y **permite cerrar posición** (back alto → lay bajo) | Cuenta Betfair + app key (hay una clave "delayed" gratuita para desarrollo) | **Clave para ejecutar la estrategia.** En un exchange "cerrar con beneficio" es nativo; en una casa normal depende del cash-out que te ofrezcan |
| Scraping de webs de casas/comparadores | Lo que se vea en la web | Gratis pero frágil y suele violar los términos de uso | Descartado salvo necesidad concreta |
| Proveedores profesionales (Sportradar, OddsJam, etc.) | Todo, en tiempo real | Caro | Si el proyecto escala |

### Nota importante sobre "cerrar la apuesta"
- En una **casa de apuestas** tradicional, cerrar antes de tiempo depende del *cash-out*:
  no siempre existe, la casa aplica margen, y las casas suelen limitar cuentas ganadoras.
- En un **exchange (Betfair)** se hace back a cuota alta y después lay a cuota baja sobre la
  misma selección: el beneficio queda asegurado gane quien gane. Es la forma "limpia" de
  ejecutar esta estrategia.

→ Propuesta: **analizar con The Odds API** (muchas casas, para detectar dónde está la
cuota alta) y **validar/ejecutar contra Betfair** (dónde se puede cerrar).

## 3. Arquitectura del módulo de datos

```
proveedor (The Odds API, Betfair, ...)      ← un adaptador por fuente
        │  normaliza a OddsSnapshot
        ▼
almacenamiento (SQLite: data/getobet.db)    ← append-only, una fila por cuota capturada
        ▼
análisis (siguiente fase)                   ← movimientos, umbrales, backtesting
```

- Cada proveedor implementa la misma interfaz (`getobet/providers/base.py`) y devuelve
  objetos `OddsSnapshot`. Añadir una fuente nueva = añadir un adaptador.
- SQLite para empezar: cero instalación, un único fichero. Migrable a Postgres/DuckDB.
- Sin dependencias externas de Python por ahora (solo librería estándar), para no
  depender de permisos de instalación en el equipo.

## 4. Frecuencia de captura y presupuesto

Cada llamada a The Odds API cuesta `nº mercados × nº regiones` créditos.
Ejemplo: una liga, mercado 1X2, región `eu` = 1 crédito por captura.

| Frecuencia | Créditos/mes (1 liga, 1 mercado) |
|---|---|
| Cada hora | ~720 → excede el plan gratis |
| Cada 2 horas | ~360 → cabe en el plan gratis |
| Cada 15 min | ~2.900 → plan de pago |

La caída de cuota que buscamos suele concentrarse en las últimas horas/día antes del
inicio, así que lo ideal a futuro es **muestreo adaptativo**: poco frecuente a varios días
vista, muy frecuente cerca del inicio.

## 5. Decisiones pendientes

1. **Deportes y competiciones** a seguir primero (¿fútbol: LaLiga, Premier, Champions…?).
2. **Mercados**: ¿solo 1X2 o también goles/hándicap?
3. **Casas de apuestas** concretas en las que se opera.
4. **¿Usamos Betfair?** Si sí, hace falta cuenta y app key.
5. **Dónde corre la captura**: este PC (solo cuando está encendido) o un servidor/servicio
   en la nube programado (recomendable para tener series completas).
6. **Presupuesto** para la API de datos.
