"""
Dashboard data endpoint.

Returns the payload the dashboard.html prototype currently hardcodes:
stats, academy progress, streak history, today's plan, and recommendations.

This is now behind real auth: a valid access token is required, and a
student can only fetch their own dashboard (an admin can fetch anyone's).
That's the actual authorization check this endpoint was missing before —
previously it accepted any user_id in the URL and returned the same mock
data regardless of who asked.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.db_models import User

router = APIRouter()

MOCK_DASHBOARD = {
    "student": {"name": "Amara K.", "plan": "Professional", "location": "Kampala"},
    "stats": {
        "hours_this_week": 6.5,
        "courses_in_progress": 3,
        "certificates_earned": 2,
        "streak_days": 12,
    },
    "continue_learning": {
        "course_code": "MKT 132",
        "course_title": "Digital Marketing",
        "lesson": "Lesson 8 of 14 — Conversion funnels",
        "progress_pct": 57,
    },
    "in_progress": [
        {"course_code": "FIN 214", "course_title": "Financial Statements", "progress_pct": 34},
        {"course_code": "LANG 301", "course_title": "Business Mandarin", "progress_pct": 45},
    ],
    "academy_progress": [
        {"academy": "Business & Entrepreneurship", "pct": 68},
        {"academy": "Finance & Accounting", "pct": 34},
        {"academy": "Marketing & Sales", "pct": 82},
        {"academy": "Office Administration", "pct": 12},
        {"academy": "Language Institute", "pct": 45},
    ],
    "todays_plan": [
        {"title": "Watch: MKT 132 · Lesson 7 recap", "minutes": 12, "done": True},
        {"title": "Finish MKT 132 · Lesson 8: Conversion funnels", "minutes": 20, "done": False},
        {"title": "Practice: Business Mandarin vocabulary", "minutes": 10, "done": False},
        {"title": "Quiz: FIN 214 · Cash flow statements", "minutes": None, "due": "tonight", "done": False},
        {"title": "Read: case study — pricing strategy", "minutes": 7, "done": False},
    ],
    "recommended": [
        {"code": "ADM 108", "title": "Office Administration Fundamentals", "level": "Beginner", "duration": "5h 20m"},
        {"code": "BUS 204", "title": "Business Strategy & Scaling", "level": "Intermediate", "duration": "6h 40m"},
        {"code": "LANG 118", "title": "Arabic for Trade", "level": "Beginner", "duration": "4h 10m"},
    ],
}


@router.get("/{user_id}")
def get_dashboard(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this dashboard")
    # Still the same mock payload regardless of who asked — real per-student
    # data (progress, streak, recommendations) is the next piece to wire up
    # once enrollments/lessons are actually being written to, not just read.
    return MOCK_DASHBOARD
