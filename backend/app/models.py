"""Pydantic models shared across the MonaLearn API routers."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Course(BaseModel):
    code: str
    title: str
    academy: str
    level: Literal["Beginner", "Intermediate", "Advanced"]
    languages: list[str]
    status: Literal["enrolling", "live"]
    duration: str
    duration_minutes: int
    description: str
    learn_outcomes: list[str]
    lessons: list[str]


class Certificate(BaseModel):
    certificate_id: str
    course_code: str
    course_title: str
    score: int = Field(ge=0, le=100)
    issued_to: str
    issued_at: str
    status: Literal["valid", "revoked"] = "valid"


class CertificateVerifyResult(BaseModel):
    valid: bool
    certificate: Optional[Certificate] = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    course_code: str = "MKT 132"
    lesson_context: str = "Lesson 8: Conversion funnels"
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    reply: str
