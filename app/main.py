from uuid import uuid4

from fastapi import FastAPI, File, UploadFile

from app.jobs import create_job, get_job
from app.tasks import process_document


app = FastAPI(
    title="OnGyeol Backend"
)


@app.get("/")
def root():
    return {
        "service": "OnGyeol",
        "status": "running",
    }


@app.post("/documents")
async def upload_document(
    file: UploadFile = File(...)
):
    job_id = str(uuid4())

    file_data = await file.read()

    create_job(
        job_id=job_id,
        filename=file.filename,
    )

    process_document.delay(
        job_id,
        file_data,
        file.filename,
    )

    return {
        "job_id": job_id,
        "status": "queued",
    }


@app.get("/jobs/{job_id}")
def get_job_status(
    job_id: str
):
    job = get_job(job_id)

    if job is None:
        return {
            "error": "Job not found"
        }

    return job