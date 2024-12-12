from client import get_cinder_client
from notifications import logging
from config import load_config

config = load_config()

def clean_old_snapshots(volume_id, keep_count=None):
    """
    Clean old snapshots for a specific volume, keeping the latest 'keep_count' snapshots.
    """
    try:
        cinder = get_cinder_client()
        keep_count = int(keep_count or config["storage"]["max_snapshots_per_volume"])  # Convert to integer
        snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
        snapshots_to_delete = sorted(snapshots, key=lambda s: s.created_at)[:-keep_count]

        for snapshot in snapshots_to_delete:
            snapshot_size = int(snapshot.size)  # Ensure snapshot.size is an integer
            cinder.volume_snapshots.delete(snapshot.id)
            logging.info(f"Snapshot deleted: {snapshot.id} (size: {snapshot_size} GB)")

    except Exception as e:
        logging.error(f"Error cleaning snapshots: {e}")

def enforce_storage_limits(volume_id, max_size_gb=None):
    try:
        cinder = get_cinder_client()
        max_size_gb = int(max_size_gb or config["storage"]["max_total_size_gb"])  # Convert to integer
        snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})

        total_size_gb = sum(snapshot.size for snapshot in snapshots)
        logging.info(f"Total size of snapshots for volume {volume_id}: {total_size_gb} GB")

        if total_size_gb > max_size_gb:
            logging.warning(f"Snapshot storage for volume {volume_id} exceeds {max_size_gb} GB. Cleaning up older snapshots.")
            snapshots_to_delete = sorted(snapshots, key=lambda s: s.created_at)
            for snapshot in snapshots_to_delete:
                if total_size_gb <= max_size_gb:
                    break
                cinder.volume_snapshots.delete(snapshot.id)
                total_size_gb -= snapshot.size
                logging.info(f"Deleted snapshot {snapshot.id}. Remaining size: {total_size_gb} GB")
    except Exception as e:
        logging.error(f"Error enforcing storage limits for volume {volume_id}: {e}")
