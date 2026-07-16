# MonaLearn — project bundle

Everything designed so far, organized as a real project rather than loose
files. Each layer uses the language/framework suited to it, per the spec's
Technology Requirements section:

```
monalearn-platform/
├── frontend/          HTML / CSS / JS  — the nine UI prototypes
│   ├── landing.html       Marketing landing page
│   ├── login.html         Login / signup
│   ├── dashboard.html     Student dashboard (auth-gated)
│   ├── tutor.html         AI Tutor chat interface
│   ├── simulation.html    Business Simulation Environment (Venture Sim)
│   ├── marketplace.html   Course marketplace + course detail view
│   ├── admin.html         Admin console (auth + role gated)
│   ├── instructor.html    Instructor console (auth + role gated)
│   ├── verify.html        Public certificate verification page (no login required)
│   ├── auth.js            Shared auth helper (token storage, authFetch, requireAuthOrDemo)
│   └── vercel.json        Clean-URL routing for the pages above
├── backend/           Python / FastAPI — API scaffold
│   ├── app/
│   │   ├── main.py            FastAPI app + router wiring
│   │   ├── models.py          Pydantic models (API request/response shapes)
│   │   ├── db.py              SQLAlchemy engine/session setup
│   │   ├── db_models.py       SQLAlchemy ORM models (User, Course, Enrollment, Certificate, ...)
│   │   ├── auth.py            Password hashing, JWT issuance, auth dependencies
│   │   └── routers/
│   │       ├── auth.py            Signup, login, /me
│   │       ├── admin.py           Admin-only endpoints (guarded by role check)
│   │       ├── instructor.py      Instructor-only endpoints (guarded by role check)
│   │       ├── billing.py         Stripe Checkout, webhook, billing portal
│   │       ├── courses.py         Course catalog (search-friendly, database-backed)
│   │       ├── certificates.py    Certificate verification (database-backed)
│   │       ├── dashboard.py       Dashboard data (auth-protected)
│   │       └── tutor.py           AI Tutor chat, proxied server-side
│   ├── schema.sql             Raw PostgreSQL DDL, mirrors db_models.py
│   ├── seed_db.py             Populates academies/courses/lessons/demo users/certificates
│   ├── requirements.txt
│   └── .env.example
├── automation/        Python — standalone scheduled/batch scripts
│   ├── generate_lesson_content.py   AI Content Creation System (draft lessons)
│   ├── resource_intelligence.py     AI Resource Intelligence System (source checks)
│   └── requirements.txt
├── .github/workflows/ CI + push-to-deploy + scheduled resource checks
└── render.yaml         Render blueprint (backend + cron job)
```

## What's real vs. illustrative

Be clear-eyed about what this bundle actually is: a well-organized
**prototype**, not a deployed product.

- **Frontend** — fully built, functional in the browser.
  - `tutor.html` makes real calls to Claude when opened inside a Claude.ai
    artifact (that environment proxies and authenticates the request for
    you). Opened as a plain local file outside Claude.ai, that call will
    fail — there's no key or proxy behind it there.
  - `simulation.html` runs entirely client-side with its own in-memory
    state (budget, team, revenue history) and doesn't call the backend.
  - `marketplace.html` and `verify.html` follow a live-fetch-with-fallback
    pattern: they try the real backend first (`GET /api/courses`,
    `GET /api/certificates/{id}`) and fall back to a built-in copy of the
    same sample data if that fails, so both still work standalone. A small
    badge shows which one is actually in use ("Live API" vs "Demo data").
    The embedded fallback data and the backend's in-memory data are kept
    field-for-field identical by hand — there's no single source of truth
    yet, so edit both if you change a course or certificate.
  - `dashboard.html`, `admin.html`, and `instructor.html` are genuinely
    auth-gated (see "Frontend auth wiring" below) — no token redirects to
    `login.html`, unless `?demo=1` is in the URL, which bypasses the gate
    entirely for previews.
  - `admin.html`'s Overview/Courses/Revenue/AI Monitoring tabs are still
    mock data — only the Students tab calls a real endpoint
    (`/api/admin/users`) once you're logged in as an admin.
  - `instructor.html`'s Overview and My Courses tabs call real endpoints
    (`/api/instructor/overview`, `/api/instructor/courses`) once you're
    logged in as an instructor — course creation actually writes a new row
    to the database now (always as a `draft`, pending review), not just to
    the page's local state. Sessions/mentorship on that page are still
    local-only; nothing about a booking or a scheduled live session
    persists anywhere.
- **Backend** — a genuine, runnable FastAPI app with working routes and real
  auth. `courses.py` and `certificates.py` now genuinely query the database
  (`schema.sql`/`db_models.py`) instead of an in-memory list — run
  `python seed_db.py` once against your database to populate it with the
  same sample courses, lessons, demo users, and certificates that used to
  be hardcoded in Python. The API response shape didn't change, so
  `marketplace.html` and `verify.html` don't need any updates to keep
  working against it.
