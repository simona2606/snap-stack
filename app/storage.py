from client import get_cinder_client
from notifications import logging

def clean_old_snapshots(volume_id, keep_count=3):
    try:
        cinder = get_cinder_client() 
        snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
        snapshots_to_delete = sorted(snapshots, key=lambda s: s.created_at)[:-keep_count]
        for snapshot in snapshots_to_delete:
            cinder.volume_snapshots.delete(snapshot.id)
            logging.info(f"Snapshot deleted: {snapshot.id}")
    except Exception as e:
        logging.error(f"Error cleaning snapshots: {e}")

