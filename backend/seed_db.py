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
        "code": "BUS 150", "title": "Customer Discovery & Market Research",
        "academy": "Business & Entrepreneurship", "level": "Beginner",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 260,
        "description": "How to find out what customers actually want before you build anything "
                        "for them — structured interviews, cheap research methods, and reading "
                        "the signals that matter.",
        "learn_outcomes": [
            "Run a customer interview that doesn't lead the witness", "Spot a real problem versus a nice-to-have",
            "Size a market without expensive research tools", "Turn conversations into a testable hypothesis",
        ],
        "lessons": [
            "Why most market research asks the wrong questions", "Structuring a customer interview",
            "Reading between the lines of what people say", "Cheap ways to estimate market size",
            "Turning insight into a hypothesis", "Deciding when you've learned enough",
        ],
    },
    {
        "code": "BUS 220", "title": "Leadership & Team Building",
        "academy": "Business & Entrepreneurship", "level": "Intermediate",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 300,
        "description": "The shift from doing the work yourself to getting a small team to do it "
                        "well — delegation, feedback, and keeping people around.",
        "learn_outcomes": [
            "Delegate a task without losing quality", "Give feedback people can actually use",
            "Run a one-on-one that builds trust", "Recognize early signs of a team problem",
        ],
        "lessons": [
            "Moving from doer to manager", "Delegating without micromanaging",
            "Giving feedback that lands", "Running a useful one-on-one",
            "Handling conflict on a small team", "Keeping good people from leaving",
        ],
    },
    {
        "code": "BUS 260", "title": "Branding Fundamentals",
        "academy": "Business & Entrepreneurship", "level": "Beginner",
        "languages": ["English"], "status": "live", "duration_minutes": 240,
        "description": "What a brand actually is beyond a logo — positioning, voice, and the "
                        "promise you're making customers before they buy.",
        "learn_outcomes": [
            "Write a one-line positioning statement", "Define a consistent brand voice",
            "Choose visual identity basics that hold up", "Audit a brand for consistency",
        ],
        "lessons": [
            "What a brand promises, beyond the logo", "Positioning against real alternatives",
            "Finding a voice that sounds like you", "Visual identity basics that scale",
            "Keeping a brand consistent across channels", "Auditing your own brand honestly",
        ],
    },
    {
        "code": "BUS 340", "title": "Corporate Strategy & Expansion",
        "academy": "Business & Entrepreneurship", "level": "Advanced",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 320,
        "description": "Strategic decisions for a business past its first few years — where to "
                        "expand, when to diversify, and how to compete against larger players.",
        "learn_outcomes": [
            "Evaluate a market before entering it", "Decide between organic growth and acquisition",
            "Build a competitive moat that holds up", "Plan an expansion without overextending",
        ],
        "lessons": [
            "Evaluating a new market honestly", "Organic growth versus acquisition",
            "Building a moat competitors can't cross quickly", "Diversification: when it helps and when it doesn't",
            "Planning an expansion budget realistically", "Case study: an expansion that worked, and one that didn't",
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
        "code": "FIN 120", "title": "Bookkeeping Basics",
        "academy": "Finance & Accounting", "level": "Beginner",
        "languages": ["English"], "status": "live", "duration_minutes": 220,
        "description": "The habits and mechanics of keeping clean books from day one — so the "
                        "numbers are still trustworthy a year later.",
        "learn_outcomes": [
            "Set up a simple chart of accounts", "Record transactions accurately as they happen",
            "Reconcile a bank statement without dread", "Spot a bookkeeping error before it compounds",
        ],
        "lessons": [
            "Why bookkeeping habits matter more than software", "Setting up a simple chart of accounts",
            "Recording transactions as they happen", "Reconciling a bank statement",
            "Common bookkeeping mistakes and how to catch them", "Closing the books at month end",
        ],
    },
    {
        "code": "FIN 230", "title": "Excel for Finance",
        "academy": "Finance & Accounting", "level": "Intermediate",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 280,
        "description": "The specific Excel skills finance work actually uses — not every formula "
                        "that exists, just the ones that show up in a real spreadsheet.",
        "learn_outcomes": [
            "Build a simple financial model from scratch", "Use lookup and reference formulas confidently",
            "Create a chart that communicates, not decorates", "Audit a spreadsheet for errors before sharing it",
        ],
        "lessons": [
            "Spreadsheet habits that prevent errors later", "Formulas finance actually uses day to day",
            "Building a simple financial model", "Lookup and reference formulas",
            "Charts that communicate clearly", "Auditing a spreadsheet before you share it",
        ],
    },
    {
        "code": "FIN 250", "title": "Payroll & Tax Fundamentals",
        "academy": "Finance & Accounting", "level": "Intermediate",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 250,
        "description": "The basics of running payroll correctly and understanding what a small "
                        "business owes in taxes, without needing to become an accountant.",
        "learn_outcomes": [
            "Calculate a simple payroll run correctly", "Understand common payroll deductions",
            "Know which taxes apply to a small business", "Avoid the most common compliance mistakes",
        ],
        "lessons": [
            "How payroll actually works, step by step", "Common deductions and what they're for",
            "Calculating a payroll run correctly", "Taxes a small business typically owes",
            "Filing basics and deadlines that matter", "Mistakes that trigger the most compliance trouble",
        ],
    },
    {
        "code": "FIN 315", "title": "Investment Basics",
        "academy": "Finance & Accounting", "level": "Advanced",
        "languages": ["English"], "status": "live", "duration_minutes": 260,
        "description": "How to evaluate where to put money that isn't going straight back into "
                        "daily operations — risk, return, and the basic instruments worth understanding.",
        "learn_outcomes": [
            "Compare risk and return across investment types", "Read a basic investment prospectus",
            "Understand diversification in practice", "Avoid the most common investing mistakes",
        ],
        "lessons": [
            "Risk and return, the real relationship", "Common investment types explained plainly",
            "Reading a basic prospectus", "Diversification in practice, not just theory",
            "Avoiding common investing mistakes", "Building a simple investment plan",
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
        "code": "MKT 110", "title": "Marketing Fundamentals & Customer Psychology",
        "academy": "Marketing & Sales", "level": "Beginner",
        "languages": ["English"], "status": "live", "duration_minutes": 250,
        "description": "Why people actually buy things, and how to build a marketing approach "
                        "around real decision-making instead of guesswork.",
        "learn_outcomes": [
            "Explain the psychology behind a buying decision", "Identify your actual target customer, not a vague one",
            "Position an offer around a real need", "Choose the right channel for your specific audience",
        ],
        "lessons": [
            "Why people actually buy", "Defining a target customer precisely",
            "Positioning an offer around a real need", "Choosing channels that fit your audience",
            "Common psychology mistakes in marketing", "Putting a simple marketing plan together",
        ],
    },
    {
        "code": "MKT 160", "title": "SEO & Content Marketing",
        "academy": "Marketing & Sales", "level": "Beginner",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 270,
        "description": "How search engines actually decide what to rank, and how to write "
                        "content that earns attention instead of chasing algorithms.",
        "learn_outcomes": [
            "Do basic keyword research that's actually useful", "Structure a page for both readers and search engines",
            "Build a simple content calendar", "Measure whether content is actually working",
        ],
        "lessons": [
            "How search engines really decide rankings", "Keyword research without the guesswork",
            "Structuring a page for readers and search", "Building a content calendar you'll stick to",
            "Measuring what's actually working", "Common SEO mistakes that waste effort",
        ],
    },
    {
        "code": "MKT 210", "title": "Social Media & Influencer Marketing",
        "academy": "Marketing & Sales", "level": "Intermediate",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 260,
        "description": "Running a social presence and influencer partnerships that build real "
                        "audience trust instead of empty engagement.",
        "learn_outcomes": [
            "Choose the right platform for your audience", "Plan a content calendar that doesn't burn out",
            "Evaluate an influencer partnership honestly", "Read engagement metrics that actually matter",
        ],
        "lessons": [
            "Choosing the right platform, not every platform", "Planning content without burning out",
            "Evaluating an influencer partnership", "Negotiating a fair influencer deal",
            "Metrics that matter versus vanity numbers", "Handling a social media mistake publicly",
        ],
    },
    {
        "code": "MKT 305", "title": "Building and Managing a Sales Team",
        "academy": "Marketing & Sales", "level": "Advanced",
        "languages": ["English"], "status": "live", "duration_minutes": 300,
        "description": "Moving from selling yourself to building a sales team that performs "
                        "consistently without you in every conversation.",
        "learn_outcomes": [
            "Hire for the right sales traits, not just charisma", "Build a repeatable sales process a team can follow",
            "Set targets that motivate without distorting behavior", "Coach an underperforming salesperson effectively",
        ],
        "lessons": [
            "What makes someone good at sales, really", "Building a repeatable sales process",
            "Hiring for a sales role well", "Setting targets that motivate the right things",
            "Coaching a salesperson who's struggling", "Running a sales team meeting that helps",
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
        "code": "ADM 130", "title": "Microsoft Office Essentials",
        "academy": "Office Administration", "level": "Beginner",
        "languages": ["English", "Français"], "status": "live", "duration_minutes": 240,
        "description": "The Word, Excel, and PowerPoint skills that come up constantly in office "
                        "work, taught around real tasks instead of feature tours.",
        "learn_outcomes": [
            "Format a professional document quickly in Word", "Build a simple spreadsheet with working formulas",
            "Put together a clean, readable presentation", "Move information between the three tools smoothly",
        ],
        "lessons": [
            "Word: formatting a professional document", "Word: templates and reusable formats",
            "Excel: a spreadsheet with working formulas", "Excel: simple charts and formatting",
            "PowerPoint: building a clean presentation", "Moving information between Word, Excel, and PowerPoint",
        ],
    },
    {
        "code": "ADM 160", "title": "Records & Document Management",
        "academy": "Office Administration", "level": "Beginner",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 210,
        "description": "Setting up a filing and records system, physical or digital, that "
                        "survives when you're not the one looking for something.",
        "learn_outcomes": [
            "Design a folder structure that makes sense to others", "Set a retention policy for common document types",
            "Handle sensitive documents appropriately", "Recover quickly when something goes missing",
        ],
        "lessons": [
            "Why most filing systems fail eventually", "Designing a folder structure others can use",
            "Retention: what to keep, and for how long", "Handling sensitive and confidential documents",
            "Digital backups that actually get used", "What to do when something goes missing",
        ],
    },
    {
        "code": "ADM 210", "title": "Report Writing & Business Communication",
        "academy": "Office Administration", "level": "Intermediate",
        "languages": ["English"], "status": "enrolling", "duration_minutes": 250,
        "description": "Writing reports and internal communication that get read and acted on, "
                        "not skimmed and ignored.",
        "learn_outcomes": [
            "Structure a report so the point comes first", "Write an email that gets a timely response",
            "Summarize a long document without losing what matters", "Adapt tone for different audiences appropriately",
        ],
        "lessons": [
            "Leading with the point, not the buildup", "Structuring a report people will actually read",
            "Writing emails that get responses", "Summarizing without losing what matters",
            "Adapting tone for different audiences", "Proofreading for clarity, not just typos",
        ],
    },
    {
        "code": "ADM 250", "title": "Meeting & Project Coordination",
        "academy": "Office Administration", "level": "Intermediate",
        "languages": ["English"], "status": "live", "duration_minutes": 260,
        "description": "Running meetings that end on time with clear outcomes, and coordinating "
                        "small projects without a dedicated project management tool.",
        "learn_outcomes": [
            "Build an agenda that keeps a meeting on track", "Run a meeting that ends with clear next steps",
            "Track a small project without heavy tooling", "Follow up so action items actually get done",
        ],
        "lessons": [
            "Building an agenda that keeps things on track", "Running the meeting itself",
            "Capturing decisions and next steps clearly", "Tracking a small project simply",
            "Following up so nothing falls through", "Handling a meeting that's gone off the rails",
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
