# UniVent-BackEnd

Phase 2 turns the UniVent React app into a full-stack application: a Flask REST API and a PostgreSQL database replace the Ticketmaster API, with full CRUD on two related resources, **Clubs** and **Events**. A club belongs to one university and has many events; an event's university must match its club's university.

Frontend: [UniVent-FrontEnd](https://github.com/nobuyanzi07-cell/UniVent-FrontEnd)

## Setup

You need Python 3.11+ and PostgreSQL 14+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
createdb univent
cp .env.example .env             # then fill in the values below
flask db upgrade                 # create the tables
flask run --port 5000
```

The API is now at http://localhost:5000. Start the frontend with `npm run dev` in UniVent-FrontEnd; it proxies `/api` to this port.

## Environment variables

### Backend (`.env`)

| Variable | Required | Example | Description |
| --- | --- | --- | --- |
| `DATABASE_URL` | Yes | `postgresql://postgres:postgres@localhost:5432/univent` | PostgreSQL connection string. |
| `FLASK_APP` | Yes | `app.py` | Flask entry point. |
| `FLASK_DEBUG` | No | `1` | Auto-reload and debug pages locally. |
| `CORS_ORIGINS` | Production | `https://univent.vercel.app` | Frontend origin(s) allowed to call the API. |

### Frontend (`.env` in UniVent-FrontEnd)

| Variable | Required | Example | Description |
| --- | --- | --- | --- |
| `VITE_API_URL` | Production only | `https://univent-api.onrender.com` | Base URL of this API. Leave empty locally. |
| `VITE_USE_MOCK` | No | `false` | `true` uses mock events instead of the API. |

## Frontend routes

| Path | Page | API calls |
| --- | --- | --- |
| `/` | Browse events | `GET /api/events` |
| `/events/:id` | Event details | `GET /api/events/:id` |
| `/saved` | Saved events | none (localStorage) |
| `/create` | Create event | `GET /api/clubs?university=`, `POST /api/events` |
| `/clubs/new` | Create club | `POST /api/clubs` |
| `/clubs/:id/edit` | Edit club | `GET /api/clubs/:id`, `PATCH /api/clubs/:id` |
| `/auth` | Log in / sign up | none yet |

## API endpoints

Full request and response examples are in [`docs/API.md`](docs/API.md).

| Method | Endpoint | Success | Errors |
| --- | --- | --- | --- |
| GET | `/api/clubs?university=` | 200 list | — |
| GET | `/api/clubs/<id>` | 200 club | 404 |
| POST | `/api/clubs` | 201 club | 400 |
| PATCH | `/api/clubs/<id>` | 200 club | 400, 404 |
| DELETE | `/api/clubs/<id>` | 204 | 404, 409 |
| GET | `/api/events?q=&university=&club_id=` | 200 list | — |
| GET | `/api/events/<id>` | 200 event | 404 |
| POST | `/api/events` | 201 event | 400 |
| PATCH | `/api/events/<id>` | 200 event | 400, 404 |
| DELETE | `/api/events/<id>` | 204 | 404 |