from scheduler import get_cinder_client

def restore_volume(volume_id, snapshot_id):
    try:
        cinder = get_cinder_client()
        # Retrieve the selected snapshot using its ID
        snapshot = cinder.volume_snapshots.get(snapshot_id)

        # Check if the snapshot belongs to the correct volume
        if snapshot.volume_id != volume_id:
            print(f"Snapshot {snapshot_id} does not belong to volume {volume_id}.")
            return

        # Create a new volume from the snapshot
        restored_volume = cinder.volumes.create(size=snapshot.size, snapshot_id=snapshot.id)
        print(f"Volume {restored_volume.id} restored from snapshot {snapshot.id}")

    except Exception as e:
        print(f"Error restoring volume {volume_id} from snapshot {snapshot_id}: {e}")

