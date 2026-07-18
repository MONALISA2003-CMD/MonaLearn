"""
Temporary, phone-deployable seeding endpoint.

Exists so the database can be seeded without shell/terminal access — visit
this URL once in a browser with the right key, and it runs seed_db.py's
seed() function on the server. This is NOT how you'd want to seed a real
production system long-term (a properly protected admin CLI or one-off
job is safer, since anyone who guesses/leaks SEED_SECRET can re-run this),
but it's a pragmatic bridge for phone-only deployment where a terminal
genuinely isn't available. Consider removing this route, or at least
rotating SEED_SECRET, once you've seeded once and have another way in.

seed_db.seed() is idempotent (checks for existing rows before inserting),
so visiting this twice by accident won't duplicate anything.
"""
import os

from fastapi import APIRouter, HTTPException, Query

import seed_db

router = APIRouter()


@router.get("/seed")
def run_seed(key: str = Query(..., description="Must match SEED_SECRET in the environment")):
    expected = os.environ.get("SEED_SECRET")
    if not expected:
        raise HTTPException(status_code=500, detail="SEED_SECRET isn't set on the server yet.")
    if key != expected:
        raise HTTPException(status_code=403, detail="Invalid key.")
    seed_db.seed()
    return {"status": "seed complete — try /api/courses to confirm"}
