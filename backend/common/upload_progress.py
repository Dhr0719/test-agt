import redis
from django.conf import settings


redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def set_upload_progress(task_id, status, step, percent):
    key = f"upload:task:{task_id}:progress"

    redis_client.hset(key, mapping={
        "status": status,
        "step": step,
        "percent": percent,
    })

    redis_client.expire(key, 3600)


def get_upload_progress(task_id):
    key = f"upload:task:{task_id}:progress"
    data = redis_client.hgetall(key)

    if not data:
        return {
            "status": "UNKNOWN",
            "step": "暂无进度",
            "percent": "0",
        }

    return data