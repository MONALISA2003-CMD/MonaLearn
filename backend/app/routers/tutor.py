"""
AI Tutor endpoint.

The tutor.html prototype calls the Anthropic API directly from the browser,
which only works inside the Claude.ai artifact sandbox where that call is
proxied and authenticated automatically. In a real deployment, the frontend
should call THIS endpoint instead, so the Anthropic API key stays on the
server and is never exposed to the browser.

Requires ANTHROPIC_API_KEY to be set (see .env.example).
"""
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from app.models import ChatRequest, ChatResponse

load_dotenv()

router = APIRouter()

_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="ANTHROPIC_API_KEY is not set on the server. Copy .env.example to .env and add your key.",
            )
        _client = Anthropic(api_key=api_key)
    return _client


def build_system_prompt(course_code: str, lesson_context: str) -> str:
    return f"""You are the MonaLearn AI Tutor, embedded inside course {course_code}, \
currently on {lesson_context}. The student is an adult learner working through \
MonaLearn's practical, career-focused curriculum.

Behave like a genuinely good human instructor, not a generic assistant:
- Explain concepts clearly and concretely, using small-business or entrepreneurship \
examples where useful.
- Keep answers focused: usually 3-6 sentences unless the student asks for a full \
study plan, a list, or more depth.
- When helpful, ask a short checking question back, or offer to quiz the student.
- Be direct and substantive rather than flattering. Do not open with praise like \
"great question."
- Do not claim to know things about this specific student beyond what's in the \
conversation."""


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    client = get_client()
    system_prompt = build_system_prompt(request.course_code, request.lesson_context)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": m.role, "content": m.content} for m in request.messages],
        )
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        raise HTTPException(status_code=502, detail=f"Tutor request failed: {exc}") from exc

    reply_text = "".join(block.text for block in message.content if block.type == "text")
    return ChatResponse(reply=reply_text)
