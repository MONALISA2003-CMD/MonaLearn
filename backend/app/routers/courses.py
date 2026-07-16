"""
Course catalog endpoint — now reading from the real database instead of a
hardcoded Python list. Run `python seed_db.py` once against your database
before expecting this to return anything.

Backs the course marketplace (frontend/marketplace.html) and the landing
page's ledger search. marketplace.html still keeps its own embedded
fallback copy of this same data for when the backend isn't reachable at
all — see the README's note on that.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db import get_db
from app.db_models import Academy, Course as CourseRow
from app.models import Course

router = APIRouter()


def _format_duration(minutes: int) -> str:
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins:02d}m" if hours else f"{mins}m"


def _to_api_course(row: CourseRow) -> Course:
    return Course(
        code=row.code,
        title=row.title,
        academy=row.academy.name,
        level=row.level,
        languages=row.languages,
        status=row.status,
        duration=_format_duration(row.duration_minutes),
        duration_minutes=row.duration_minutes,
        description=row.description or "",
        learn_outcomes=row.learn_outcomes,
        lessons=[lesson.title for lesson in row.lessons],
    )


@router.get("", response_model=list[Course])
def list_courses(q: Optional[str] = Query(None, description="Filter by code, title, or academy"), db: Session = Depends(get_db)):
    query = db.query(CourseRow).join(Academy)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(CourseRow.code.ilike(like), CourseRow.title.ilike(like), Academy.name.ilike(like)))
    rows = query.order_by(CourseRow.code).all()
    return [_to_api_course(r) for r in rows]


@router.get("/{code}", response_model=Course)
def get_course(code: str, db: Session = Depends(get_db)):
    row = db.query(CourseRow).join(Academy).filter(CourseRow.code.ilike(code)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Course not found. Have you run seed_db.py?")
    return _to_api_course(row)
