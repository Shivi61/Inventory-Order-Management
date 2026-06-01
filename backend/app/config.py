import os

# Secret used for signing (reserved for auth/session features).
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

# Comma-separated list of origins allowed by CORS. CORS_ORIGINS is kept as a
# fallback for older configs.
_origins = os.getenv("ALLOWED_ORIGINS", os.getenv("CORS_ORIGINS", "http://localhost:5173"))
ALLOWED_ORIGINS = [o.strip() for o in _origins.split(",") if o.strip()]

# Products at or below this quantity are flagged as low stock.
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))

# All API routes live under this prefix.
API_PREFIX = "/api/v1"
