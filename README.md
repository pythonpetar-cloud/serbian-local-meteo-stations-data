# Local Meteo API

A weather data aggregator built for paragliders and outdoor athletes -- pulls
real-time conditions (wind, pressure, rain, gust alerts) from several
independent Serbian weather station APIs and makes them available through a
REST API and a Telegram bot.

## Why

Paragliding and outdoor sports depend on conditions that generic weather
apps don't surface well -- wind gusts, sudden pressure drops, hyper-local
station readings. This project pulls data straight from the small local
meteo stations pilots already trust, and puts it one command away in
Telegram instead of requiring a browser and a bookmark list.

## How it works

The project has two interfaces on top of the same aggregation logic:

- **REST API** (FastAPI) -- `GET /station/{id}` and `GET /stations` return
  live, normalized data for one or all stations.
- **Telegram bot** (`python-telegram-bot`) -- `/station <name>` fetches a
  station by name (diacritics optional -- "Fruska gora" resolves to
  "Fruška gora"), `/stations` lists all available stations as deep links
  you can tap directly, and `/rajac` is a shortcut for a specific station
  with richer data (fog risk, trail state, hiking index, rapid-change alerts).

Data fetching, message formatting, and bot command handling live in
separate modules, so the same underlying data can be reused by either
interface without duplication.

```
[station APIs] --(httpx, async)--> [aggregator] --+--> [FastAPI REST API]
                                                    +--> [Telegram bot]
```

## Features

- Aggregates multiple independent station APIs behind one consistent shape
- Async, concurrent fetching (httpx) -- multi-station requests don't block
  on each other
- One custom station (Rajac) has a different upstream shape entirely
  (fog risk, trail conditions, rapid-change alerts) and is normalized into
  the same interface as the standard stations
- Wind speeds reported in both km/h and m/s, since paragliders think in m/s
- Telegram deep-linking: tapping a station in `/stations` opens the bot
  with that station pre-selected, no typing required
- Diacritic-insensitive station name matching for typing convenience
- Per-station error isolation -- one failing station doesn't break a
  multi-station request

## Tech stack

Python · FastAPI · httpx (async) · python-telegram-bot · requests

## Project structure

```
.
├── main.py           # FastAPI app and routes
├── weather.py         # station data fetching, normalization, name matching
├── formatter.py        # Telegram message formatting (HTML)
└── telegram_bot.py      # bot commands and handlers
```

## Running locally

```bash
git clone https://github.com/pythonpetar-cloud/REPO-NAME.git
cd REPO-NAME
pip install fastapi httpx python-telegram-bot python-dotenv uvicorn
```

Create a `.env` file:

```
TELEGRAM_BOT_TOKEN=your_bot_token
BOT_USERNAME=your_bot_username
```

Run the API:

```bash
uvicorn main:app --reload
```

Run the Telegram bot (separate process):

```bash
python telegram_bot.py
```

## Status

Actively used. Next steps: additional stations, and possibly a simple web
dashboard alongside the API and bot.
