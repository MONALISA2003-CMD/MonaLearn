"""
Admin-only endpoints.

Just enough to demonstrate the get_current_admin_user dependency actually
guarding something — this is the real backend counterpart to the Students
tab in frontend/admin.html, which currently reads from its own hardcoded
JS array instead of calling this.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_admin_user
from app.db import get_db
from app.db_models import User
from app.routers.auth import UserOut

router = APIRouter()


@router.get("/users", response_model=list[UserOut])
def list_users(_: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()
