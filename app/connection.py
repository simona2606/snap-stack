import os
from openstack import connection
import logging

def get_cinder_client():
    try:
        logging.info("Trying to create OpenStack connection...")
        conn = connection.Connection(
            auth_url=os.getenv('OS_AUTH_URL', 'http://192.168.64.2/identity/v3'),
            username=os.getenv('OS_USERNAME', 'admin'),
            password=os.getenv('OS_PASSWORD', 'secret'),
            project_name=os.getenv('OS_PROJECT_NAME', 'demo'),
            user_domain_id=os.getenv('OS_USER_DOMAIN_ID', 'default'),
            project_domain_id=os.getenv('OS_PROJECT_DOMAIN_ID', 'default'),
            region_name=os.getenv('OS_REGION_NAME', 'RegionOne')
        )
        logging.info("OpenStack connection created successfully.")
        return conn.block_storage  # Restituisci il client Cinder
    except Exception as e:
        logging.error(f"Error during OpenStack authentication: {e}")
        raise
