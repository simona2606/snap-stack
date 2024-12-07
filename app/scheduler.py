from apscheduler.schedulers.background import BackgroundScheduler
from monitor import monitor_volumes
from client import get_cinder_client
from notifications import logging
from config import load_config
from storage import enforce_storage_limits, clean_old_snapshots

# Load configuration
config = load_config()

def combined_volume_management():
    """
    Monitor volumes and manage snapshots (enforce storage limits and clean old snapshots).
    """
    try:
        cinder = get_cinder_client()

        # Monitor volume states
        logging.info("Starting volume monitoring.")
        monitor_volumes()

        # Manage snapshots for each volume
        volumes = cinder.volumes.list()
        if not volumes:
            logging.warning("No volumes found for snapshot management.")
            return

        for volume in volumes:
            volume_id = volume.id
            logging.info(f"Managing snapshots for volume {volume_id}.")

            # Enforce storage limits
            enforce_storage_limits(volume_id)

            # Clean old snapshots
            clean_old_snapshots(volume_id)

        logging.info("Combined volume management completed successfully.")
    except Exception as e:
        logging.error(f"Error in combined volume management: {e}")

def create_snapshot(volume_id):
    """
    Create a snapshot for the given volume.
    """
    try:
        cinder = get_cinder_client()
        snapshot = cinder.volume_snapshots.create(volume_id, name=f'snapshot-{volume_id}')
        logging.info(f"Snapshot created for volume {volume_id}: {snapshot.id}")
        return snapshot.id
    except Exception as e:
        logging.error(f"Error creating snapshot for volume {volume_id}: {e}")
        raise

def start_combined_scheduler(scheduler):
    """
    Start the scheduler for combined volume monitoring and snapshot management.
    """
    try:
        interval_minutes = int(config["storage"].get("interval_minutes", 2))  # Default: 2 minutes
        scheduler.add_job(
            func=combined_volume_management,
            trigger='interval',
            minutes=interval_minutes,
            id="combined_volume_management",
            replace_existing=True
        )
        logging.info(f"Combined volume management job scheduled every {interval_minutes} minutes.")
    except Exception as e:
        logging.error(f"Error scheduling combined volume management: {e}")

def schedule_snapshots(scheduler, volume_id, interval_minutes=60):
    """
    Schedule periodic snapshots for a specific volume.
    """
    try:
        scheduler.add_job(
            func=lambda: create_snapshot(volume_id),
            trigger='interval',
            minutes=interval_minutes,
            id=f"snapshot_{volume_id}",
            replace_existing=True
        )
        logging.info(f"Snapshot scheduling started for volume {volume_id} every {interval_minutes} minutes.")
    except Exception as e:
        logging.error(f"Error scheduling snapshots for volume {volume_id}: {e}")
        raise

def start_monitoring(scheduler):
    """
    Start the scheduler for volume monitoring.
    """
    try:
        scheduler.add_job(
            monitor_volumes,
            'interval',
            minutes=config["monitoring"]["interval_minutes"],  # Interval from configuration
            id="monitor_volumes",
            replace_existing=True
        )
        logging.info("Started volume monitoring.")
    except Exception as e:
        logging.error(f"Error starting volume monitoring: {e}")
        raise
