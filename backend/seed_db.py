"""
Seed script: populates the database with the same sample data that used to
live as hardcoded Python lists inside courses.py and certificates.py.

Run once against a fresh database:
    cd backend
    python seed_db.py

Idempotent — safe to run again, it skips anything that already exists by
unique key (academy name, course code, user email, certificate ID).
"""
from app.auth import hash_password
from app.db import SessionLocal, init_db
from app.db_models import Academy, Certificate, Course, Lesson, User

ACADEMIES = [
    "Business & Entrepreneurship",
    "Finance & Accounting",
    "Marketing & Sales",
    "Office Administration",
    "Language Institute",
]

COURSES = [
    {
        "code": "BUS 101", "title": "Entrepreneurship Fundamentals",
        "academy": "Business & Entrepreneurship", "level": "Beginner",
        "languages": ["English"], "status": "live", "duration_minutes": 340,
        "description": "A practical starting point for anyone testing a business idea for the "
                        "first time — from spotting a real problem to making your first "
                        "deliberate sale.",
        "learn_outcomes": [
            "Validate an idea before building anything",
            "Talk to real customers without leading them",
            "Write a one-page plan you'll actually use",
            "Price and position a first offer",
        ],
        "lessons": [
            "Spotting a problem worth solving", "Talking to your first ten customers",
            "Validating an idea before you build it", "Writing a one-page business plan",
            "Naming, pricing, and positioning", "Making your first sale, on purpose",
        ],
    },
    {
        "code": "BUS 204", "title": "Business Strategy & Scaling",
        "academy": "Business & Entrepreneurship", "level": "Intermediate",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 400,
        "description": "For founders past the first sale — how to choose what not to do, "
                        "build systems before hiring, and expand without losing what made "
                        "the business work.",
        "learn_outcomes": [
            "Define a strategy you can say no with", "Build repeatable systems before hiring",
            "Decide when to raise money, and when not to", "Expand into a second market deliberately",
        ],
        "lessons": [
            "What \"strategy\" actually means", "Choosing what not to do",
            "Building systems before you hire", "When to raise money, and when not to",
            "Expanding into a second market", "Scaling without losing quality",
        ],
    },
    {
        "code": "BUS 310", "title": "Fundraising & Investment Prep",
        "academy": "Business & Entrepreneurship", "level": "Advanced",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 290,
        "description": "What investors actually look for, how to build a pitch deck that "
                        "survives real questions, and how to negotiate a term sheet without "
                        "losing the room.",
        "learn_outcomes": [
            "Build a pitch deck that survives scrutiny", "Read and negotiate a term sheet",
            "Estimate an early-stage valuation", "Plan for life after the round closes",
        ],
        "lessons": [
            "What investors actually look for", "Building a pitch deck that survives questions",
            "Understanding term sheets", "Valuing an early-stage company",
            "Negotiating without losing the room", "Life after the round closes",
        ],
    },
    {
        "code": "FIN 214", "title": "Financial Statements",
        "academy": "Finance & Accounting", "level": "Intermediate",
        "languages": ["English", "Kiswahili"], "status": "enrolling", "duration_minutes": 320,
        "description": "Read a balance sheet, income statement, and cash flow statement well "
                        "enough to catch a problem before it becomes a crisis.",
        "learn_outcomes": [
            "Read a balance sheet without panic", "Separate profit from cash in your head",
            "Spot trouble in a statement early", "Present numbers to a non-finance audience",
        ],
        "lessons": [
            "Reading a balance sheet without panic", "The income statement, line by line",
            "Where cash flow tells a different story", "Spotting trouble before it's a crisis",
            "Comparing statements across periods", "Presenting numbers to someone who isn't an accountant",
        ],
    },
    {
        "code": "FIN 105", "title": "Budgeting & Financial Planning",
        "academy": "Finance & Accounting", "level": "Beginner",
        "languages": ["English"], "status": "live", "duration_minutes": 250,
        "description": "Build a budget that survives contact with a real month, and a simple "
                        "forecast you don't need a finance degree to maintain.",
        "learn_outcomes": [
            "Separate fixed costs from the ones you control", "Plan for a bad month before it happens",
            "Forecast without spreadsheeting yourself into a corner", "Review and adjust a budget monthly",
        ],
        "lessons": [
            "Building a budget that survives contact with reality", "Fixed costs versus the ones you control",
            "Planning for a bad month before it happens", "Personal finance habits that carry into business",
            "Simple forecasting without a finance degree", "Reviewing and adjusting the plan monthly",
        ],
    },
    {
        "code": "MKT 132", "title": "Digital Marketing",
        "academy": "Marketing & Sales", "level": "Beginner",
        "languages": ["English", "Español"], "status": "live", "duration_minutes": 365,
        "description": "How customers actually decide to buy, and how to build a funnel, ad "
                        "copy, and email sequence that matches how your specific business sells.",
        "learn_outcomes": [
            "Map a funnel that matches your business", "Write ad copy people actually read",
            "Read conversion data honestly", "Run an email sequence that isn't spam",
        ],
        "lessons": [
            "How customers actually decide to buy", "Building a funnel that matches your business",
            "Writing ad copy people actually read", "Conversion funnels, from click to customer",
            "Email marketing without sounding like spam", "Reading your numbers honestly",
        ],
    },
    {
        "code": "MKT 220", "title": "Sales & Negotiation",
        "academy": "Marketing & Sales", "level": "Intermediate",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 315,
        "description": "Sell without sounding like you're selling — handling objections, "
                        "negotiating price, and closing conversations rather than just pitches.",
        "learn_outcomes": [
            "Handle objections without getting defensive", "Negotiate price without racing to the bottom",
            "Close conversations, not just pitches", "Build a sales process you can repeat",
        ],
        "lessons": [
            "Selling without sounding like you're selling", "Handling objections without getting defensive",
            "Negotiating price without racing to the bottom", "Closing conversations, not just pitches",
            "Building a sales process you can repeat", "Managing a small sales team",
        ],
    },
    {
        "code": "ADM 108", "title": "Office Administration Fundamentals",
        "academy": "Office Administration", "level": "Beginner",
        "languages": ["English", "Français"], "status": "enrolling", "duration_minutes": 320,
        "description": "The software and the judgment behind a well-run office — scheduling, "
                        "records, meetings, and the etiquette that holds it all together.",
        "learn_outcomes": [
            "Run a calendar that actually works", "Keep records that survive an audit",
            "Write emails people respond to", "Run a meeting that ends on time",
        ],
        "lessons": [
            "Running a calendar that actually works", "Records and filing that survive an audit",
            "Writing emails people actually respond to", "Running a meeting that ends on time",
            "Professional etiquette across cultures", "Managing competing priorities",
        ],
    },
    {
        "code": "LANG 301", "title": "Business Mandarin",
        "academy": "Language Institute", "level": "Advanced",
        "languages": ["中文"], "status": "live", "duration_minutes": 450,
        "description": "Boardroom-level Mandarin — formal workplace hierarchy, negotiating a "
                        "deal, and writing a professional email with real fluency.",
        "learn_outcomes": [
            "Navigate formal workplace hierarchy", "Negotiate a deal in Mandarin",
            "Write a professional business email", "Present numbers and reports clearly",
        ],
        "lessons": [
            "Formal greetings and workplace hierarchy", "Negotiating a deal in Mandarin",
            "Writing a professional email", "Presenting numbers and reports",
            "Small talk that builds real relationships", "Handling disagreement politely",
        ],
    },
    {
        "code": "LANG 118", "title": "Arabic for Trade",
        "academy": "Language Institute", "level": "Beginner",
        "languages": ["العربية"], "status": "enrolling", "duration_minutes": 285,
        "description": "Practical Arabic for buying, selling, and negotiating — greetings, "
                        "numbers, and the vocabulary of an actual trade conversation.",
        "learn_outcomes": [
            "Handle business greetings and introductions", "Negotiate numbers and prices confidently",
            "Write a simple business message", "Understand key regional dialect differences",
        ],
        "lessons": [
            "Greetings and introductions in a business setting", "Numbers, prices, and negotiating",
            "Writing a simple business message", "Talking about your product or service",
            "Understanding regional dialect differences", "Closing a conversation politely",
        ],
    },
    {
        "code": "LANG 210", "title": "French for Business",
        "academy": "Language Institute", "level": "Beginner",
        "languages": ["Français"], "status": "enrolling", "duration_minutes": 270,
        "description": "Practical French for a business setting — enough to greet a client, "
                        "write a simple email, and hold a basic meeting without switching to English.",
        "learn_outcomes": [
            "Handle greetings and introductions professionally", "Write a short business email in French",
            "Discuss numbers, prices, and schedules", "Understand common meeting vocabulary",
        ],
        "lessons": [
            "Greetings and professional introductions", "Numbers, dates, and scheduling",
            "Writing a simple business email", "Ordering and discussing prices",
            "Small talk before a meeting starts", "Closing a conversation politely",
        ],
    },
    {
        "code": "LANG 150", "title": "Kiswahili for Trade",
        "academy": "Language Institute", "level": "Beginner",
        "languages": ["Kiswahili"], "status": "live", "duration_minutes": 240,
        "description": "Everyday Kiswahili for buying, selling, and working across East Africa's "
                        "biggest trade language.",
        "learn_outcomes": [
            "Greet and address people appropriately", "Negotiate prices and quantities",
            "Describe your business simply", "Handle common customer questions",
        ],
        "lessons": [
            "Greetings and forms of respect", "Numbers and negotiating a price",
            "Describing your product or service", "Asking and answering customer questions",
            "Directions and everyday logistics", "Closing a sale politely",
        ],
    },
    {
        "code": "LANG 305", "title": "German for Industry",
        "academy": "Language Institute", "level": "Beginner",
        "languages": ["Deutsch"], "status": "enrolling", "duration_minutes": 330,
        "description": "German for manufacturing, logistics, and technical trade — the vocabulary "
                        "that shows up on a factory floor or a shipping manifest.",
        "learn_outcomes": [
            "Handle greetings and workplace introductions", "Read basic technical and shipping documents",
            "Ask clarifying questions on a production line", "Discuss schedules and delivery timelines",
        ],
        "lessons": [
            "Greetings and workplace introductions", "Numbers, measurements, and units",
            "Reading a simple shipping document", "Asking questions on a production floor",
            "Discussing timelines and delays", "Closing a work conversation politely",
        ],
    },
    {
        "code": "LANG 140", "title": "Spanish for Business",
        "academy": "Language Institute", "level": "Beginner",
        "languages": ["Español"], "status": "live", "duration_minutes": 255,
        "description": "Spanish for client calls, simple contracts, and everyday business "
                        "conversation across Spanish-speaking markets.",
        "learn_outcomes": [
            "Handle introductions and small talk professionally", "Discuss pricing and terms simply",
            "Write a short business message", "Understand common contract vocabulary",
        ],
        "lessons": [
            "Greetings and professional small talk", "Numbers, prices, and terms",
            "Writing a short business message", "Common contract and agreement vocabulary",
            "Handling a simple phone call", "Closing a business conversation",
        ],
    },
    {
        "code": "LANG 400", "title": "Workplace Sign Language Basics",
        "academy": "Language Institute", "level": "Beginner",
        "languages": ["Sign Language"], "status": "enrolling", "duration_minutes": 240,
        "description": "Foundational signing for everyday workplace communication — greetings, "
                        "basic requests, and enough fingerspelling to introduce yourself and your role.",
        "learn_outcomes": [
            "Fingerspell your name and basic workplace terms", "Sign common greetings and introductions",
            "Ask and answer simple workplace questions", "Recognize numbers and basic scheduling signs",
        ],
        "lessons": [
            "The alphabet and fingerspelling basics", "Greetings and self-introduction",
            "Common workplace vocabulary", "Asking simple questions",
            "Numbers and scheduling signs", "Putting it together: a short conversation",
        ],
    },
]

