# Pinball Widget API

A small Flask app that loads the VPS DB JSON and exposes:
- A JSON API for games and their child models
- HTML card widgets for **recently updated tables** and **recently updated backglasses**

> The upstream JSON is hosted at the VPS DB site. You can also run offline by setting `VPSDB_LOCAL_PATH`
> to a local copy of `vpsdb.json`.

---

## Endpoints

### Health
- `GET /health`
  - Returns `{ "status": "ok" }`

### API

- `GET /api/games`
  - Returns a JSON list of games (with `tableFiles` and `b2sFiles`)
  - Query params:
    - `limit` (int, default 50, max 500): number of games to return (sorted by most recently updated)

Example:
- `/api/games?limit=25`

---

## Table Widgets

### Mini-table widget
- `GET /widgets/tables/list`
  - Returns an HTML card widget showing the most recently updated tables
  - Query params:
    - `sort` (string, default `created`): `updated | created`
    - `limit` (int, default 10): number of tables to return
    - `format` (string, optional): filter on a table format value (exact, case-insensitive)
    - `theme` (string, default `light`): `light | dark | transparent`
    - `header` (string, default `true`): `true | false`
    - `footer` (string, default `true`): `true | false`

Examples:
- `/widgets/tables/list`
- `/widgets/tables/list?limit=15&theme=dark`
- `/widgets/tables/list?format=vpx&limit=10&theme=transparent`
- `/widgets/tables/list?format=fp&limit=5&theme=light&sort=updated`

### Image row widget
- `GET /widgets/tables/images`
  - Same filtering/sorting as `/widgets/tables/list`, but displayed as a horizontal row of images
  - Query params:
    - `sort`, `limit`, `format`, `theme`, `header`, `footer`

Examples:
- `/widgets/tables/images?limit=12`
- `/widgets/tables/images?format=vpx&theme=dark`

---

## Backglass Widgets

### Mini-table widget
- `GET /widgets/backglasses/list`
  - Returns an HTML card widget showing the most recently updated backglasses
  - Query params:
    - `sort` (string, default `updated`): `updated | created`
    - `limit` (int, default 10): number of items to return
    - `feature` (string, optional): filter on a single feature name (exact, case-insensitive)
    - `theme` (string, default `light`): `light | dark | transparent`
    - `header` (string, default `true`): `true | false`
    - `footer` (string, default `true`): `true | false`

Examples:
- `/widgets/backglasses/list`
- `/widgets/backglasses/list?limit=10&feature=2-screen&theme=dark`
- `/widgets/backglasses/list?limit=10&feature=2-screen&theme=dark&sort=created`

### Image row widget
- `GET /widgets/backglasses/images`
  - Same filtering/sorting as `/widgets/backglasses/list`, but displayed as a horizontal row of images
  - Query params:
    - `sort`, `limit`, `feature`, `theme`, `header`, `footer`

---

## Configuration

Environment variables:
- `VPSDB_URL` (default: VPS DB JSON URL)
- `VPSDB_LOCAL_PATH` (optional): path to a local `vpsdb.json` file
- `CACHE_TTL_SECONDS` (default: 900)

---

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Then open:
- `http://localhost:8000/widgets/tables/list?theme=light`
- `http://localhost:8000/widgets/backglasses/list?theme=dark`

---

## Running with Docker

Build & run:

```bash
docker compose -f docker-compose-example.yml up --build
```

---

## Notes

- The mapping code is defensive because upstream fields can evolve.
- Epoch timestamps (seconds or milliseconds) are converted to UTC `datetime` objects and rendered as ISO strings.
- URL priority is assigned by insertion order; the "best" URL is the highest priority non-broken URL.

## Multi-value filters

You can filter by multiple values using comma-separated lists:
- Tables: `?format=VPX,FP`
- Backglasses: `?feature=2Screens,Grill`



## Local JSON sync (remote -> disk)

This app keeps a **local copy** of the VPS DB JSON on disk and updates it when the upstream
timestamp increases.

How it works:
1. A local file `vpsdb.lastUpdated.json` stores the epoch timestamp associated with your local copy.
2. On load (by default), the app calls `VPSDB_LASTUPDATED_URL`.
3. If `remoteTimestamp > localTimestamp` (or the local JSON is missing), it downloads the latest JSON from `VPSDB_REMOTE_URL`.

Environment variables:
- `VPSDB_REMOTE_URL` (default: remote vpsdb.json URL)
- `VPSDB_LASTUPDATED_URL` (default: remote lastUpdated.json URL)
- `VPSDB_STORAGE_DIR` (default: `./data`)
- `VPSDB_LOCAL_JSON_PATH` (default: `${VPSDB_STORAGE_DIR}/vpsdb.json`)
- `VPSDB_LOCAL_TIMESTAMP_PATH` (default: `${VPSDB_STORAGE_DIR}/vpsdb.lastUpdated.json`)
- `VPSDB_SYNC_ON_START` (default: `true`)

Manual sync:
- `POST /sync` will perform a sync check and download only if remote is newer.


## Sync endpoints

- `GET /sync/status`
  - Returns the current local vs remote timestamps:
    - `localTimestamp`
    - `remoteTimestamp`

- `POST /sync`
  - Manual sync check. Downloads the latest DB only when:
    - local JSON is missing, or
    - `remoteTimestamp > localTimestamp`
  - Returns:
    - `updated` (bool)
    - `localTimestamp`
    - `remoteTimestamp`

### Sync behavior
- Automatic sync is performed on app startup when `VPSDB_SYNC_ON_START` is `true`.
- Sync errors are logged but do not prevent app startup.
- Sync opertations happen when the table or backglass widgets are requested.