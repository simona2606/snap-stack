import os
from keystoneauth1.identity import v3
from keystoneauth1 import session
from cinderclient import client

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
