"""
AI Content Creation System — lesson draft generator.

Given a course code and topic, asks Claude to draft a lesson: objectives,
explanation, a worked example, and a short quiz. This produces a DRAFT only —
the product spec calls for a human review workflow before anything is
published, so treat the JSON output as input to an editor, not a finished
lesson.

Usage:
    pip install -r requirements.txt
    cp ../backend/.env.example .env   # add your ANTHROPIC_API_KEY
    python generate_lesson_content.py --code "MKT 132" --topic "Conversion funnels" --level Beginner
"""
import argparse
import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are an instructional designer for MonaLearn, a practical \
skills platform. Draft one lesson as strict JSON with keys: \
title, objectives (list of 3-5 strings), explanation (string, 150-250 words), \
worked_example (string), quiz (list of 4 objects with question, choices, answer_index). \
Return JSON only, no prose outside the JSON object."""


def get_client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("Set ANTHROPIC_API_KEY in automation/.env before running this script.")
    return Anthropic(api_key=api_key)


def generate_lesson(client: Anthropic, course_code: str, topic: str, level: str) -> dict:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Course: {course_code}\nTopic: {topic}\nLevel: {level}"}
        ],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description="Draft a MonaLearn lesson with Claude.")
    parser.add_argument("--code", required=True, help='Course code, e.g. "MKT 132"')
    parser.add_argument("--topic", required=True, help="Lesson topic")
    parser.add_argument("--level", default="Beginner", choices=["Beginner", "Intermediate", "Advanced"])
    parser.add_argument("--out", default="generated_lessons", help="Output directory")
    args = parser.parse_args()

    client = get_client()
    lesson = generate_lesson(client, args.code, args.topic, args.level)

    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)
    filename = out_dir / f"{args.code.replace(' ', '_')}_{args.topic.replace(' ', '_')}.json"
    filename.write_text(json.dumps(lesson, indent=2))
    print(f"Draft saved to {filename} — route it through human review before publishing.")


if __name__ == "__main__":
    main()
