from flask import Flask, render_template, request, redirect, url_for, jsonify
from monitor import monitor_volumes
from restore import restore_volume
from scheduler import start_scheduler, update_jobs, create_snapshot 
from storage import clean_old_snapshots, enforce_storage_limits
from apscheduler.schedulers.background import BackgroundScheduler
import os
from client import get_cinder_client
from notifications import logging, send_email
from config import load_config, update_config
import yaml

# Initial configuration
app = Flask(__name__)

scheduler = BackgroundScheduler()

# Main endpoint: list all volumes
@app.route('/')
def index():
    try:
        cinder = get_cinder_client()
        volumes = cinder.volumes.list()
        message = request.args.get('message', None)
        category = request.args.get('category', None)
        return render_template('index.html', volumes=volumes, message=message, category=category)
    except Exception as e:
        app.logger.error(f"Error retrieving volumes: {e}", exc_info=True)
        message = "Error retrieving volumes"
        category = "danger"
        return render_template('index.html', message=message, category=category)

# Endpoint to manually create a snapshot
@app.route('/snapshot/<volume_id>', methods=['POST'])
def snapshot(volume_id):
    try:
        create_snapshot(volume_id)
        logging.info("Snapshot created successfully!")
        message = "Snapshot created successfully!"
        category = "success"
    except Exception as e:
        logging.error(f"Error creating snapshot for volume {volume_id}: {e}")
        message = f"Error creating snapshot: {e}"
        category = "danger"

    # Redirect to the index page, passing the message and category as query parameters
    return redirect(url_for('index', message=message, category=category))

# Endpoint to manually clean old snapshots
@app.route('/clean/<volume_id>', methods=['POST'])
def clean(volume_id):
    try:
        config = load_config()

        keep_count = int(request.form.get('keep_count', config["storage"]["max_snapshots_per_volume"])) 
        max_size_gb = int(request.form.get('max_size_gb', config["storage"]["max_total_size_gb"]))  

        # Enforce storage limits first
        enforce_storage_limits(volume_id, max_size_gb)

        # Clean old snapshots by count
        clean_old_snapshots(volume_id, keep_count=keep_count)  

        logging.info("Old snapshots cleaned successfully!")
        message = "Old snapshots cleaned successfully!"
        category = "success"
    except Exception as e:
        logging.error(f"Error cleaning snapshots for volume {volume_id}: {e}")
        message = f"Error cleaning snapshots: {e}"
        category = "danger"

    # Redirect to the index page with message and category as query parameters
    return redirect(url_for('index', message=message, category=category))

# Endpoint to monitor volume status
@app.route('/monitor', methods=['GET'])
def monitor():
    try:
        monitor_volumes()
        logging.info("Monitoring completed successfully!")
        message = "Monitoring completed successfully."
        category = "success"
    except Exception as e:
        logging.error("Error monitoring volumes")
        message = "Error monitoring volumes"
        category = "danger"

    # Redirect to the index page with message and category as query parameters
    return redirect(url_for('index', message=message, category=category))

# Endpoint to restore a volume
@app.route('/restore/<volume_id>', methods=['GET', 'POST'])
def restore(volume_id):
    try:
        cinder = get_cinder_client()

        # If the request is a POST (form submission), perform the restore action
        if request.method == 'POST':
            snapshot_id = request.form['snapshot_id']  # Retrieve the selected snapshot ID from the form
            volume_name = request.form['volume_name']

            restore_volume(volume_id, snapshot_id, volume_name) 
            logging.info("Volume restored successfully!")
            message = "Volume restored successfully!"
            category = "success"
            return redirect(url_for('index', message=message, category=category))

        # If the request is GET, display the restore page with available snapshots for the volume
        snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
        return render_template('restore.html', volume_id=volume_id, snapshots=snapshots, message=None)
    
    except Exception as e:
        logging.error(f"Error restoring volume {volume_id}: {e}")
        message = f"Error restoring volume: {e}"
        category = "danger"
        return redirect(url_for('index', message=message, category=category))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        try:
            # Take new value from the form
            new_data = request.form.to_dict(flat=False)

            # Convert data 
            formatted_data = {}
            for key, value in new_data.items():
                section, subkey = key.split("[", 1)
                subkey = subkey.rstrip("]")
                if section not in formatted_data:
                    formatted_data[section] = {}
                formatted_data[section][subkey] = value[0]

            # Update the configuration
            update_config(formatted_data)

            message = "Settings updated successfully!"
            category = "success"
        except Exception as e:
            logging.error(f"Error updating settings: {str(e)}")
            message = f"Error updating settings: {str(e)}"
            category = "danger"

        # Redirect to the settings page with message and category as query parameters
        return redirect(url_for('settings', message=message, category=category))

    # View the configuration
    try:
        current_config = load_config()
        message = request.args.get('message', None)
        category = request.args.get('category', None)
        return render_template("settings.html", config=current_config, message=message, category=category)
    except Exception as e:
        logging.error(f"Error loading settings: {str(e)}")
        return render_template("settings.html", config={}, message="Error loading settings", category="danger")

if __name__ == '__main__':
    try:
        config = load_config()

        start_scheduler(scheduler)

        app.run(
            host=config["app"]["host"], 
            port=config["app"]["port"]
        )
    except Exception as e:
        logging.error(f"Error starting the application: {e}")

