from fastapi import FastAPI
import importlib
import logging

from app.database import init_db  # ensure this exists and registers startup/shutdown

app = FastAPI(title="Lumen Bank API", version="1.0")

# Import auth router (must exist)
try:
    auth_mod = importlib.import_module("app.routers.auth")
    app.include_router(auth_mod.router)
except ModuleNotFoundError:
    logging.warning("Auth router (app.routers.auth) not found — auth endpoints won't be available.")

# Try several possible module names for accounts/transactions router and include the first found
_account_router_candidates = [
    "app.routers.accounts",
    "app.routers.crud",
    "app.routers.transactions",
    "app.routers.accounts_router",
]

for _mod_name in _account_router_candidates:
    try:
        mod = importlib.import_module(_mod_name)
        app.include_router(mod.router)
        break
    except ModuleNotFoundError:
        continue
else:
    logging.warning(
        "No accounts router found among candidates %s. Accounts endpoints will be unavailable.",
        _account_router_candidates,
    )

# initialize DB / ORMs
init_db(app)
