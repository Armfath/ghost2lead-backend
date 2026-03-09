## Ghost2Lead Backend

Ghost2Lead is a FastAPI-based backend that powers lead capture, user management, and analytics for the Ghost2Lead platform. It exposes a versioned HTTP API, background workers for async jobs, and integrates with Postgres, Redis, Celery, and PostHog.

### Tech stack

- **Language**: Python 3.12+
- **Web framework**: FastAPI
- **Database**: PostgreSQL (via SQLAlchemy + asyncpg)
- **Caching / queues**: Redis
- **Background jobs**: Celery + worker container
- **Migrations**: Alembic
- **API docs**: Scalar UI (served from the FastAPI app)
- **Packaging / tooling**: `uv` (via `uv.lock`), `pytest`, `ruff`

### Local development

#### 1. Prerequisites

- **Python**: 3.12 or later
- **uv**: recommended for dependency management (`pip install uv`)
- **Docker & Docker Compose**: for running Postgres, Redis, and the worker

#### 2. Environment variables

Create a `.env` file in the project root, based on `.env.example`:

```bash
cp .env.example .env
```

Then fill in:

- **Database**: `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_SERVER`, `DATABASE_PORT`, `DATABASE_NAME`
- **Redis**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB_CELERY`, `REDIS_DB_OTP`, `REDIS_DB_TOKEN_BLACKLIST`
- **PostHog**: `POSTHOG_DATABASE_URL`, `POSTHOG_PROJECT_ID`, `POSTHOG_EVENTS_TABLE_NAME`
- **OpenAI**: `OPENAI_API_KEY`
- **Mail / OTP**: `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_FROM_NAME`, `MAIL_SERVER`, `MAIL_PORT`

Never commit real secrets; `.env.example` is the canonical reference.

#### 3. Install dependencies

You can use either `uv` (preferred) or plain `pip`.

- **With uv** (uses `pyproject.toml` / `uv.lock`):

```bash
uv sync
```

- **With pip** (uses `requirements.txt`):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 4. Run the stack with Docker

Spin up API, Postgres, Redis, and Celery worker:

```bash
docker compose up --build
```

This will:

- Start the API on `http://localhost:8000`
- Start Postgres on the internal `db` service
- Start Redis on the internal `redis` service
- Start a Celery worker container

To stop:

```bash
docker compose down
```

#### 5. Run the API without Docker

If you already have Postgres and Redis running locally and a virtualenv activated:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or, with plain `uvicorn`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The healthcheck endpoint will be available at:

- `GET http://localhost:8000/health`

### API docs

The OpenAPI schema is exposed at:

- `GET {API_PREFIX}/openapi.json` (configured via `app/core/config.py`)

Scalar API docs are served by the backend at:

- `GET {API_PREFIX}/docs`

`API_PREFIX` and `API_V1` are defined in `app/core/config.py` and used by `app/main.py` and `app/api/v1/router.py`.

### Background worker

Celery tasks are defined under:

- `app/worker/tasks.py`

In Docker, the worker is started via the `celery` service (see `compose.yaml`).

To run a worker manually (with env vars set and Redis reachable):

```bash
celery -A app.worker.tasks:celery_app worker --loglevel=info
```

### Database migrations

Alembic is configured via `alembic.ini` and the `migrations/` folder.

- **Run migrations**:

```bash
alembic upgrade head
```

- **Create a new migration**:

```bash
alembic revision --autogenerate -m "describe change"
```

### Testing & linting

- **Run tests** (pytest discovers tests under `tests/`):

```bash
uv run pytest
```

or, if using a virtualenv with `pip`:

```bash
pytest
```

- **Run Ruff** (linting, as configured in `pyproject.toml`):

```bash
uv run ruff check .
```

### Project structure

High-level layout:

- **`app/main.py`**: FastAPI app, CORS, healthcheck, docs, router mounting
- **`app/api/v1`**: versioned API routers (e.g. auth, lead, stats)
- **`app/models`**: SQLAlchemy models
- **`app/schemas`**: Pydantic schemas / DTOs
- **`app/repository`**: data access layer
- **`app/services`**: business logic layer
- **`app/core`**: configuration, DB, Redis, exceptions, dependencies
- **`app/worker`**: Celery app and tasks
- **`scripts`**: entrypoint and healthcheck scripts
- **`migrations`**: Alembic migration scripts

The goal is **strict separation of concerns**: API layer → services → repositories → database.

### Deployment

For production, use `compose.prod.yaml` together with pre-built images:

1. Build and push images to a registry (e.g. GHCR) for:
   - `api` backend
   - `worker` Celery worker
2. Set `COMPOSE_IMAGE_BASE` to your image base, for example:

```bash
export COMPOSE_IMAGE_BASE=ghcr.io/myorg/ghost2lead-backend
docker compose -f compose.prod.yaml up -d
```

Make sure to provide a production-grade `.env` file and external Postgres/Redis services as needed.

### Conventions

- **Code style**: enforced by Ruff (`pyproject.toml`)
- **Tests**: add unit tests for services and repositories, plus smoke/functional tests under `tests/`
- **Logging & monitoring**: use structured logs locally; wire up Sentry/Logtail or similar in production

