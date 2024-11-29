from scheduler import get_cinder_client

def monitor_volumes():
    cinder = get_cinder_client()
    for volume in cinder.volumes.list():
        if volume.status == 'error':
            print(f"Volume {volume.id} in error state!")
            restore_volume(volume.id)

