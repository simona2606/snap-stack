from apscheduler.schedulers.background import BackgroundScheduler
from cinderclient import client
import os

# Configura il client Cinder
def get_cinder_client():
    return client.Client(
        version='3',
        username=os.getenv('OS_USERNAME'),
        password=os.getenv('OS_PASSWORD'),
        project_name=os.getenv('OS_PROJECT_NAME'),
        auth_url=os.getenv('OS_AUTH_URL')
    )

def create_snapshot(volume_id):
    cinder = get_cinder_client()
    snapshot = cinder.volume_snapshots.create(volume_id, name=f'snapshot-{volume_id}')
    print(f"Snapshot creato: {snapshot.id}")

def schedule_snapshots(volume_id, interval_minutes=60):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: create_snapshot(volume_id), 'interval', minutes=interval_minutes)
    scheduler.start()