- **Automation** — the two scripts run for real if you supply an Anthropic
  API key. `resource_intelligence.py` only checks whether a URL is
  reachable; it isn't a scraper and doesn't evaluate content quality on its
  own — that part of the spec ("evaluate quality, remove outdated
  information") still needs either a human reviewer or a further
  LLM-scoring step layered on top.

## Frontend auth wiring

`dashboard.html`, `admin.html`, and `instructor.html` are genuinely gated,
not just decorated with a login-looking sidebar:

- No token and no `?demo=1` in the URL → redirected to `login.html`.
- `login.html` calls the real `/api/auth/login` and `/api/auth/signup`
  endpoints and stores the returned JWT via `auth.js`.
- Once on a gated page, it calls `GET /api/auth/me` to identify who's
  logged in, and renders their real name/plan/role.
  - `admin.html` checks `role === "admin"` and shows an "Admins only"
    screen instead of the console if it isn't.
  - `instructor.html` checks `role === "instructor"` (or `"admin"`) the
    same way.
- `admin.html`'s Students tab calls the real `GET /api/admin/users`, and
  `instructor.html`'s Overview tab calls the real
  `GET /api/instructor/overview`, both replacing their mock numbers when
  the call succeeds.

**To actually see this work:** run the backend, sign up through
`login.html`, then manually promote that account — there's no UI for this
yet, it's a raw SQL update:
```sql
UPDATE users SET role = 'admin' WHERE email = 'you@example.com';
-- or
UPDATE users SET role = 'instructor' WHERE email = 'you@example.com';
```

**The `?demo=1` escape hatch:** every gated page still works without a
backend at all via `dashboard.html?demo=1`, `admin.html?demo=1`, and
`instructor.html?demo=1` — that's what keeps these usable as Claude.ai
artifact previews and quick demos. The banner at the top of the page makes
it obvious when you're looking at sample data instead of a real session.

**Known limits, not hidden:** `auth.js` stores the token in `localStorage`,
the normal approach for a small multi-page site like this — but it will
silently fail to persist inside Claude.ai's artifact preview sandbox
specifically, since that iframe blocks storage access. It works normally
once these files are actually deployed or opened from disk, which is the
whole point of the file existing. There's also no token refresh (a token
just expires after 60 minutes and you log in again) and no "forgot
password" flow. `marketplace.html`, `tutor.html`, and `simulation.html`
aren't auth-gated at all — only the three pages that needed it most were
wired up.

## Running the backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # or your preferred env tool
pip install -r requirements.txt
cp .env.example .env      # add your real ANTHROPIC_API_KEY, DATABASE_URL, JWT_SECRET_KEY
python seed_db.py         # creates tables (if needed) and populates courses/certificates/demo users
uvicorn app.main:app --reload
```

Interactive API docs: http://127.0.0.1:8000/docs

`seed_db.py` prints the demo accounts it creates and their password
(`demo-password-123` for all of them, local testing only — this is not a
password to keep). Log in as `amara@example.com` to see a real student
with two real certificates attached, or `grace.instructor@example.com` to
see a real instructor account already linked to two real courses (MKT 132,
MKT 220) — try creating a new course from `instructor.html` while logged
in as her and watch it actually show up via `GET /api/instructor/courses`.

**Try the auth flow directly:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"amara@example.com","password":"a-real-password","full_name":"Amara K."}'
# -> { "access_token": "eyJ...", "token_type": "bearer" }

curl http://localhost:8000/api/dashboard/1 -H "Authorization: Bearer eyJ..."
```

**Database:** `schema.sql` is the real PostgreSQL DDL — run it by hand
(`psql monalearn -f schema.sql`) if you want migration history from day
one. For quick local testing, the backend also creates tables
automatically on startup (`init_db()` in `app/db.py`) against whatever
`DATABASE_URL` points to, falling back to a local SQLite file if it's
unset. That SQLite fallback only really works for the `users` table — the
`courses`/`lessons` tables use a genuine PostgreSQL `ARRAY` column that
SQLite can't represent, so point `DATABASE_URL` at real Postgres before
touching those.

Also missing on purpose: no refresh tokens, no password reset flow, no
email verification, and `create_all()` instead of real Alembic migrations
— fine for a prototype, not fine once a database has real rows in it you
can't afford to lose to a schema change.

## Running the automation scripts

```bash
cd automation
pip install -r requirements.txt
cp ../backend/.env.example .env    # add your real ANTHROPIC_API_KEY

python generate_lesson_content.py --code "MKT 132" --topic "Conversion funnels" --level Beginner
python resource_intelligence.py
```

## Billing

