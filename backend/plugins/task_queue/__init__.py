'''Backend plugin setting up a Celery app with Redis broker.

Provides:
- `celery_app` – Celery instance configured from env vars.
- Example task `run_periodic_cleanup`.
''' 

import os
from celery import Celery

# Default broker URL – can be overridden via REDIS_URL env var.
broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery('jarvis', broker=broker_url, backend=broker_url)

# Example configuration – can be extended via env vars or config file.
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(name='jarvis.run_periodic_cleanup')
def run_periodic_cleanup():
    """Placeholder periodic cleanup task.
    In a real system this could delete expired sessions, prune logs, etc.
    """
    return "cleanup completed"
