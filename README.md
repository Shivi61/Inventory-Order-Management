# Inventory & Order Management System

A production-oriented full-stack app for managing products, customers, orders and
inventory tracking.

## Tech stack

| Layer            | Technology                                            |
| ---------------- | ----------------------------------------------------- |
| Frontend         | React 18 (Vite, JavaScript), React Router, Axios      |
| Backend          | Python, FastAPI, SQLAlchemy 2, Pydantic v2, Uvicorn   |
| Database         | PostgreSQL (Alembic migrations)                       |
| Containerization | Docker (multi-stage builds), Docker Compose           |
| Web server       | Nginx (serves the built frontend)                     |
| Tests            | Pytest (backend), Vitest + Testing Library (frontend) |

## Architecture

Three containerized services orchestrated with Docker Compose. The frontend is a
static React build served by Nginx; it talks to the FastAPI backend over JSON/HTTP;
the backend persists everything in PostgreSQL.

```
        ┌─────────────────┐      JSON / HTTP      ┌──────────────────────┐     SQL    ┌──────────────┐
        │  React + Vite   │ ───── /api/v1/* ────▶ │   FastAPI (Uvicorn)  │ ─────────▶ │  PostgreSQL  │
 user ▶ │  served by Nginx│ ◀──── responses ───── │                      │ ◀───────── │              │
        └─────────────────┘                       └──────────────────────┘            └──────────────┘
          frontend service                          backend service                     db service
          (Vercel in prod)                           (Render in prod)                    (Neon in prod)
```

**Request flow (backend):**

```
HTTP request
   │
   ▼
CORS middleware ─▶ version-redirect middleware (/-bare → /api/v1) ─▶ structured logging middleware
   │
   ▼
Router (products / customers / orders / dashboard / inventory-transactions)
   │
   ▼
Pydantic schema validation  ──▶  business logic  ──▶  SQLAlchemy models / session
   │                                                        │
   ▼                                                        ▼
JSON response                                          PostgreSQL
```

- **Routers** ([backend/app/routers/](backend/app/routers/)) define endpoints; each is mounted under `/api/v1`.
- **Schemas** ([schemas.py](backend/app/schemas.py)) validate input and shape output with Pydantic.
- **Models** ([models.py](backend/app/models.py)) are SQLAlchemy ORM tables; a portable `GUID` type gives UUID keys on Postgres (and works under SQLite in tests).
- **Migrations** are Alembic; the container runs `alembic upgrade head` on startup before serving.
- **Middleware** handles CORS, redirects unversioned paths to the current API version, and emits structured request logs.

## Features

### Product management
- Create, list, retrieve, update, soft-delete
- Unique SKU (enforced in code → `409`, and at the DB level)
- Price must be greater than 0; quantity can never be negative (Pydantic + DB CHECK)
- Server-side **search** (name or SKU) and **pagination**

### Customer management
- Create, list, retrieve, soft-delete
- Unique email with format validation (→ `409` on duplicate)

### Order management
- Create orders with **multiple line items**
- **Status workflow**: pending → confirmed → completed / cancelled (`PATCH /orders/{id}/status`)
- Cancelling an order **restores stock** and **keeps the record** (status set to `cancelled`)
- Order total is **always computed by the backend** (clients cannot override it)
- Unit prices are snapshotted at order time

### Inventory & business rules
- Orders are rejected when stock is insufficient → `400 {"message": "Insufficient inventory"}`
- Placing an order automatically **reduces stock**, all in one transaction
- **Inventory transaction history** — every movement is logged (Product Added /
  Stock Updated / Order Created / Order Cancelled) with a signed quantity change

### Dashboard & analytics
- Totals for products, customers, orders, plus a low-stock count and the low-stock list

### Production-oriented engineering
- **API versioning** under `/api/v1` (bare paths 307-redirect to the current version)
- **UUID primary keys** and `created_at` / `updated_at` **audit fields** on all tables
- **Soft deletes** for products and customers (records retained, hidden from queries)
- **Alembic migrations** applied automatically on container startup
- **Structured JSON request logging** (method, path, status, duration)
- **OpenAPI / Swagger** docs at `/docs`; **health check** at `/health`
- Database **indexes** on `sku`, `name`, and `email`
- **Environment-based configuration** — no hardcoded credentials

### Frontend & UX
- Responsive layout for desktop, tablet and mobile
- Pages: Dashboard, Products, Customers, Orders, Inventory history
- Client-side **form validation**, **toast** success/error messages, **skeleton loaders**, empty states
- Organized component structure with React hooks for state management