The landing page's Basic/Professional/Premium buttons now call a real
Stripe Checkout flow instead of doing nothing:

- Click a plan → if you're not logged in, you're sent to `login.html` and
  land right back on checkout after (`?checkout=basic` etc. round-trips
  through the login redirect).
- `POST /api/billing/create-checkout-session` creates or reuses a Stripe
  customer and returns a Checkout URL to redirect to.
- `POST /api/billing/webhook` is what actually updates `User.plan` and the
  `subscriptions` table — Stripe calls this after a successful payment, not
  the frontend, which is the correct place for that logic to live.
- `GET /api/billing/portal` (wired to "Manage plan" on `dashboard.html`)
  opens Stripe's hosted billing portal for managing or canceling.

**Read this before trusting it:** unlike the rest of this backend, `billing.py`
has never actually been run against Stripe from this environment — there's
no network access here to test it against a real (even test-mode) Stripe
account. It's written correctly against the real Stripe Python SDK, with
signature verification on the webhook and a clear 500 instead of a crash
if `STRIPE_SECRET_KEY` isn't set, but "compiles and looks right" is a lower
bar than "verified working," and this is the one piece in the whole bundle
where that gap hasn't been closed. Test it against Stripe test mode
(`stripe listen --forward-to localhost:8000/api/billing/webhook`) before
relying on it.

To actually use it: create a Stripe account, three recurring Prices for
Basic/Professional/Premium, and set `STRIPE_SECRET_KEY`,
`STRIPE_WEBHOOK_SECRET`, and the three `STRIPE_PRICE_*` variables in `.env`.



## Deploying

This repo is set up for push-to-deploy: Vercel for the frontend, Render for
the backend and the recurring resource-check job, GitHub Actions as the CI
gate in between.

**1. Push this whole folder to a GitHub repo.**

**2. Frontend → Vercel**
- New Project in Vercel, import the repo.
- Set the project's Root Directory to `frontend`.
- No build command needed — it's static HTML. Deploy.
- `frontend/vercel.json` gives you clean URLs: `/`, `/dashboard`, `/tutor`,
  `/simulation`, `/marketplace`, `/admin`, `/verify`.
- Every push to `main` auto-deploys via Vercel's own GitHub integration —
  no Actions workflow needed for this side.

**3. Backend + cron job → Render**
- New > Blueprint in Render, point it at the repo. It reads `render.yaml`
  and provisions both `monalearn-api` (the FastAPI service) and
  `monalearn-resource-intelligence` (the scheduled source-checker)
  automatically.
- Add your real `ANTHROPIC_API_KEY`, `DATABASE_URL`, `JWT_SECRET_KEY`, and
  (once billing is actually tested — see "Billing" above) the Stripe keys
  in the Render dashboard for `monalearn-api` (Settings > Environment).
  They're intentionally left out of `render.yaml`.
- Optional but recommended once this is more than a demo: turn OFF
  "Auto-Deploy" on `monalearn-api` in Render, and instead let
  `.github/workflows/deploy-backend.yml` trigger deploys — that way a
  broken backend never goes live, because the deploy only fires if the
  compile check passes first. To enable that, copy the service's Deploy
  Hook URL from Render and add it to the repo as a secret named
  `RENDER_DEPLOY_HOOK_URL` (GitHub repo Settings > Secrets and variables >
  Actions). If you skip this, Render's own Auto-Deploy is enough on its own.

**4. CI → GitHub Actions**
Three workflows come with the repo, all under `.github/workflows/`:
- `ci.yml` — runs on every push and PR, compile-checks the Python and
  confirms all frontend pages exist.
- `deploy-backend.yml` — the push-to-deploy gate described above.
- `resource-intelligence.yml` — runs the source-reachability check every 6
  hours for free on GitHub's schedule, as an alternative to Render's cron
  job. Use one or the other, not both, so it doesn't run twice.

**Costs to expect once this is live, not just a demo:** Vercel's free tier
covers the frontend comfortably. Render's Starter plan for the API is
$7/month (the free tier works for showing people but sleeps after 15
minutes idle, with a slow first request after). The cron job costs nothing
extra on Render's usage-based cron pricing for a check this small, or
nothing at all if you use the GitHub Actions version instead.

## Not included yet

Straight from the original spec, still outstanding: the RAG/vector-database
layer for the Resource Intelligence System, the instructor console's
session-scheduling and mentorship-booking forms (course creation now
persists for real, sessions still don't), and billing exists in code but
hasn't been verified against a live Stripe account (see "Billing" above —
that's the one piece in this bundle where "written correctly" and "tested
working" aren't the same claim). Auth covers three of the nine frontend
pages. `admin.py`'s user list and `dashboard.py`'s stats are still mock
data layered on top of real auth — courses, certificates, and instructor
course creation are the resources reading from and writing to the database
end to end so far.
