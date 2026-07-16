"""
Instructor endpoints.

/courses is now real: GET returns this instructor's actual courses from
the database (enrollment counts included), and POST actually creates a row
— always as a draft, since new courses go through review before appearing
in the marketplace. /overview and /payouts are still mock data layered on
top of a real role check; enrollments/payments aren't tracked yet, so
there's nothing real to compute those from.
"""
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_instructor_user
from app.db import get_db
from app.db_models import Academy, Course, Enrollment, User

router = APIRouter()

MOCK_OVERVIEW = {
    "students_taught": 1284,
    "courses_published": 3,
    "earnings_this_month": 940.50,
    "completion_rate": 68,
}

MOCK_PAYOUTS = [
    {"date": "2026-07-01", "amount": 940.50, "status": "paid"},
    {"date": "2026-06-01", "amount": 812.20, "status": "paid"},
    {"date": "2026-05-01", "amount": 765.90, "status": "paid"},
]

ACADEMY_PREFIX = {
    "Business & Entrepreneurship": "BUS",
    "Finance & Accounting": "FIN",
    "Marketing & Sales": "MKT",
    "Office Administration": "ADM",
    "Language Institute": "LANG",
}


class InstructorCourseOut(BaseModel):
    code: str
    title: str
    status: str
    students: int
    price: float
    academy: str


class CourseCreateRequest(BaseModel):
    title: str
    academy: str
    level: str
    price: float = 0
    description: str = ""


def _generate_course_code(db: Session, academy_name: str) -> str:
    prefix = ACADEMY_PREFIX.get(academy_name, "GEN")
    n = 500
    while True:
        code = f"{prefix} {n}"
        if not db.query(Course).filter(Course.code == code).first():
            return code
        n += 10


@router.get("/overview")
def get_overview(_: User = Depends(get_current_instructor_user)):
    return MOCK_OVERVIEW


@router.get("/courses", response_model=list[InstructorCourseOut])
def list_my_courses(current_user: User = Depends(get_current_instructor_user), db: Session = Depends(get_db)):
    rows = db.query(Course).filter(Course.instructor_id == current_user.id).order_by(Course.created_at.desc()).all()
    out = []
    for row in rows:
        student_count = db.query(Enrollment).filter(Enrollment.course_id == row.id).count()
        out.append(InstructorCourseOut(
            code=row.code, title=row.title, status=row.status,
            students=student_count, price=float(row.price), academy=row.academy.name,
        ))
    return out


@router.post("/courses", response_model=InstructorCourseOut, status_code=201)
def create_course(
    request: CourseCreateRequest,
    current_user: User = Depends(get_current_instructor_user),
    db: Session = Depends(get_db),
):
    academy = db.query(Academy).filter(Academy.name == request.academy).first()
    if not academy:
        raise HTTPException(status_code=400, detail=f"Unknown academy: {request.academy}")
    if request.level not in ("Beginner", "Intermediate", "Advanced"):
        raise HTTPException(status_code=400, detail=f"Invalid level: {request.level}")

    code = _generate_course_code(db, request.academy)
    course = Course(
        code=code, title=request.title, academy_id=academy.id, instructor_id=current_user.id,
        level=request.level, status="draft", languages=["English"], duration_minutes=0,
        price=request.price, description=request.description, learn_outcomes=[],
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return InstructorCourseOut(
        code=course.code, title=course.title, status=course.status,
        students=0, price=float(course.price), academy=academy.name,
    )


@router.get("/payouts")
def get_payouts(_: User = Depends(get_current_instructor_user)):
    return {"commission_rate_pct": 20, "next_payout_date": "2026-08-01", "history": MOCK_PAYOUTS}
