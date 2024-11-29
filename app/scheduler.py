from apscheduler.schedulers.background import BackgroundScheduler
#from connection import get_cinder_client
from cinderclient import client
import os
from keystoneauth1.identity import v3
from keystoneauth1 import session

def get_cinder_client():
    try:
        # Authentication Configuration
        auth = v3.Password(
            auth_url=os.getenv('OS_AUTH_URL', 'http://192.168.64.2/identity/v3'),
            username=os.getenv('OS_USERNAME', 'admin'),
            password=os.getenv('OS_PASSWORD', 'secret'),
            project_name=os.getenv('OS_PROJECT_NAME', 'demo'),
            user_domain_id=os.getenv('OS_USER_DOMAIN_ID', 'default'),
            project_domain_id=os.getenv('OS_PROJECT_DOMAIN_ID', 'default'),
        )

        # Session Creation
        sess = session.Session(auth=auth)

        return client.Client('3', session=sess)
    except Exception as e:
        print(f"Error creating Cinder client: {e}")
        raise

def create_snapshot(volume_id):
    cinder = get_cinder_client()
    snapshot = cinder.volume_snapshots.create(volume_id, name=f'snapshot-{volume_id}')
    print(f"Snapshot created: {snapshot.id}")

def schedule_snapshots(volume_id, interval_minutes=60):
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: create_snapshot(volume_id), 'interval', minutes=interval_minutes)
    scheduler.start()

