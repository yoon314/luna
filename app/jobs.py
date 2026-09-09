import redis
import json


redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=1,
    decode_responses=True
)


def create_job(job_id: str, filename: str):
    job = {
        "status": "queued",
        "progress": 0,
        "filename": filename,
        "result": None
    }

    redis_client.set(
        f"job:{job_id}",
        json.dumps(job)
    )


def get_job(job_id: str):
    data = redis_client.get(f"job:{job_id}")

    if data is None:
        return None

    return json.loads(data)


def update_job(job_id: str, **updates):
    job = get_job(job_id)

    if job is None:
        return None

    job.update(updates)

    redis_client.set(
        f"job:{job_id}",
        json.dumps(job)
    )

    return job