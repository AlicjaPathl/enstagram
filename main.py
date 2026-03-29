import os
import time
import random
import threading
import json
import requests
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FLAG = os.getenv('APP_FLAG', 'CTF{placeholder_flag}')
MIN_W = int(os.getenv('MIN_WAIT', 30))
MAX_W = int(os.getenv('MAX_WAIT', 300))

# Wczytaj zadania z JSON
with open('tasks.json', 'r', encoding='utf-8') as f:
    TASKS = json.load(f)


# --- Wątek 1: flaga (bez zmian) ---
def background_noise():
    while True:
        try:
            wait_time = random.randint(MIN_W, MAX_W)
            time.sleep(wait_time)
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


# --- Wątek 2: szum z tasks.json ---
def task_noise():
    endpoints = [
        lambda: requests.post(
            'http://127.0.0.1/api/login',
            data={
                'username': random.choice(TASKS['users']),
                'password': random.choice(TASKS['passwords'])
            }
        ),
        lambda: requests.post(
            'http://127.0.0.1/api/message',
            data={
                'from': random.choice(TASKS['users']),
                'body': random.choice(TASKS['messages'])
            }
        ),
        lambda: requests.post(
            'http://127.0.0.1/api/token',
            headers={
                'Authorization': random.choice(TASKS['tokens']),
                'User-Agent': 'AppClient/2.1'
            },
            data={'action': 'verify'}
        ),
    ]

    while True:
        try:
            wait_time = random.randint(MIN_W // 2, MAX_W // 2)
            time.sleep(wait_time)
            random.choice(endpoints)()
        except Exception:
            pass


threading.Thread(target=background_noise, daemon=True).start()
threading.Thread(target=task_noise, daemon=True).start()


# --- Endpointy aplikacji ---
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


# --- Endpointy szumu ---
@app.route('/internal_audit', methods=['POST'])
def internal_audit():
    return "Audit Logged", 200

@app.route('/api/login', methods=['POST'])
def api_login():
    return "OK", 200

@app.route('/api/message', methods=['POST'])
def api_message():
    return "OK", 200

@app.route('/api/token', methods=['POST'])
def api_token():
    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)