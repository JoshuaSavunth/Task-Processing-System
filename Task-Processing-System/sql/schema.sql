-- ============================
-- Users table (NEW in V2)
-- ============================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- Workers table (NEW in V2)
-- ============================
CREATE TABLE IF NOT EXISTS workers (
    id SERIAL PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'ALIVE'
        CHECK (status IN ('ALIVE', 'DEAD')),
    last_heartbeat TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- Jobs table (UPGRADED in V2)
-- ============================
CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,

    -- Task type
    type TEXT NOT NULL CHECK (type IN ('fibonacci', 'prime_factorization')),
    input INTEGER NOT NULL CHECK (input >= 0),

    -- Job status
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),

    -- Ownership (NEW)
    user_id INTEGER NOT NULL REFERENCES users(id),

    -- Worker assignment (NEW)
    worker_id INTEGER REFERENCES workers(id),

    -- Retry logic (NEW)
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,

    -- Results
    result JSONB,
    error TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- ============================
-- Index for job claiming
-- ============================
CREATE INDEX IF NOT EXISTS jobs_pending_created_idx
    ON jobs (created_at)
    WHERE status = 'PENDING';
