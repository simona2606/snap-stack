from client import get_cinder_client

def monitor_volumes():
    try:
        cinder = get_cinder_client() 
        for volume in cinder.volumes.list():
            if volume.status == 'error':
                print(f"Volume {volume.id} in error state!")
                snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume.id})
                if snapshots:
                    latest_snapshot = sorted(snapshots, key=lambda s: s.created_at)[-1]
                    restore_volume(volume.id, latest_snapshot.id)
    except Exception as e:
        print(f"Error monitoring volumes: {e}")
