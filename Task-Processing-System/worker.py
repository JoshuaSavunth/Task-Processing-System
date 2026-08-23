import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
import signal
import time

print("Worker starting...")

from app import database
from app.tasks.executor import execute_task

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("worker")
running = True


def stop_worker(signum: int, _frame: object) -> None:
    del signum
    global running
    running = False


def run(poll_interval: float = 2.0, heartbeat_interval: float = 5.0) -> None:
    signal.signal(signal.SIGINT, stop_worker)
    signal.signal(signal.SIGTERM, stop_worker)

    # Version 2: register worker
    worker_id = database.register_worker()
    logger.info(f"Worker started with ID {worker_id}")

    last_heartbeat = time.time()

    while running:
        # Version 2: mark dead workers + reset stuck jobs
        database.mark_dead_workers()
        database.reset_stuck_jobs()

        # Version 2: heartbeat
        now = time.time()
        if now - last_heartbeat >= heartbeat_interval:
            database.update_worker_heartbeat(worker_id)
            last_heartbeat = now
            logger.info(f"Heartbeat updated for worker {worker_id}")

        logger.info("Checking for jobs")
        job = database.claim_pending_job(worker_id)

        if job is None:
            time.sleep(poll_interval)
            continue

        job_id = job["id"]
        logger.info(f"Claimed job {job_id}")

        try:
            logger.info(f"Executing {job['type']}")
            result = execute_task(job["type"], job["input"])
            database.complete_job(job_id, result)
            logger.info(f"Job {job_id} completed")

        except Exception as exc:
            logger.error(f"Job {job_id} failed: {exc}")
            database.fail_or_retry_job(job_id, str(exc))

    logger.info("Worker shutting down")

if __name__ == "__main__":
    run()

