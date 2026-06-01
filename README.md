# Inventory & Order Management System

A full-stack app for managing products, customers and orders with inventory tracking.

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Frontend:** React (Vite)
- **Containerized** with Docker and Docker Compose

## Features

- Product management (create, list, update, delete) with unique SKUs
- Customer management (create, list, delete) with unique emails
- Order creation with multiple line items
- Inventory rules:
  - product quantity can never go negative
  - an order is rejected if stock is insufficient
  - placing an order automatically reduces stock
  - cancelling an order returns the stock
  - the order total is always calculated on the backend
- Dashboard with totals and a low-stock list

## Project layout

```
backend/    FastAPI service
frontend/   React (Vite) app
docker-compose.yml
```

## Running locally with Docker

You need Docker and Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

PostgreSQL data is kept in a named volume (`pgdata`), so it survives restarts.

## Running the backend without Docker

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/inventory
uvicorn app.main:app --reload
```

## Running the frontend without Docker

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

## API overview

| Method | Path                  | Description                  |
| ------ | --------------------- | ---------------------------- |
| POST   | /products             | Create a product             |
| GET    | /products             | List products                |
| GET    | /products/{id}        | Get a product                |
| PUT    | /products/{id}        | Update a product             |
| DELETE | /products/{id}        | Delete a product             |
| POST   | /customers            | Create a customer            |
| GET    | /customers            | List customers               |
| GET    | /customers/{id}       | Get a customer               |
| DELETE | /customers/{id}       | Delete a customer            |
| POST   | /orders               | Create an order              |
| GET    | /orders               | List orders                  |
| GET    | /orders/{id}          | Get an order                 |
| DELETE | /orders/{id}          | Cancel an order (returns stock) |
| GET    | /dashboard/summary    | Totals + low-stock products  |

### Example: create an order

```json
POST /orders
{
  "customer_id": 1,
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 3, "quantity": 1 }
  ]
}
```

## Configuration

All configuration comes from environment variables (see `.env.example`):

| Variable            | Used by  | Purpose                                  |
| ------------------- | -------- | ---------------------------------------- |
| `DATABASE_URL`      | backend  | PostgreSQL connection string             |
| `CORS_ORIGINS`      | backend  | Comma-separated list of allowed origins  |
| `LOW_STOCK_THRESHOLD` | backend | Quantity at/below which stock is "low"  |
| `VITE_API_URL`      | frontend | Backend base URL (baked in at build)     |

No credentials are hardcoded anywhere.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions to publish the
backend image to Docker Hub and deploy to Render (backend) and Vercel/Netlify
(frontend).
