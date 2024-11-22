def clean_old_snapshots(volume_id, keep_count=3):
    cinder = get_cinder_client()
    snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
    snapshots_to_delete = sorted(snapshots, key=lambda s: s.created_at)[:-keep_count]
    for snapshot in snapshots_to_delete:
        cinder.volume_snapshots.delete(snapshot.id)
        print(f"Snapshot eliminato: {snapshot.id}")

