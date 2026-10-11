# Community Digital Voting System

A full-stack community voting platform built with **FastAPI** (Python) and **React** (Vite). Community members can create proposals, cast votes, and track results in real time. An auto-generated Python SDK (via OpenAPI Generator) is included for programmatic access.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Data Models](#data-models)
- [Frontend](#frontend)
- [Python SDK](#python-sdk)
- [Database & Migrations](#database--migrations)
- [Running Tests](#running-tests)
- [Environment Notes](#environment-notes)

---

## Features

- **Proposals** — Create, list, and view community proposals with a configurable deadline.
- **Voting** — Submit a `yes`, `no`, or `abstain` vote per proposal. One vote per voter per proposal (enforced at the database level).
- **Vote Revocation** — Voters can retract their vote while the proposal is still active.
- **Admin Controls** — Manually close an active proposal via an admin-protected endpoint.
- **Auto-expiry Logic** — Proposals past their deadline are treated as `expired`.
- **Vote Counts** — Live aggregated counts (`yes`, `no`, `abstain`, `total`) on every proposal detail response.
- **Interactive API Docs** — Swagger UI and ReDoc served automatically by FastAPI.
- **React Frontend** — Separate Admin and User dashboards built with React 19 and React Router.
- **Python SDK** — Auto-generated client library in `voting_sdk/` via OpenAPI Generator.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, SQLAlchemy 2, Alembic |
| Database | SQLite (`voting.db`) |
| Validation | Pydantic v2 |
| Frontend | React 19, Vite 8, React Router v7, Axios |
| Icons | Lucide React |
| Linting | Oxlint |
| Testing | Pytest, HTTPX |
| SDK | OpenAPI Generator (Python client) |

---

## Project Structure

```
community-digital-voting-system/
|
+-- main.py                  # FastAPI app entry point, CORS config, router registration
+-- database.py              # SQLAlchemy engine and session factory
+-- models.py                # ORM models: Proposal, Vote
+-- schemas.py               # Pydantic request/response schemas
+-- dependencies.py          # Shared dependencies: get_db, require_admin
+-- requirements.txt         # Python dependencies
+-- alembic.ini              # Alembic migration configuration
+-- voting.db                # SQLite database (created by setup; not committed)
+-- seed_data.sql            # Sample data: 5 proposals (3 active, 1 closed, 1 expired)
+-- seed_db.py               # Loads seed_data.sql into voting.db (--reset is destructive)
+-- sample_voting.db         # Clean sample database built from migrations + seed data
+-- build_sample_db.py       # Rebuilds sample_voting.db
+-- pytest.ini               # Limits the default pytest run to tests/
+-- openapi.json             # Exported OpenAPI spec used to generate the SDK
+-- openapitools.json        # OpenAPI Generator config (version + SDK settings)
+-- setupdev.bat             # One-time environment setup script (Windows)
+-- runapplication.bat       # Launch backend + frontend (Windows)
|
+-- routers/
|   +-- proposals.py         # Proposal CRUD and voting endpoints
|   +-- votes.py             # Vote revocation endpoint
|
+-- services/
|   +-- proposals.py         # Business logic for proposals
|   +-- votes.py             # Business logic for votes
|
+-- migrations/              # Alembic migration scripts
|
+-- tests/
|   +-- test_api.py          # Pytest integration tests
|
+-- frontend/                # React + Vite frontend
|   +-- src/
|   |   +-- main.jsx
|   |   +-- App.jsx
|   |   +-- Navbar.jsx
|   |   +-- AdminDashboard.jsx
|   |   +-- UserDashboard.jsx
|   |   +-- api.js           # Axios client (points to 127.0.0.1:8000)
|   |   +-- index.css
|   |   +-- App.css
|   +-- index.html
|   +-- vite.config.js
|   +-- package.json
|
+-- voting_sdk/              # Auto-generated Python SDK (OpenAPI Generator)
```

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | 3.10+ | Must be on PATH |
| Node.js | 18+ | Includes npm |
| Java | 11+ | Required for OpenAPI Generator CLI only |
| openapi-generator-cli | Latest | Only if regenerating the SDK |

---

## Quick Start

### Option A — Windows (Recommended)

**Step 1 — Set up environments (run once):**
```bat
.\setupdev.bat
```
This creates the Python virtual environment in `env\`, installs all backend and frontend dependencies, builds the SQLite schema with `alembic upgrade head`, and loads the sample proposals from `seed_data.sql` (only if the database is empty).

**Step 2 — Launch the application:**
```bat
.\runapplication.bat
```
This opens two separate terminal windows:
- **Backend** -> `http://127.0.0.1:8000`
- **Frontend** -> `http://127.0.0.1:5173`

---

### Option B — Manual Setup

**Backend:**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python seed_db.py
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

---

## API Reference

Interactive documentation:
- **Swagger UI** -> `http://127.0.0.1:8000/docs`
- **ReDoc** -> `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON** -> `http://127.0.0.1:8000/openapi.json`

### Endpoints

#### Health Check
| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Returns API status |

#### Proposals
| Method | Path | Description |
|---|---|---|
| `POST` | `/proposals/` | Create a new proposal |
| `GET` | `/proposals/` | List all proposals (optional `?status=active\|closed\|expired`) |
| `GET` | `/proposals/{id}` | Get proposal details with live vote counts |
| `PATCH` | `/proposals/{id}/close` | Manually close a proposal *(Admin only)* |
| `POST` | `/proposals/{id}/vote` | Submit a vote on a proposal |

#### Votes
| Method | Path | Description |
|---|---|---|
| `DELETE` | `/votes/{vote_id}` | Revoke a previously cast vote |

### Example: Create a Proposal

```json
POST /proposals/
{
  "title": "Install solar panels on community hall",
  "description": "Proposal to reduce energy costs by installing 20kW solar panels.",
  "deadline": "2026-11-01T23:59:00"
}
```

### Example: Cast a Vote

```json
POST /proposals/1/vote
{
  "voter_name": "Alice",
  "vote": "yes"
}
```

> **Note:** Each voter can only vote once per proposal. A second attempt returns HTTP 400.

### Admin Authentication

The admin endpoint (`PATCH /proposals/{id}/close`) requires:
```
X-Admin-Token: karthi123
```
> The default token is `karthi123`. Override it with the `ADMIN_TOKEN` environment variable (read in `dependencies.py`) before deploying to production.

---

## Data Models

### Proposal

| Field | Type | Description |
|---|---|---|
| `id` | integer | Auto-incremented primary key |
| `title` | string (max 200) | Proposal title |
| `description` | text | Full proposal body |
| `created_at` | datetime (UTC) | Auto-set on creation |
| `deadline` | datetime (UTC) | Defaults to 2 days from creation |
| `status` | enum | `active`, `closed`, or `expired` |

### Vote

| Field | Type | Description |
|---|---|---|
| `id` | integer | Auto-incremented primary key |
| `proposal_id` | integer (FK) | References `proposals.id` |
| `voter_name` | string (max 100) | Voter identifier |
| `vote` | enum | `yes`, `no`, or `abstain` |
| `voted_at` | datetime (UTC) | Auto-set on creation |

> **Constraint:** `(proposal_id, voter_name)` is unique — one vote per voter per proposal.

---

## Frontend

| View | Route | Description |
|---|---|---|
| User Dashboard | `/` | Browse proposals, cast/revoke votes, view live counts |
| Admin Dashboard | `/admin` | Create proposals, manually close active proposals |

The API base URL is configured in `frontend/src/api.js` pointing to `http://127.0.0.1:8000`.

---

## Python SDK

The SDK in `voting_sdk/` (Python package `voting_sdk`) is generated with OpenAPI Generator 7.26.0. The generator settings live in `openapitools.json`, and the input spec is the committed `openapi.json`, so no running server is needed to regenerate it.

**Whenever an endpoint or schema changes, re-export `openapi.json` and regenerate the SDK**, otherwise the SDK goes stale. `tests/test_openapi_spec.py` fails if the committed `openapi.json` no longer matches the running app, so pytest catches this automatically.

To regenerate (requires Java and `npm install -g @openapitools/openapi-generator-cli`):
```powershell
# 1. Export the current spec from the FastAPI app
.\env\Scripts\python.exe -c "import json, main; json.dump(main.app.openapi(), open('openapi.json', 'w'), indent=2)"

# 2. Generate the SDK using the config in openapitools.json
openapi-generator-cli generate --generator-key voting-sdk

# 3. Reinstall it into the virtual environment
.\env\Scripts\python.exe -m pip install -e voting_sdk
```

To install and use locally:
```powershell
.\env\Scripts\python.exe -m pip install -e voting_sdk
```

```python
from voting_sdk import ApiClient, Configuration, ProposalsApi

client = ApiClient(Configuration(host="http://127.0.0.1:8000"))
for p in ProposalsApi(client).list_proposals_proposals_get():
    print(p.id, p.title, p.status)
```

Refer to `voting_sdk/README.md` and `voting_sdk/docs/` for full usage documentation.

---

## Database & Migrations

```powershell
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe your change"

# Roll back one migration
alembic downgrade -1
```

The migrations in `migrations/` are the authoritative schema. `voting.db` (your working database) is never committed; `setupdev.bat` creates it with `alembic upgrade head` and then runs `seed_db.py`, which loads `seed_data.sql` **only if the database has no proposals**. Nothing seeds or resets data when the application starts.

### Resetting to the sample data

> **⚠ Warning — destructive.** `--reset` permanently **deletes every proposal and vote** in `voting.db`, then inserts the 5 sample proposals (3 active, 1 closed, 1 expired). There is no undo; copy `voting.db` first if you need to keep it.

```powershell
.\env\Scripts\python.exe seed_db.py --reset
```

### Sample database (`sample_voting.db`)

`sample_voting.db` is a clean, committed SQLite file for reviewers: the schema from the migrations (stamped at revision `39bbda8b379a`) plus the 5 sample proposals and no votes. It is a convenience snapshot, not the source of truth.

To run the app against it, copy it over the working database (this replaces `voting.db`):
```powershell
Copy-Item sample_voting.db voting.db
.\env\Scripts\python.exe -m alembic upgrade head   # no-op unless newer migrations exist
```

Sample dates are fixed when the file is built, so the "active" proposals auto-expire about 3–7 days later. To get fresh dates, rebuild the file (this only touches `sample_voting.db`) or use `seed_db.py --reset` on your working database:
```powershell
.\env\Scripts\python.exe build_sample_db.py
```

---

## Running Tests

```powershell
.\env\Scripts\python.exe -m pytest -v
```

`pytest.ini` limits the default run to `tests/`. They use an in-memory SQLite database and the FastAPI TestClient, so no running server is needed. They cover:

- creating and reading proposals, vote counts, and one-vote-per-name uniqueness
- vote revocation and re-voting while a proposal is active
- rejecting votes and revocations on closed proposals and after the deadline passes (auto-expiry)
- admin closure: rejected with a missing, invalid or empty `X-Admin-Token` (401), allowed with a valid token, and rejected when the proposal is already closed (400)
- 404s for nonexistent proposals and votes, and 422s for invalid vote payloads
- the committed `openapi.json` matching the live API, so the SDK can't silently go stale

The OpenAPI Generator also creates placeholder tests in `voting_sdk/test/`. They are empty stubs and test no SDK behaviour, so they are not part of the default run (`python -m pytest voting_sdk/test` runs them).

---

## Environment Notes

- Virtual environment is in `env\` targeting **Python 3.10**.
- `voting.db` and `voting_sdk/` are **preserved** when re-running `setupdev.bat` (sample data is only loaded into an empty database).
- CORS is set to `allow_origins=["*"]` for local development — restrict this in production.
- The default admin token (`karthi123`) **must** be overridden via the `ADMIN_TOKEN` environment variable before public deployment.
- Vite defaults to port **5173**; it auto-selects the next available port if 5173 is busy.

---

## License

This project is for community and educational use. Contact the project maintainer for usage rights.
