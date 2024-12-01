from apscheduler.schedulers.background import BackgroundScheduler
import os
from monitor import monitor_volumes
from client import get_cinder_client

def create_snapshot(volume_id):
    try:
        cinder = get_cinder_client()
        snapshot = cinder.volume_snapshots.create(volume_id, name=f'snapshot-{volume_id}')
        print(f"Snapshot created for volume {volume_id}: {snapshot.id}")
        return snapshot.id
    except Exception as e:
        print(f"Error creating snapshot for volume {volume_id}: {e}")
        raise

def schedule_snapshots(volume_id, interval_minutes=60):
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: create_snapshot(volume_id), 'interval', minutes=interval_minutes)
        scheduler.start()
        print(f"Snapshot scheduling started for volume {volume_id} every {interval_minutes} minutes.")
    except Exception as e:
        print(f"Error scheduling snapshots for volume {volume_id}: {e}")
        raise

def start_monitoring():
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(monitor_volumes, 'interval', minutes=2)  # Monitor every 2 minutes
        scheduler.start()
        print("Started volume monitoring every 2 minutes.")
    except Exception as e:
        print(f"Error starting volume monitoring: {e}")
        raise
