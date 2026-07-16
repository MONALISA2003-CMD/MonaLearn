-- MonaLearn database schema (PostgreSQL)
--
-- This is the schema app/db_models.py's SQLAlchemy models are built to
-- match. For a prototype, the backend creates these tables automatically
-- on startup via Base.metadata.create_all() — see app/db.py. Run this file
-- by hand instead if you want a real migration history from day one
-- (createdb monalearn && psql monalearn -f schema.sql), and switch to
-- Alembic before this goes anywhere near production, since create_all()
-- can't handle changing an existing table's shape.

-- NOTE: db_models.py's User.role (and level/status/plan on other tables)
-- are plain VARCHAR columns via SQLAlchemy's String, not tied to these
-- Postgres ENUM types. That means running the app's init_db()/create_all()
-- produces slightly looser columns than this file's DDL does. Fine for a
-- prototype; worth reconciling (SQLAlchemy Enum type, or drop the DDL
-- enums) before this matters for real data integrity.
CREATE TYPE user_role AS ENUM ('student', 'instructor', 'admin');
CREATE TYPE user_plan AS ENUM ('free', 'basic', 'professional', 'premium', 'enterprise');
CREATE TYPE course_level AS ENUM ('Beginner', 'Intermediate', 'Advanced');
CREATE TYPE course_status AS ENUM ('draft', 'enrolling', 'live');
CREATE TYPE certificate_status AS ENUM ('valid', 'revoked');
CREATE TYPE subscription_status AS ENUM ('active', 'canceled', 'past_due');

CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    role            user_role NOT NULL DEFAULT 'student',
    plan            user_plan NOT NULL DEFAULT 'free',
    location        VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE academies (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE courses (
    id               SERIAL PRIMARY KEY,
    code             VARCHAR(20) UNIQUE NOT NULL,
    title            VARCHAR(255) NOT NULL,
    academy_id       INTEGER NOT NULL REFERENCES academies(id) ON DELETE RESTRICT,
    instructor_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- nullable: existing catalog courses predate this column
    level            course_level NOT NULL,
    status           course_status NOT NULL DEFAULT 'draft',
    languages        TEXT[] NOT NULL DEFAULT '{}',
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    price            NUMERIC(8,2) NOT NULL DEFAULT 0,  -- 0 = included in plans, not sold individually
    description      TEXT,
    learn_outcomes   TEXT[] NOT NULL DEFAULT '{}',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_courses_academy_id ON courses(academy_id);
CREATE INDEX idx_courses_instructor_id ON courses(instructor_id);

CREATE TABLE lessons (
    id               SERIAL PRIMARY KEY,
    course_id        INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    position         INTEGER NOT NULL,
    title            VARCHAR(255) NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    UNIQUE (course_id, position)
);
CREATE INDEX idx_lessons_course_id ON lessons(course_id);

CREATE TABLE enrollments (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id     INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    progress_pct  NUMERIC(5,2) NOT NULL DEFAULT 0,
    enrolled_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at  TIMESTAMPTZ,
    UNIQUE (user_id, course_id)
);
CREATE INDEX idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);

CREATE TABLE certificates (
    id             SERIAL PRIMARY KEY,
    certificate_id VARCHAR(40) UNIQUE NOT NULL,     -- e.g. MNL-2026-KM-08931
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id      INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    score          INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    status         certificate_status NOT NULL DEFAULT 'valid',
    issued_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_certificates_user_id ON certificates(user_id);

CREATE TABLE subscriptions (
    id                 SERIAL PRIMARY KEY,
    user_id            INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan               user_plan NOT NULL DEFAULT 'free',
    status             subscription_status NOT NULL DEFAULT 'active',
    current_period_end TIMESTAMPTZ,
    payment_provider_customer_id VARCHAR(255)   -- e.g. a Stripe customer ID, once payments exist
);

CREATE TABLE ai_conversation_logs (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_code  VARCHAR(20),
    message_count INTEGER NOT NULL DEFAULT 0,
    flagged      BOOLEAN NOT NULL DEFAULT FALSE,
    flag_reason  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_ai_logs_user_id ON ai_conversation_logs(user_id);
CREATE INDEX idx_ai_logs_flagged ON ai_conversation_logs(flagged) WHERE flagged = TRUE;
