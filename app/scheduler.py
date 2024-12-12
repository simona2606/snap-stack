from apscheduler.schedulers.background import BackgroundScheduler
from client import get_cinder_client
from notifications import logging, send_email
from config import load_config
from restore import restore_volume

# Load configuration
config = load_config()

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

def schedule_snapshot_jobs(scheduler):
    """
    Schedule a global job to create snapshots for all volumes periodically.
    """
    try:
        logging.info("Starting global snapshot job scheduling.")

        interval_minutes = int(config["storage"].get("snapshot_interval_minutes", 2))
        logging.info(f"Global snapshot interval: {interval_minutes} minutes.")

        # Schedule a single job to handle snapshot creation for all volumes
        def create_snapshots_for_all_volumes():
            try:
                cinder = get_cinder_client()
                volumes = cinder.volumes.list()

                if not volumes:
                    logging.warning("No volumes available for snapshot creation at this time.")
                    return

                for volume in volumes:
                    logging.info(f"Creating snapshot for volume {volume.id}.")
                    create_snapshot(volume.id)

            except Exception as e:
                logging.error(f"Error in global snapshot job: {e}")

        scheduler.add_job(
            func=create_snapshots_for_all_volumes,
            trigger='interval',
            minutes=interval_minutes,
            id="global_snapshot_job",
            replace_existing=True
        )
        logging.info("Global snapshot job scheduled successfully.")

    except Exception as e:
        logging.error(f"Error scheduling global snapshot job: {e}")

def monitor_and_restore_volumes():
    """
    Monitor volumes for errors, send notifications, and restore from the latest snapshot if needed.
    """
    try:
        cinder = get_cinder_client()
        error_volumes = []  # To store volumes in error state

        for volume in cinder.volumes.list():
            if volume.status == 'error':
                logging.warning(f"Volume {volume.id} in error state.")
                error_volumes.append(volume)

                # Find the last snapshot for the volume
                snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume.id})
                if snapshots:
                    latest_snapshot = sorted(snapshots, key=lambda s: s.created_at)[-1]
                    restored_name = f"restored-{volume.id}"
                    restore_volume(volume.id, latest_snapshot.id, restored_name)
                    logging.info(f"Volume {volume.id} restored from the snapshot {latest_snapshot.id}.")

        # Send email if there are volumes in error state
        if error_volumes:
            email_body = "\n".join([f"Volume {v.id} in error state and restored." for v in error_volumes])
            send_email("Volume Error and Restore Notification", email_body)

    except Exception as e:
        logging.error(f"Error during monitoring and restoring volumes: {e}")

def start_scheduler():
    """
    Start the scheduler for periodic tasks.
    """
    scheduler = BackgroundScheduler()
    try:
        # Schedule global snapshot creation
        schedule_snapshot_jobs(scheduler)

        # Schedule monitoring and restore
        monitoring_interval = int(config["monitoring"].get("monitoring_interval_minutes", 3))
        scheduler.add_job(
            func=monitor_and_restore_volumes,
            trigger='interval',
            minutes=monitoring_interval,
            id="monitor_and_restore_volumes",
            replace_existing=True
        )
        logging.info("Scheduled monitoring and restore job.")

        scheduler.start()
        logging.info("Scheduler started.")
    except Exception as e:
        logging.error(f"Error starting the scheduler: {e}")
        scheduler.shutdown()
