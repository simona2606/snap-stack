from flask import Flask, render_template, request, redirect, url_for
from cinderclient import client
from apscheduler.schedulers.background import BackgroundScheduler

# Configurazione iniziale
app = Flask(__name__)
scheduler = BackgroundScheduler()

# Autenticazione OpenStack
def get_cinder_client():
    return client.Client(
        version='3',
        username='admin',
        password='secret',
        project_name='demo',
        auth_url='http://192.168.64.2/identity/v3'
    )

# Funzione per creare snapshot
def create_snapshot(volume_id):
    cinder = get_cinder_client()
    snapshot = cinder.volume_snapshots.create(volume_id, name=f'snapshot-{volume_id}')
    print(f"Snapshot creato per volume {volume_id}: {snapshot.id}")
    return snapshot.id

# Funzione per monitorare lo stato dei volumi
def list_volumes():
    cinder = get_cinder_client()
    return cinder.volumes.list()

# Funzione per ripristinare un volume
def restore_volume(volume_id, snapshot_id):
    cinder = get_cinder_client()
    cinder.volumes.revert_to_snapshot(volume_id, snapshot_id)
    print(f"Volume {volume_id} ripristinato dallo snapshot {snapshot_id}.")

# Rotazione degli snapshot
def clean_old_snapshots(volume_id, keep=3):
    cinder = get_cinder_client()
    snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
    snapshots.sort(key=lambda x: x.created_at, reverse=True)
    for snapshot in snapshots[keep:]:
        cinder.volume_snapshots.delete(snapshot.id)
        print(f"Snapshot eliminato: {snapshot.id}")

# Endpoint principale: elenco volumi
@app.route('/')
def index():
    volumes = list_volumes()
    return render_template('index.html', volumes=volumes)

# Creazione manuale di uno snapshot
@app.route('/snapshot/<volume_id>', methods=['POST'])
def snapshot(volume_id):
    snapshot_id = create_snapshot(volume_id)
    return redirect(url_for('index'))

# Pulizia snapshot vecchi
@app.route('/clean/<volume_id>', methods=['POST'])
def clean(volume_id):
    clean_old_snapshots(volume_id)
    return redirect(url_for('index'))

# Pagina per ripristinare un volume
@app.route('/restore/<volume_id>', methods=['GET', 'POST'])
def restore(volume_id):
    if request.method == 'POST':
        snapshot_id = request.form['snapshot_id']
        restore_volume(volume_id, snapshot_id)
        return redirect(url_for('index'))
    cinder = get_cinder_client()
    snapshots = cinder.volume_snapshots.list(search_opts={'volume_id': volume_id})
    return render_template('restore.html', volume_id=volume_id, snapshots=snapshots)

# Avvio dell'app Flask
if __name__ == '__main__':
    scheduler.start()
    app.run(host='0.0.0.0', port=5234)

