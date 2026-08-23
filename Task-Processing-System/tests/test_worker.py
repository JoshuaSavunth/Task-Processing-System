from worker import run


def test_worker_processes_success(monkeypatch) -> None:
    import worker

    jobs = iter([{"id": 15, "type": "fibonacci", "input": 10}, None])
    completed: list[tuple[int, object]] = []
    monkeypatch.setattr(worker.database, "claim_pending_job", lambda: next(jobs))
    monkeypatch.setattr(worker.database, "complete_job", lambda job_id, result: completed.append((job_id, result)))
    monkeypatch.setattr(worker.time, "sleep", lambda _: setattr(worker, "running", False))
    worker.running = True
    run(poll_interval=0)
    assert completed == [(15, 55)]


def test_worker_processes_failure(monkeypatch) -> None:
    import worker

    jobs = iter([{"id": 16, "type": "prime_factorization", "input": 1}, None])
    failed: list[tuple[int, str]] = []
    monkeypatch.setattr(worker.database, "claim_pending_job", lambda: next(jobs))
    monkeypatch.setattr(worker.database, "fail_job", lambda job_id, error: failed.append((job_id, error)))
    monkeypatch.setattr(worker.time, "sleep", lambda _: setattr(worker, "running", False))
    worker.running = True
    run(poll_interval=0)
    assert failed[0][0] == 16