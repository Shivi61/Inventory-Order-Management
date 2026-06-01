import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine
from .routers import products

# Create tables on startup. For a small project this is simpler than wiring up
# Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory & Order Management API")

# Allowed origins come from the environment so the deployed frontend domain can
# be added without touching the code.
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(products.router)


@app.get("/health")
def health():
    return {"status": "ok"}
