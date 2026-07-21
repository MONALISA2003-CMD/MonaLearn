"""
Temporary, phone-deployable maintenance endpoints.

Exists so the database can be seeded and users promoted without
shell/terminal access — visit a URL once in a browser with the right key.
This is NOT how you'd want to run a real production system long-term (a
properly protected admin CLI or one-off job is safer, since anyone who
guesses/leaks SEED_SECRET can re-run these), but it's a pragmatic bridge
for phone-only deployment where a terminal genuinely isn't available.
Consider removing these routes, or at least rotating SEED_SECRET, once
you have another way in (e.g. a real admin panel, or occasional access
to a computer with psql).

seed_db.seed() is idempotent, so visiting /seed twice by accident won't
duplicate anything. /promote is safe to re-run too — it just sets a role.
"""
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import seed_db
from app.db import get_db
from app.db_models import User

router = APIRouter()


def _check_key(key: str):
    expected = os.environ.get("SEED_SECRET")
    if not expected:
        raise HTTPException(status_code=500, detail="SEED_SECRET isn't set on the server yet.")
    if key != expected:
        raise HTTPException(status_code=403, detail="Invalid key.")


@router.get("/seed")
def run_seed(key: str = Query(..., description="Must match SEED_SECRET in the environment")):
    _check_key(key)
    seed_db.seed()
    return {"status": "seed complete — try /api/courses to confirm"}


@router.get("/promote")
def promote_user(
    email: str = Query(..., description="Email of the account to promote"),
    role: str = Query(..., description="student, instructor, or admin"),
    key: str = Query(..., description="Must match SEED_SECRET in the environment"),
    db: Session = Depends(get_db),
):
    _check_key(key)
    if role not in ("student", "instructor", "admin"):
        raise HTTPException(status_code=400, detail="role must be student, instructor, or admin")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"No account found for {email}")
    user.role = role
    db.commit()
    return {"status": f"{email} is now role='{role}'"}

