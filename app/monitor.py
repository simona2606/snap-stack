from client import get_cinder_client
from restore import restore_volume
from notifications import logging, send_email 

def monitor_volumes():
    try:
        cinder = get_cinder_client()
        error_volumes = []  # To store volumes in error state

        for volume in cinder.volumes.list():
            if volume.status == 'error':
                logging.warning(f"Volume {volume.id} in error state.")
                error_volumes.append(volume)

                # Find the last snapshot
                snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume.id})
                if snapshots:
                    latest_snapshot = sorted(snapshots, key=lambda s: s.created_at)[-1]
                    restore_volume(volume.id, latest_snapshot.id)
                    logging.info(f"Volume {volume.id} restored from the snapshot {latest_snapshot.id}")

        # Send email if there are volumes in error state
        if error_volumes:
            body = "\n".join([f"Volume {v.id} in error state." for v in error_volumes])
            send_email("Error in volumes", body)

    except Exception as e:
        logging.error(f"Error during volume monitoring: {e}")

