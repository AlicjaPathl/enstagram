import os
import time
import random
import threading
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Pobieranie flagi z pliku .env (środowiska)
FLAG = os.getenv('APP_FLAG', 'CTF{placeholder_flag}')
MIN_W = int(os.getenv('MIN_WAIT', 30))
MAX_W = int(os.getenv('MAX_WAIT', 300))


def background_noise():
    """Wysyła flagę w losowych odstępach czasu do samego siebie."""
    while True:
        try:
            # Losowanie czasu cierpliwości: 30s - 5min
            wait_time = random.randint(MIN_W, MAX_W)
            time.sleep(wait_time)

            # Ruch wewnątrz sieci Dockera (widoczny w Wiresharku na docker0)
            requests.post(
                'http://127.0.0.1/internal_audit',
                headers={
                    'X-Flag-Vault': FLAG,
                    'User-Agent': 'Internal-Security-Bot-v1.0'
                },
                data={'status': 'active', 'heartbeat': 'true'}
            )
        except Exception:
            pass


# Start wątku tła
threading.Thread(target=background_noise, daemon=True).start()


@app.route('/')
def index():
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', images=images)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file and file.filename != '':
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
    return redirect(url_for('index'))


@app.route('/internal_audit', methods=['POST'])
def internal_audit():
    # Ten endpoint tylko odbiera ruch "szumu"
    return "Audit Logged", 200


if __name__ == '__main__':
    # Uruchomienie na porcie 80
    app.run(host='0.0.0.0', port=80)