import json
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .config import ALLOWED_ORIGINS, API_PREFIX
from .routers import customers, dashboard, inventory, orders, products

ROUTER_MODULES = (products, customers, orders, dashboard, inventory)
# Bare resource roots, e.g. "/products", used to redirect old-style requests.
UNVERSIONED_PREFIXES = tuple(m.router.prefix for m in ROUTER_MODULES)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("api")

app = FastAPI(title="Inventory & Order Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def redirect_to_versioned(request: Request, call_next):
    """Forward unversioned requests (e.g. POST /products) to the latest API
    version. A 307 keeps the method and body intact."""
    path = request.url.path
    if path != API_PREFIX and not path.startswith(API_PREFIX + "/"):
        if any(path == p or path.startswith(p + "/") for p in UNVERSIONED_PREFIXES):
            target = API_PREFIX + path
            if request.url.query:
                target = f"{target}?{request.url.query}"
            return RedirectResponse(target, status_code=307)
    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Emit a structured log line for every request."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        json.dumps(
            {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            }
        )
    )
    return response


# All resource routes are versioned under /api/v1.
for module in ROUTER_MODULES:
    app.include_router(module.router, prefix=API_PREFIX)


@app.get("/health")
def health():
    return {"status": "healthy"}
