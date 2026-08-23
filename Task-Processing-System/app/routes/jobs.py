from fastapi import APIRouter, HTTPException, status, Depends
from psycopg import DatabaseError

from app import database
from app.auth import get_current_user
from app.schemas import Job, JobCreate, JobCreated, ResultResponse

router = APIRouter()


def _not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Job not found")


@router.post("/jobs", response_model=JobCreated, status_code=status.HTTP_201_CREATED)
def submit_job(
    payload: JobCreate,
    user_id: int = Depends(get_current_user),
) -> JobCreated:
    try:
        job_id = database.create_job(payload.type.value, payload.input, user_id)
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return JobCreated(id=job_id, status="PENDING")


@router.get("/jobs", response_model=list[Job])
def get_jobs(user_id: int = Depends(get_current_user)) -> list[Job]:
    try:
        return [Job.model_validate(job) for job in database.list_jobs(user_id)]
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: int, user_id: int = Depends(get_current_user)) -> Job:
    try:
        job = database.get_job(job_id, user_id)
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    if job is None:
        raise _not_found()
    return Job.model_validate(job)


@router.get("/jobs/{job_id}/result", response_model=ResultResponse)
def get_result(job_id: int, user_id: int = Depends(get_current_user)) -> ResultResponse:
    try:
        job = database.get_job(job_id, user_id)
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    if job is None:
        raise _not_found()
    return ResultResponse(
        id=job["id"],
        status=job["status"],
        result=job["result"],
        error="Task execution failed" if job["status"] == "FAILED" else None,
    )


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_job(job_id: int, user_id: int = Depends(get_current_user)) -> None:
    try:
        if not database.delete_job(job_id, user_id):
            raise _not_found()
    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get("/tasks", response_model=list[str])
def list_tasks() -> list[str]:
    # For now, hardcode; later we’ll centralize in a tasks registry module.
    return ["fibonacci", "prime_factorization"]
