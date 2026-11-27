# UniVent API

Base URL: `http://localhost:5000` locally. All requests and responses are JSON. Field names are `snake_case`.

## Errors

Every error uses the same shape, so the frontend can show messages next to form fields.

| Status | When | Body |
| --- | --- | --- |
| 400 | Validation failed | `{ "errors": { "name": "Name is required." } }` |
| 404 | Resource not found | `{ "error": "Club not found." }` |
| 409 | Conflict (e.g. deleting a club that still has events) | `{ "error": "Club still has events." }` |
| 500 | Unexpected server error | `{ "error": "Internal server error." }` |

Keys inside `errors` must be the request field names (`start_date`, `club_id`, ...). Put errors that aren't about one field under `"error"`.

## Universities

`university` must be one of the names in the frontend's `src/constants/universities.js` (from the CUE list of accredited universities), spelled exactly the same.

---

## Clubs

### Club object

```json
{
  "id": 1,
  "name": "Strathmore Tech Society",
  "university": "Strathmore University",
  "description": "Workshops, hackathons and tech talks.",
  "contact_email": "tech@strathmore.edu",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2026-11-20T10:15:00Z"
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `name` | string | Required, 1–100 characters, unique within a university |
| `university` | string | Required, one of the supported universities |
| `description` | string | Required |
| `contact_email` | string or null | Optional, valid email |
| `logo_url` | string or null | Optional, `http(s)://` URL |

### GET /api/clubs

List clubs, sorted by name.

| Query | Description |
| --- | --- |
| `university` | Only clubs at this university (exact match) |

```http
GET /api/clubs?university=Strathmore%20University
```

`200 OK`: an array of club objects.

### GET /api/clubs/&lt;id&gt;

`200 OK`: a club object. `404` if it does not exist.

### POST /api/clubs

```json
{
  "name": "Strathmore Tech Society",
  "university": "Strathmore University",
  "description": "Workshops, hackathons and tech talks.",
  "contact_email": "tech@strathmore.edu",
  "logo_url": null
}
```

`201 Created`: the new club object.

`400 Bad Request`:

```json
{ "errors": { "name": "Name is required.", "contact_email": "Enter a valid email address." } }
```

### PATCH /api/clubs/&lt;id&gt;

Send only the fields to change. Same rules as POST.

`200 OK`: the updated club. `400` with field errors, `404` if not found.

### DELETE /api/clubs/&lt;id&gt;

`204 No Content`. `404` if not found, `409` if the club still has events.

---

## Events

### Event object

```json
{
  "id": 7,
  "name": "Hack Night",
  "category": "Technology",
  "description": "Build something in one evening.",
  "start_date": "2026-12-20",
  "start_time": "18:00",
  "venue": "Main Auditorium",
  "city": "Nairobi",
  "price": 0,
  "image_url": null,
  "university": "Strathmore University",
  "club_id": 1,
  "club": { "id": 1, "name": "Strathmore Tech Society" },
  "created_at": "2026-11-26T09:00:00Z"
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `name` | string | Required, 1–120 characters |
| `category` | string | Required: `Academic`, `Arts & Culture`, `Career`, `Community`, `Sports`, `Technology`, `Social` |
| `description` | string | Required |
| `start_date` | string `YYYY-MM-DD` | Required, today or later |
| `start_time` | string `HH:MM` or null | Optional |
| `venue` | string | Required |
| `city` | string | Required |
| `price` | number | Optional, default 0, must be ≥ 0 (KES) |
| `image_url` | string or null | Optional, `http(s)://` URL |
| `club_id` | integer | Required, must be an existing club |
| `university` | string | Required, must equal the club's university |

### GET /api/events

List events, soonest first.

| Query | Description |
| --- | --- |
| `q` | Search name, description and venue (case-insensitive) |
| `university` | Only events at this university |
| `club_id` | Only events hosted by this club |

`200 OK`: an array of event objects.

### GET /api/events/&lt;id&gt;

`200 OK`: an event object. `404` if it does not exist.

### POST /api/events

```json
{
  "name": "Hack Night",
  "category": "Technology",
  "description": "Build something in one evening.",
  "start_date": "2026-12-20",
  "start_time": "18:00",
  "venue": "Main Auditorium",
  "city": "Nairobi",
  "price": 0,
  "image_url": null,
  "university": "Strathmore University",
  "club_id": 1
}
```

`201 Created`: the new event object.

`400 Bad Request`:

```json
{
  "errors": {
    "start_date": "Date must be today or later.",
    "club_id": "This club belongs to Kenyatta University, not Strathmore University."
  }
}
```

### PATCH /api/events/&lt;id&gt;

Send only the fields to change. Same rules as POST; if `club_id` or `university` changes, they must still match.

`200 OK`: the updated event. `400` with field errors, `404` if not found.

### DELETE /api/events/&lt;id&gt;

`204 No Content`. `404` if not found.