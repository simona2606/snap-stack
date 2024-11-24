from scheduler import get_cinder_client

def restore_volume(volume_id):
    cinder = get_cinder_client()
    snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
    if snapshots:
        latest_snapshot = sorted(snapshots, key=lambda s: s.created_at, reverse=True)[0]
        restored_volume = cinder.volumes.create(size=latest_snapshot.size, snapshot_id=latest_snapshot.id)
        print(f"Volume ripristinato: {restored_volume.id}")
    else:
        print(f"Nessun snapshot valido trovato per il volume {volume_id}")

