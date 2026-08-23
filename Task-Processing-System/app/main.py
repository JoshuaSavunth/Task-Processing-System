from fastapi import FastAPI

from app.routes.jobs import router as jobs_router
from app.routes.auth import router as auth_router

app = FastAPI(title="Distributed Task System", version="2.0.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "Distributed Task System", "status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(jobs_router, tags=["jobs"])


@app.get("/api")
def api_root() -> dict[str, str]:
    return {"name": "Distributed Task System", "status": "ok"}
