# The BT Math - E-Learning Platform

Django + DRF e-learning platform for Nepali students (+2, IOE, Bachelors, Masters). Students browse courses, view free previews, and buy individual courses (one-time, lifetime access) via eSewa or Khalti (sandbox). Server-rendered Bootstrap 5 templates and a DRF API (with Swagger/OpenAPI docs) share the same project.

## Stack

- Django 6 + Django REST Framework
- PostgreSQL (falls back to SQLite automatically if `DATABASE_URL` isn't set, so you can run it immediately)
- drf-spectacular for OpenAPI schema + Swagger UI
- SimpleJWT for API auth, Django session auth for the template site
- Custom `users.User` model (email + password login, no username)
- eSewa ePay v2 and Khalti ePayment v2, both in sandbox/test mode
- Bootstrap 5 (via CDN) for templates

## Project layout

```
config/settings/{base,dev,prod}.py   environment-based settings
apps/users/        custom User model, auth views, API
apps/catalog/      Category, Program, Course, Chapter, ContentItem + protected file serving
apps/orders/       Order/Purchase model, checkout, "My Courses" dashboard
apps/payments/     eSewa + Khalti sandbox integration (services/, views, callbacks)
apps/pages/        home, about, contact, terms, privacy
templates/         Bootstrap 5 templates for all of the above
```

## 1. Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## 2. Configure your `.env`

An `.env` file already exists at the project root with a generated `DJANGO_SECRET_KEY` and sensible dev defaults (SQLite, console email backend, eSewa's public sandbox test credentials). **You still need to fill in:**

| Variable | What to put there |
|---|---|
| `DATABASE_URL` | Uncomment and fill in your Postgres connection string once you've created a database (see below). Leave commented to keep using SQLite for now. |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Only needed if you switch `EMAIL_BACKEND` to SMTP to actually send password-reset emails (e.g. a Gmail address + [App Password](https://myaccount.google.com/apppasswords)). Leave blank to keep emails printed to the console. |
| `KHALTI_SECRET_KEY` | Sign up at https://test-admin.khalti.com/ and copy your **test** secret key. eSewa's test credentials are already filled in (they're publicly documented sandbox values); Khalti issues one per test account so you must get your own. |
| `DJANGO_ALLOWED_HOSTS` / `SITE_URL` | Update if you deploy somewhere other than `127.0.0.1`. |
| `CSRF_TRUSTED_ORIGINS` | Only needed once you deploy behind a real HTTPS domain. |

`.env.example` documents every variable if you need to recreate `.env` from scratch. `.env` is already git-ignored.

### Setting up PostgreSQL (optional for local dev, required before production)

```sql
CREATE DATABASE btmath;
CREATE USER btmath_user WITH PASSWORD 'changeme';
GRANT ALL PRIVILEGES ON DATABASE btmath TO btmath_user;
```

Then uncomment `DATABASE_URL` in `.env` with matching credentials.

## 3. Run migrations, create an admin user, and seed demo data

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo   # optional: creates the +2/IOE/Bachelors/Masters nav tree + one demo course
```

## 4. Run the dev server

```bash
python manage.py runserver
```

- Site: http://127.0.0.1:8000/
- Django admin: http://127.0.0.1:8000/admin/ (manage categories, programs, courses, chapters, content items, orders)
- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Raw OpenAPI schema: http://127.0.0.1:8000/api/schema/

## How content & payments work

- **Catalog**: Category -> Program -> Course -> Chapter -> ContentItem (PDF Notes / Past Question / Tutorial / Past Trick). Mark a `Chapter` or `ContentItem` `is_free` in the admin to make it a free preview.
- **Secure file access**: paid `ContentItem.file` uploads are written to `private_media/` (outside `MEDIA_ROOT`, no public URL is ever wired to that folder). They're only ever served through `apps.catalog.views.ProtectedContentView`, which checks `is_free` / chapter `is_free` / an existing successful `Order` before streaming the file. There's no way to guess a direct URL to locked content.
- **Purchases**: one `Order` per course purchase attempt (`pending` -> `success`/`failed`). A course counts as purchased once it has a `success` order for that student - see `Course.user_has_access()`.
- **Payments**: `apps/payments/services/esewa.py` and `khalti.py` wrap the sandbox APIs (form-POST + signature for eSewa, initiate/lookup for Khalti). Both gateways redirect back into `apps.payments.views`, which independently re-verifies the transaction with the gateway (not just trusting the redirect) before marking the order successful and unlocking the course.

## API auth

- `POST /api/v1/register/` - create an account
- `POST /api/v1/token/` - obtain a JWT access/refresh pair (email + password)
- `POST /api/v1/token/refresh/`
- `GET/PATCH /api/v1/me/`
- `GET /api/v1/categories/`, `/api/v1/programs/`, `/api/v1/courses/` (public, read-only)
- `GET/POST /api/v1/orders/` (JWT or session auth required)

## What's intentionally out of scope (per the requirements doc)

Social login, an instructor role, subscriptions, and production payment credentials are all deliberately not implemented - see the "Out of Scope" section of the original requirements doc.
