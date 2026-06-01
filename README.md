# Inventory & Order Management System

A full-stack app for managing products, customers and orders with inventory tracking.

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL (Alembic migrations)
- **Frontend:** React (Vite)
- **Containerized** with Docker and Docker Compose

## Features

- Product management with search and pagination; unique SKUs; price must be > 0
- Customer management with unique emails
- Orders with multiple line items and a status workflow
  (pending / confirmed / completed / cancelled)
- Inventory rules:
  - product quantity can never go negative
  - an order is rejected if stock is insufficient
  - placing an order automatically reduces stock
  - cancelling an order returns the stock and keeps the order on record
  - the order total is always calculated on the backend
- Every stock movement is recorded as an inventory transaction (audit history)
- UUID primary keys and `created_at` / `updated_at` audit fields
- Soft deletes for products and customers (records are kept, just hidden)
- Dashboard with totals and a low-stock list
- Structured request logging
- Tests: Pytest (backend) and Vitest + Testing Library (frontend)

## Project layout

```
backend/    FastAPI service + Alembic migrations + tests
frontend/   React (Vite) app + tests
docker-compose.yml
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

All routes are versioned under `/api/v1`.

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
