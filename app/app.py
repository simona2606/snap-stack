from flask import Flask, render_template, request, redirect, url_for
from monitor import monitor_volumes
from restore import restore_volume
from scheduler import schedule_snapshots
from storage import clean_old_snapshots
from apscheduler.schedulers.background import BackgroundScheduler
import os
from scheduler import get_cinder_client

# Initial configuration
app = Flask(__name__)
scheduler = BackgroundScheduler()

# Function to create a snapshot 
def create_snapshot(volume_id):
    try:
        cinder = get_cinder_client()
        snapshot = cinder.volume_snapshots.create(volume_id, name=f'snapshot-{volume_id}')
        print(f"Snapshot created for volume {volume_id}: {snapshot.id}")
        return snapshot.id
    except Exception as e:
        print(f"Error creating snapshot for volume {volume_id}: {e}")
        raise

# Function to rotate old snapshots
def clean_snapshots(volume_id):
    try:
        clean_old_snapshots(volume_id, keep_count=3)
    except Exception as e:
        print(f"Error cleaning old snapshots for volume {volume_id}: {e}")
        raise

# Main endpoint: list all volumes
@app.route('/')
def index():
    try:
        cinder = get_cinder_client()
        volumes = cinder.volumes.list()
        return render_template('index.html', volumes=volumes)
    except Exception as e:
        app.logger.error(f"Error retrieving volumes: {e}", exc_info=True)
        return "Error retrieving volumes", 500

# Endpoint to manually create a snapshot
@app.route('/snapshot/<volume_id>', methods=['POST'])
def snapshot(volume_id):
    try:
        create_snapshot(volume_id)
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error creating snapshot for volume {volume_id}: {e}")
        return f"Error creating snapshot for volume {volume_id}", 500

# Endpoint to manually clean old snapshots
@app.route('/clean/<volume_id>', methods=['POST'])
def clean(volume_id):
    try:
        clean_snapshots(volume_id)
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error cleaning snapshots for volume {volume_id}: {e}")
        return f"Error cleaning snapshots for volume {volume_id}", 500

# Endpoint to schedule automatic snapshots
@app.route('/schedule/<volume_id>', methods=['POST'])
def schedule(volume_id):
    try:
        schedule_snapshots(volume_id, interval_minutes=60)  # Adjust interval as needed
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error scheduling snapshots for volume {volume_id}: {e}")
        return f"Error scheduling snapshots for volume {volume_id}", 500

# Endpoint to monitor volume status
@app.route('/monitor', methods=['GET'])
def monitor():
    try:
        monitor_volumes()
        return "Monitoring completed. Check logs for details."
    except Exception as e:
        print(f"Error monitoring volumes: {e}")
        return "Error monitoring volumes", 500

# Endpoint to restore a volume
@app.route('/restore/<volume_id>', methods=['GET', 'POST'])
def restore(volume_id):
    try:
        cinder = get_cinder_client()
        if request.method == 'POST':
            snapshot_id = request.form['snapshot_id']
            restore_volume(volume_id, snapshot_id)
            return redirect(url_for('index'))
        snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
        return render_template('restore.html', volume_id=volume_id, snapshots=snapshots)
    except Exception as e:
        print(f"Error restoring volume {volume_id}: {e}")
        return f"Error restoring volume {volume_id}", 500

# Start the Flask app and the scheduler
if __name__ == '__main__':
    try:
        scheduler.start()
        app.run(host='0.0.0.0', port=5235)
    except Exception as e:
        print(f"Error starting the application: {e}")
