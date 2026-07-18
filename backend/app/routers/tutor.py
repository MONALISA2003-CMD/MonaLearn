"""
AI Tutor endpoint — backed by Google AI Studio's Gemini API (free tier).
The frontend (tutor.html) calls THIS endpoint rather than any AI provider
directly, so the API key stays on the server and is never exposed to the
browser.

Requires GOOGLE_API_KEY to be set (see .env.example). Get a free key at
https://aistudio.google.com/apikey — no payment method required for the
free tier, which is generous enough for a prototype like this.

Model note: "gemini-1.5-flash" is used below — fast and within Google AI
Studio's free tier. If Google has moved the free tier to a newer model
name by the time you're reading this, check https://aistudio.google.com
for the current free-tier model list and update MODEL_NAME accordingly.
"""
import os

from fastapi import APIRouter, HTTPException
import google.generativeai as genai

from app.models import ChatRequest, ChatResponse

router = APIRouter()

MODEL_NAME = "gemini-1.5-flash"

_configured = False


def _ensure_configured():
    global _configured
    if not _configured:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GOOGLE_API_KEY is not set on the server. Add it in Render's Environment tab.",
            )
        genai.configure(api_key=api_key)
        _configured = True


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
    _ensure_configured()

    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided.")

    system_prompt = build_system_prompt(request.course_code, request.lesson_context)
    model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=system_prompt)

    # Gemini's chat history uses role "model" where Anthropic/OpenAI use
    # "assistant" — everything except the newest message becomes history,
    # and the newest message is sent separately via send_message().
    gemini_history = [
        {"role": "model" if m.role == "assistant" else "user", "parts": [m.content]}
        for m in request.messages[:-1]
    ]
    latest_message = request.messages[-1].content

    try:
        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(
            latest_message,
            generation_config={"max_output_tokens": 1000},
        )
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the client
        raise HTTPException(status_code=502, detail=f"Tutor request failed: {exc}") from exc

    reply_text = response.text or ""
    return ChatResponse(reply=reply_text)
