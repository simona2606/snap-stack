import os
from keystoneauth1.identity import v3
from keystoneauth1 import session
from cinderclient import client
from notifications import logging, send_email

def get_cinder_client():
    try:
        # Retrieve environment variables
        auth_url = os.getenv('OS_AUTH_URL')
        username = os.getenv('OS_USERNAME')
        password = os.getenv('OS_PASSWORD')
        project_name = os.getenv('OS_PROJECT_NAME')
        user_domain_id = os.getenv('OS_USER_DOMAIN_ID')
        project_domain_id = os.getenv('OS_PROJECT_DOMAIN_ID')

        # Ensure all required variables are set
        missing_env_vars = [
            var for var, value in [
                ('OS_AUTH_URL', auth_url),
                ('OS_USERNAME', username),
                ('OS_PASSWORD', password),
                ('OS_PROJECT_NAME', project_name),
                ('OS_USER_DOMAIN_ID', user_domain_id),
                ('OS_PROJECT_DOMAIN_ID', project_domain_id),
            ] if value is None
        ]

        if missing_env_vars:
            logging.error(f"Missing required environment variables: {', '.join(missing_env_vars)}")
            raise ValueError(f"Missing required environment variables: {', '.join(missing_env_vars)}")

        # Authentication configuration
        auth = v3.Password(
            auth_url=auth_url,
            username=username,
            password=password,
            project_name=project_name,
            user_domain_id=user_domain_id,
            project_domain_id=project_domain_id,
        )

        # Create a session
        sess = session.Session(auth=auth)

        # Return the Cinder client
        return client.Client('3', session=sess)

    except Exception as e:
        logging.error(f"Error creating Cinder client: {e}")
        raise

