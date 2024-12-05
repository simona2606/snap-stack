from client import get_cinder_client
from notifications import logging

def restore_volume(volume_id, snapshot_id, volume_name):
    try:
        cinder = get_cinder_client()
        # Retrieve the selected snapshot using its ID
        snapshot = cinder.volume_snapshots.get(snapshot_id)

        # Check if the snapshot belongs to the correct volume
        if snapshot.volume_id != volume_id:
            logging.error(f"Snapshot {snapshot_id} does not belong to volume {volume_id}.")
            return

        # Create a new volume from the snapshot and assign the name
        restored_volume = cinder.volumes.create(size=snapshot.size, snapshot_id=snapshot.id, name=volume_name)
        logging.info(f"Volume {restored_volume.id} restored from snapshot {snapshot.id} with name '{volume_name}'.")

    except Exception as e:
        logging.error(f"Error restoring volume {volume_id} from snapshot {snapshot_id}: {e}")
