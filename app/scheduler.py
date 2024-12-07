from apscheduler.schedulers.background import BackgroundScheduler
import os
from monitor import monitor_volumes
from client import get_cinder_client
from notifications import logging
from config import load_config

config = load_config()

def create_snapshot(volume_id):
    try:
        cinder = get_cinder_client()
        snapshot = cinder.volume_snapshots.create(volume_id, name=f'snapshot-{volume_id}')
        logging.info(f"Snapshot created for volume {volume_id}: {snapshot.id}")
        return snapshot.id
    except Exception as e:
        logging.error(f"Error creating snapshot for volume {volume_id}: {e}")
        raise

def schedule_snapshots(volume_id, interval_minutes=60):
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: create_snapshot(volume_id), 'interval', minutes=interval_minutes)
        scheduler.start()
        logging.info(f"Snapshot scheduling started for volume {volume_id} every {interval_minutes} minutes.")
    except Exception as e:
        logging.error(f"Error scheduling snapshots for volume {volume_id}: {e}")
        raise

def start_monitoring():
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            monitor_volumes, 
            'interval', 
            minutes=config["monitoring"]["interval_minutes"]  # The interval from the configuration file
        )
        scheduler.start()
        logging.info("Started volume monitoring.")
    except Exception as e:
        logging.error(f"Error starting volume monitoring: {e}")
        raise

