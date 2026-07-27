# Traveller Login & Dashboard — Setup

This backend now provides traveller authentication and itinerary data for the
**traveller dashboard** app, backed by PostgreSQL.

## What was added

- `app/models/traveller.py` — `Traveller`, `Itinerary`, `ItineraryStop` tables.
- `app/core/security.py` — bcrypt password hashing + JWT (HS256) tokens.
- `app/schemas/auth_schema.py` — request/response schemas (serialised in the
  camelCase shape the dashboard's `types.ts` already expects).
- `app/routers/auth.py` — `POST /api/auth/register`, `POST /api/auth/login`,
  `POST /api/auth/google`, `POST /api/auth/forgot-password`, `POST /api/auth/reset-password`,
  `GET /api/auth/me`, `PUT /api/auth/me`.
- `app/core/google_auth.py` — verifies Google Sign-In ID tokens.
- `app/services/password_reset_service.py` — sends the password-reset email via Resend.
- `app/routers/itineraries.py` — `GET /api/traveller/itineraries`, `PUT /api/traveller/itineraries`.
- `seed.py` — creates tables and inserts a demo traveller + itineraries.

## Where login lives now

Traveller login/sign-up is built **natively into the main website** (`ril-homepage-rebuild`):

- `/login/traveller` — sign in, create account, Google, and "forgot password".
- `/reset-password?token=…` — the page the reset email links to.
- `/traveller` — the premium traveller dashboard (profile + itineraries from the DB).

The main site talks to this backend via `VITE_API_BASE_URL` (default `http://localhost:8000`).
(The standalone `traveler-dashboard` app in Downloads still works too, but is no longer the
primary login home.)

## Admin console

A separate, seeded admin area manages public site content:

- `app/models/admin.py`, `app/models/content.py` — `Admin`, `Theme`, `Place`, `Package` tables.
- `app/core/admin_security.py` — admin JWT (`scope=admin`) + `get_current_admin`.
- `app/routers/admin.py` — `POST /api/admin/login`, CRUD for `/themes`, `/places`, `/packages`,
  and `GET /api/admin/reports/overview` + `/api/admin/reports/travellers.csv`.
- `app/routers/content.py` — **public, no-auth** reads (`/api/content/themes|places|packages`)
  that the live site consumes, so admin edits appear automatically.
- `seed_admin_content.py` — creates an admin + the initial themes, places, and packages.

Seed and log in:

```
python seed_admin_content.py
```

```
email:    admin@royaleisles.lk
password: admin12345
```

On the site: `/login/admin` → `/admin` (Reports · Packages · Themes · Places).
Admins manage public packages/themes/places only — they do **not** touch travellers'
personal itineraries. The public Itineraries page already reads packages from the DB live
(with a curated fallback if the API is down). Wiring the Expectations theme cards + Mapbox
map to the DB is the remaining follow-up.

## Password reset (self-service)

`forgot-password` generates a short-lived reset JWT and emails a link to
`FRONTEND_BASE_URL/reset-password?token=…` via Resend; `reset-password` verifies the token,
sets the new bcrypt password, and signs the traveller in. It needs:

- `RESEND_API_KEY` (already set — reused from the brochure feature).
- `FRONTEND_BASE_URL` — the main website's URL, used to build the reset link
  (added to `.env`, defaults to `http://localhost:5173`). Set this to your live domain in production.
- `RESET_EXPIRE_MINUTES` — optional, defaults to 30.

## Sign-up options

Travellers can now create their own accounts two ways:

- **Email + password** — the dashboard's "Create an account" form → `POST /api/auth/register`.
- **Continue with Google** — the dashboard's Google button → `POST /api/auth/google`.

Both create a row in `travellers` and return a login token. A Google account has a
null `hashed_password` and `auth_provider = 'google'`; if someone later signs in with
Google using an email that already registered with a password, the two are linked.

### If you already created the tables manually

The `travellers` table gained three columns. On an existing database, run:

```sql
ALTER TABLE travellers ALTER COLUMN hashed_password DROP NOT NULL;
ALTER TABLE travellers ADD COLUMN auth_provider VARCHAR(20) NOT NULL DEFAULT 'email';
ALTER TABLE travellers ADD COLUMN google_sub VARCHAR(255) UNIQUE;
```

(Fresh databases created by `create_all` / `seed.py` already include these.)

### Enabling Google Sign-In

1. In the [Google Cloud console](https://console.cloud.google.com/) → APIs & Services →
   Credentials, create an **OAuth 2.0 Client ID** of type **Web application**.
2. Under *Authorized JavaScript origins*, add the dashboard's origin
   (e.g. `http://localhost:3000` for dev, and your live domain for production).
3. Copy the generated **Client ID** into both:
   - backend `.env` → `GOOGLE_CLIENT_ID=...`
   - dashboard `.env.local` → `VITE_GOOGLE_CLIENT_ID=...`
4. Restart both servers. The Google button appears automatically once
   `VITE_GOOGLE_CLIENT_ID` is set (it stays hidden while empty).

## 1. Fix the database connection (required)

The `DATABASE_URL` in `.env` currently fails authentication:

```
FATAL: password authentication failed for user "postgres"
```

Update `.env` with the correct Postgres password so the URL looks like:

```
DATABASE_URL=postgresql://postgres:YOUR_REAL_PASSWORD@localhost:5432/RIL-DB
```

Confirm the `RIL-DB` database exists (create it in pgAdmin/psql if not).

## 2. Install dependencies

```
pip install -r requirements.txt
```

(New: `bcrypt`, `python-jose[cryptography]`.)

## 3. Create tables + seed the demo traveller

```
python seed.py
```

This prints the login credentials it created:

```
email:    harrison.sterling@heritage-travels.com
password: traveller123
```

Tables are also auto-created on server startup, but `seed.py` is what inserts data.

## 4. Run the API

```
uvicorn app.main:app --reload --port 8000
```

Interactive docs: http://localhost:8000/docs

## 5. Run the traveller dashboard

In the dashboard project (`traveler-dashboard/`):

```
npm install
npm run dev        # http://localhost:3000
```

It reads the backend URL from `.env.local` (`VITE_API_URL=http://localhost:8000`),
already created. Log in with the seeded credentials above.

## Notes

- `JWT_SECRET` and `JWT_EXPIRE_MINUTES` were appended to `.env`. Keep `JWT_SECRET`
  secret; change it to rotate all tokens. Tokens last 24h by default.
- Adding real travellers: insert rows into `travellers` with a hashed password —
  reuse `app.core.security.hash_password("plain-text")` (see `seed.py`).
- For production schema changes, switch from `create_all` to Alembic migrations.
