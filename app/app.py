from flask import Flask, render_template, request, redirect, url_for, jsonify
from monitor import monitor_volumes
from restore import restore_volume
from scheduler import schedule_snapshots, start_combined_scheduler, start_monitoring
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

config = load_config()

# Function to create a snapshot 
def create_snapshot(volume_id):
    try:
        cinder = get_cinder_client()
        snapshot = cinder.volume_snapshots.create(volume_id, name=f'snapshot-{volume_id}')
        logging.info(f"Snapshot created for volume {volume_id}: {snapshot.id}")
        return snapshot.id
    except Exception as e:
        logging.error(f"Error creating snapshot for volume {volume_id}: {e}")
        raise

# Function to rotate old snapshots
def clean_snapshots(volume_id, keep_count):
    try:
        clean_old_snapshots(volume_id, keep_count=keep_count)
        logging.info("Old Snapshots successfully cleaned!")
    except Exception as e:
        logging.error(f"Error cleaning old snapshots for volume {volume_id}: {e}")
        raise

# Main endpoint: list all volumes
@app.route('/')
def index():
    try:
        cinder = get_cinder_client()
        volumes = cinder.volumes.list()
        message = None  # Default message is None if there are no alerts
        return render_template('index.html', volumes=volumes, message=message)
    except Exception as e:
        app.logger.error(f"Error retrieving volumes: {e}", exc_info=True)
        message = ("Error retrieving volumes", "danger")  # Error message
        return render_template('index.html', message=message)

# Endpoint to manually create a snapshot
@app.route('/snapshot/<volume_id>', methods=['POST'])
def snapshot(volume_id):
    try:
        create_snapshot(volume_id)
        logging.info("Snapshot created successfully!")
        message = ("Snapshot created successfully!", "success")  # Success message
    except Exception as e:
        logging.error("Error creating snapshot for volume {volume_id}: {e}")
        message = (f"Error creating snapshot for volume {volume_id}: {e}", "danger")  # Error message

    cinder = get_cinder_client()
    volumes = cinder.volumes.list()
    return render_template('index.html', message=message, volumes=volumes)

# Endpoint to manually clean old snapshots
@app.route('/clean/<volume_id>', methods=['POST'])
def clean(volume_id):
    try:
        keep_count = int(request.form.get('keep_count', 3))  # Default to 3 snapshots
        max_size_gb = int(request.form.get('max_size_gb', 50))  # Default to 50 GB
        
        # Enforce storage limits first
        enforce_storage_limits(volume_id, max_size_gb)
        
        # Clean old snapshots by count
        clean_snapshots(volume_id, keep_count=keep_count)
        
        logging.info("Old snapshots cleaned successfully!")
        message = ("Old snapshots cleaned successfully!", "success")  # Success message
    except Exception as e:
        logging.error(f"Error cleaning snapshots for volume {volume_id}: {e}")
        message = (f"Error cleaning snapshots for volume {volume_id}: {e}", "danger")  # Error message

    cinder = get_cinder_client()
    volumes = cinder.volumes.list()
    return render_template('index.html', message=message, volumes=volumes)

# Endpoint to monitor volume status
@app.route('/monitor', methods=['GET'])
def monitor():
    try:
        monitor_volumes()
        logging.info("Monitoring completed successfully!")
        message = ("Monitoring completed successfully.", "success")  # Success message
    except Exception as e:
        logging.error("Error monitoring volumes")
        message = ("Error monitoring volumes", "danger")  # Error message
    return render_template('index.html', message=message)

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
            message = ("Volume restored successfully!", "success")  # Success message
            return redirect(url_for('index', message=message))  # Redirect back to the index page after restoring the volume
        
        # If the request is GET, display the restore page with available snapshots for the volume
        snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
        return render_template('restore.html', volume_id=volume_id, snapshots=snapshots, message=None)
    
    except Exception as e:
        logging.error(f"Error restoring volume {volume_id}: {e}")
        message = (f"Error restoring volume {volume_id}: {e}", "danger")  # Error message
        return render_template('index.html', message=message)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    message = None

    if request.method == 'POST':
        try:
            # Raccogli i nuovi dati dal form
            new_data = request.form.to_dict(flat=False)
            
            # Converti i dati in un formato accettabile
            formatted_data = {}
            for key, value in new_data.items():
                section, subkey = key.split("[", 1)
                subkey = subkey.rstrip("]")
                if section not in formatted_data:
                    formatted_data[section] = {}
                formatted_data[section][subkey] = value[0]
            
            # Update the configuration
            updated_config = update_config(formatted_data)
            message = ("Settings updated successfully!", "success")
        except Exception as e:
            logging.error(f"Error updating settings: {str(e)}")
            message = (f"Error updating settings: {str(e)}", "danger")

    # View the configuration
    try:
        current_config = load_config()
        return render_template("settings.html", config=current_config, message=message)
    except Exception as e:
        logging.error(f"Error loading settings: {str(e)}")
        message = (f"Error loading settings: {str(e)}", "danger")
        return render_template("settings.html", config={}, message=message)

if __name__ == '__main__':
    try:
        # Start combined volume management and monitoring
        start_combined_scheduler(scheduler)
        start_monitoring(scheduler)

        # Start the scheduler and the Flask app.
        scheduler.start()
        app.run(
            host=config["app"]["host"], 
            port=config["app"]["port"]
        )
    except Exception as e:
        logging.error(f"Error starting the application: {e}")
