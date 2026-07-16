"""
Certificate verification endpoint — now reading from the real database
instead of a hardcoded dict. Run `python seed_db.py` once against your
database before expecting this to find anything.

Backs the public verify.html page, the landing page's "Verify a
certificate" box, and the certificates card on the dashboard. Deliberately
unauthenticated — that's the point of a public verification page, the same
way Credly or a university's certificate lookup works without a login.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.db_models import Certificate as CertificateRow
from app.models import Certificate, CertificateVerifyResult

router = APIRouter()


def _to_api_certificate(row: CertificateRow) -> Certificate:
    return Certificate(
        certificate_id=row.certificate_id,
        course_code=row.course.code,
        course_title=row.course.title,
        score=row.score,
        issued_to=row.user.full_name,
        issued_at=row.issued_at.date().isoformat(),
        status=row.status,
    )


@router.get("/{certificate_id}", response_model=CertificateVerifyResult)
def verify_certificate(certificate_id: str, db: Session = Depends(get_db)):
    row = db.query(CertificateRow).filter(CertificateRow.certificate_id == certificate_id.strip().upper()).first()
    if not row:
        return CertificateVerifyResult(valid=False, certificate=None)
    cert = _to_api_certificate(row)
    return CertificateVerifyResult(valid=(cert.status == "valid"), certificate=cert)