### Testing & tooling
- Backend **Pytest** suite (products, customers, orders, inventory, dashboard, versioning)
- Frontend **Vitest + Testing Library** component tests
- Idempotent database **seed script** for sample data

## Project layout

```
backend/
  app/
    routers/      # products, customers, orders, dashboard, inventory-transactions
    models.py     # SQLAlchemy ORM models
    schemas.py    # Pydantic request/response schemas
    config.py     # env-based settings
    inventory.py  # stock-movement helper
    seed.py       # sample data
    main.py       # app, middleware, router wiring
  alembic/        # migrations
  tests/          # pytest suite
  Dockerfile      # multi-stage build
frontend/
  src/
    pages/        # Dashboard, Products, Customers, Orders, Inventory
    components/   # Nav, Modal, Toast, Skeleton
    api/          # axios client
  Dockerfile      # build -> nginx
docker-compose.yml
render.yaml       # backend deploy blueprint
```

## Running locally with Docker

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

The backend container runs `alembic upgrade head` on startup, then serves the API.
PostgreSQL data is kept in a named volume (`pgdata`).

> If port 5173 or 8000 is already in use, set `FRONTEND_PORT` / `BACKEND_PORT`
> in `.env` (and update `VITE_API_URL` to match the backend port).

## API overview

All routes are versioned under `/api/v1`. For convenience, unversioned requests
(e.g. `POST /products`) are redirected (HTTP 307, preserving method and body) to
the current version, so both `/products` and `/api/v1/products` work.

| Method | Path                              | Description                       |
| ------ | --------------------------------- | --------------------------------- |
| POST   | /api/v1/products                  | Create a product                  |
| GET    | /api/v1/products                  | List products (`?search=&page=&page_size=`) |
| GET    | /api/v1/products/{id}             | Get a product                     |
| PUT    | /api/v1/products/{id}             | Update a product                  |
| DELETE | /api/v1/products/{id}             | Soft-delete a product             |
| POST   | /api/v1/customers                 | Create a customer                 |
| GET    | /api/v1/customers                 | List customers                    |
| GET    | /api/v1/customers/{id}            | Get a customer                    |
| DELETE | /api/v1/customers/{id}            | Soft-delete a customer            |
| POST   | /api/v1/orders                    | Create an order                   |
| GET    | /api/v1/orders                    | List orders                       |
| GET    | /api/v1/orders/{id}               | Get an order                      |
| PATCH  | /api/v1/orders/{id}/status        | Change order status               |
| DELETE | /api/v1/orders/{id}               | Cancel an order (returns stock)   |
| GET    | /api/v1/dashboard                 | Totals + low-stock products       |
| GET    | /api/v1/inventory-transactions    | Stock movement history (`?product_id=`) |
| GET    | /health                           | Health check                      |

### Example: create an order

```json
POST /api/v1/orders
{
  "customer_id": "5f3b…",
  "items": [
    { "product_id": "9ac1…", "quantity": 2 },
    { "product_id": "1de7…", "quantity": 1 }
  ]
}
```

If stock is insufficient the API responds `400 {"message": "Insufficient inventory"}`.

## Configuration

All configuration comes from environment variables (see `.env.example`):

| Variable              | Used by  | Purpose                                  |
| --------------------- | -------- | ---------------------------------------- |
| `DATABASE_URL`        | backend  | PostgreSQL connection string             |
| `ALLOWED_ORIGINS`     | backend  | Comma-separated CORS origins             |
| `SECRET_KEY`          | backend  | App secret (reserved for auth/sessions)  |
| `LOW_STOCK_THRESHOLD` | backend  | Quantity at/below which stock is "low"   |
| `VITE_API_URL`        | frontend | Backend base URL (baked in at build)     |

No credentials are hardcoded anywhere.

## Seeding sample data

To populate the database with a few products, customers and orders:

```bash
# with docker compose running
docker compose exec backend python -m app.seed

# or locally (after migrations)
cd backend && python -m app.seed
```

The seed is idempotent — it does nothing if products already exist.

## Database migrations

Schema is managed with Alembic.

```bash
cd backend
alembic upgrade head          # apply migrations
alembic revision --autogenerate -m "describe change"   # create a new one
```

## Tests

```bash
# backend
cd backend && pip install -r requirements.txt && pytest

# frontend
cd frontend && npm install && npm test
```

## Running without Docker

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/inventory
alembic upgrade head
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for publishing the backend image to Docker Hub
and deploying to Render (backend) and Vercel/Netlify (frontend).