# (email, full_name, plan, password, role) — password is the same for all
# demo accounts, only for local testing. Change it / delete these before anything real.
DEMO_USERS = [
    ("amara@example.com", "Amara K.", "professional", "demo-password-123", "student"),
    ("tendai@example.com", "Tendai Moyo", "premium", "demo-password-123", "student"),
    ("sofia@example.com", "Sofia Reyes", "professional", "demo-password-123", "student"),
    ("priya@example.com", "Priya Nair", "professional", "demo-password-123", "student"),
    ("daniel@example.com", "Daniel Owusu", "basic", "demo-password-123", "student"),
    ("grace.instructor@example.com", "Grace N.", "professional", "demo-password-123", "instructor"),
]

# Course codes to hand off to the instructor demo account, so
# instructor.html has something real to show on first login instead of an
# empty state. These courses predate the instructor_id column, which is
# why this is a seed-time reassignment rather than how the column gets set
# in normal use (that happens via POST /api/instructor/courses).
INSTRUCTOR_OWNED_COURSES = {
    "grace.instructor@example.com": ["MKT 132", "MKT 220"],
}

# (certificate_id, user_email, course_code, score, status)
CERTIFICATES = [
    ("MNL-2026-KM-08931", "amara@example.com", "MKT 132", 91, "valid"),
    ("MNL-2026-KM-04117", "amara@example.com", "BUS 101", 88, "valid"),
    ("MNL-2026-TM-11029", "tendai@example.com", "FIN 214", 94, "valid"),
    ("MNL-2026-SR-09876", "sofia@example.com", "BUS 204", 79, "valid"),
    ("MNL-2026-PN-07654", "priya@example.com", "ADM 108", 85, "valid"),
    ("MNL-2026-DO-05432", "daniel@example.com", "FIN 105", 73, "revoked"),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        # Academies
        academy_by_name = {}
        for name in ACADEMIES:
            existing = db.query(Academy).filter(Academy.name == name).first()
            if not existing:
                existing = Academy(name=name)
                db.add(existing)
                db.flush()
                print(f"Created academy: {name}")
            academy_by_name[name] = existing

        # Courses + lessons
        for c in COURSES:
            existing = db.query(Course).filter(Course.code == c["code"]).first()
            if existing:
                continue
            course = Course(
                code=c["code"], title=c["title"], academy_id=academy_by_name[c["academy"]].id,
                level=c["level"], status=c["status"], languages=c["languages"],
                duration_minutes=c["duration_minutes"], description=c["description"],
                learn_outcomes=c["learn_outcomes"],
            )
            db.add(course)
            db.flush()
            for i, lesson_title in enumerate(c["lessons"], start=1):
                db.add(Lesson(course_id=course.id, position=i, title=lesson_title,
                               duration_minutes=c["duration_minutes"] // len(c["lessons"])))
            print(f"Created course: {c['code']} — {c['title']} ({len(c['lessons'])} lessons)")

        # Demo users
        user_by_email = {}
        for email, full_name, plan, password, role in DEMO_USERS:
            existing = db.query(User).filter(User.email == email).first()
            if not existing:
                existing = User(
                    email=email, full_name=full_name, plan=plan, role=role,
                    hashed_password=hash_password(password),
                )
                db.add(existing)
                db.flush()
                print(f"Created user: {email} (role: {role}, password: {password})")
            user_by_email[email] = existing

        # Hand a couple of existing courses to the instructor demo account,
        # so instructor.html shows real linked data on first login.
        for email, codes in INSTRUCTOR_OWNED_COURSES.items():
            instructor = user_by_email.get(email)
            if not instructor:
                continue
            for code in codes:
                course = db.query(Course).filter(Course.code == code).first()
                if course and course.instructor_id is None:
                    course.instructor_id = instructor.id
                    print(f"Assigned {code} to {email}")
        db.commit()

        # Certificates
        for cert_id, email, course_code, score, status_val in CERTIFICATES:
            existing = db.query(Certificate).filter(Certificate.certificate_id == cert_id).first()
            if existing:
                continue
            course = db.query(Course).filter(Course.code == course_code).first()
            if not course:
                print(f"Skipping certificate {cert_id}: course {course_code} not found")
                continue
            db.add(Certificate(
                certificate_id=cert_id, user_id=user_by_email[email].id, course_id=course.id,
                score=score, status=status_val,
            ))
            print(f"Created certificate: {cert_id}")

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
