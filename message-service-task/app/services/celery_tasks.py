from celery import Celery

celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0"
)

@celery.task
def update_last_seen(user_id):
    print(f"Updated last seen for {user_id}")