from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Optional

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import settings


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    """Open a transaction and roll it back automatically if work fails."""
    with psycopg.connect(settings.database_url, row_factory=dict_row) as connection:
        with connection.transaction():
            yield connection


# ==========================
# USER MANAGEMENT (Version 2)
# ==========================

def create_user(username: str, password_hash: str) -> int:
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            RETURNING id
            """,
            (username, password_hash),
        )
        return cursor.fetchone()["id"]


def get_user_by_username(username: str) -> Optional[dict[str, Any]]:
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = %s
            """,
            (username,),
        )
        return cursor.fetchone()


# ==========================
# WORKER MANAGEMENT (Version 2)
# ==========================

def register_worker() -> int:
    """Register a worker and return its ID."""
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO workers DEFAULT VALUES
            RETURNING id
            """
        )
        return cursor.fetchone()["id"]


def update_worker_heartbeat(worker_id: int) -> None:
    """Update the heartbeat timestamp for a worker."""
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE workers
            SET last_heartbeat = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (worker_id,),
        )


def mark_dead_workers(timeout_seconds: int = 15) -> None:
    """
    Mark workers as DEAD if they haven't sent a heartbeat
    within timeout_seconds.
    """
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE workers
            SET status = 'DEAD'
            WHERE status = 'ALIVE'
              AND last_heartbeat < (CURRENT_TIMESTAMP - (%s || ' seconds')::interval)
            """,
            (timeout_seconds,),
        )


def reset_stuck_jobs() -> None:
    """
    Reset jobs that are RUNNING but assigned to DEAD workers
    back to PENDING so other workers can pick them up.
    """
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE jobs
            SET status = 'PENDING',
                worker_id = NULL,
                started_at = NULL
            WHERE status = 'RUNNING'
              AND worker_id IN (
                  SELECT id FROM workers WHERE status = 'DEAD'
              )
            """
        )


# ==========================
# JOB MANAGEMENT (Version 1 + Version 2)
# ==========================

def create_job(job_type: str, input_value: int, user_id: Optional[int] = None) -> int:
    """
    Create a new job. In Version 2, optionally associate it with a user_id.
    """
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO jobs (type, input, status, user_id)
            VALUES (%s, %s, 'PENDING', %s)
            RETURNING id
            """,
            (job_type, input_value, user_id),
        )
        return cursor.fetchone()["id"]


def get_job(job_id: int, user_id: Optional[int] = None) -> Optional[dict[str, Any]]:
    """
    Get a single job. If user_id is provided, enforce ownership.
    """
    with get_connection() as connection, connection.cursor() as cursor:
        if user_id is None:
            cursor.execute(
                """
                SELECT id, type, input, status, result, error,
                       created_at, started_at, completed_at,
                       retry_count, max_retries, last_error, user_id, worker_id
                FROM jobs
                WHERE id = %s
                """,
                (job_id,),
            )
        else:
            cursor.execute(
                """
                SELECT id, type, input, status, result, error,
                       created_at, started_at, completed_at,
                       retry_count, max_retries, last_error, user_id, worker_id
                FROM jobs
                WHERE id = %s AND user_id = %s
                """,
                (job_id, user_id),
            )
        return cursor.fetchone()


def list_jobs(user_id: Optional[int] = None) -> list[dict[str, Any]]:
    """
    List jobs. If user_id is provided, only return that user's jobs.
    """
    with get_connection() as connection, connection.cursor() as cursor:
        if user_id is None:
            cursor.execute(
                """
                SELECT id, type, input, status, result, error,
                       created_at, started_at, completed_at,
                       retry_count, max_retries, last_error, user_id, worker_id
                FROM jobs
                ORDER BY created_at DESC
                """
            )
        else:
            cursor.execute(
                """
                SELECT id, type, input, status, result, error,
                       created_at, started_at, completed_at,
                       retry_count, max_retries, last_error, user_id, worker_id
                FROM jobs
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
        return list(cursor.fetchall())


def delete_job(job_id: int, user_id: Optional[int] = None) -> bool:
    """
    Delete a job. If user_id is provided, enforce ownership.
    """
    with get_connection() as connection, connection.cursor() as cursor:
        if user_id is None:
            cursor.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
        else:
            cursor.execute(
                "DELETE FROM jobs WHERE id = %s AND user_id = %s",
                (job_id, user_id),
            )
        return cursor.rowcount == 1


def claim_pending_job(worker_id: int) -> Optional[dict[str, Any]]:
    """
    Claim exactly one job; SKIP LOCKED prevents two workers claiming it.
    In Version 2, we also assign worker_id and set started_at.
    """
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, type, input
            FROM jobs
            WHERE status = 'PENDING'
            ORDER BY created_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1
            """
        )
        job = cursor.fetchone()
        if job is None:
            return None
        cursor.execute(
            """
            UPDATE jobs
            SET status = 'RUNNING',
                started_at = CURRENT_TIMESTAMP,
                worker_id = %s
            WHERE id = %s
            RETURNING id, type, input
            """,
            (worker_id, job["id"]),
        )
        return cursor.fetchone()


def complete_job(job_id: int, result: Any) -> None:
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE jobs
            SET status = 'COMPLETED',
                result = %s,
                completed_at = CURRENT_TIMESTAMP,
                last_error = NULL
            WHERE id = %s
            """,
            (Jsonb(result), job_id),
        )


def fail_or_retry_job(job_id: int, error: str) -> None:
    """
    Fail a job or requeue it depending on retry_count and max_retries.
    """
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT retry_count, max_retries
            FROM jobs
            WHERE id = %s
            """,
            (job_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return

        retry_count = row["retry_count"]
        max_retries = row["max_retries"]

        if retry_count < max_retries:
            # Requeue the job
            cursor.execute(
                """
                UPDATE jobs
                SET status = 'PENDING',
                    retry_count = retry_count + 1,
                    last_error = %s,
                    worker_id = NULL,
                    started_at = NULL,
                    completed_at = NULL
                WHERE id = %s
                """,
                (error, job_id),
            )
        else:
            # Permanently fail the job
            cursor.execute(
                """
                UPDATE jobs
                SET status = 'FAILED',
                    error = %s,
                    last_error = %s,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (error, error, job_id),
            )
