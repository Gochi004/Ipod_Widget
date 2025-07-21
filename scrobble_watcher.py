import requests
import pylast
import sys
import time
import os

# UTF-8 safe output (mostly for Windows, harmless on macOS)
try:
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
except:
    pass

# Config (replace with real values or use environment variables)
API_KEY = "API_KEY"
API_SECRET = "API_SECRET"
USERNAME = "USERNAME"
PASSWORD_HASH = pylast.md5("PASSWORD")  # Consider sourcing from env securely

GITHUB_TOKEN = "GH_TK"
WEBHOOK_URL = "https://api.github.com/repos/Gochi004/Ipod_Widget/dispatches"  

LAST_SCROBBLE_FILE = "last_scrobble.txt"
LOG_FILE = "scrobble_log.txt"

# Connect to Last.fm
network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=USERNAME,
    password_hash=PASSWORD_HASH
)

def safe_console(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print("Texto con caracteres especiales")

def log_scrobble(text):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def send_webhook():
    payload = {"event_type": "new_scrobble"}
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    safe_console(f"Webhook enviado → {response.status_code}")
    if response.status_code != 204:
        safe_console(f"GitHub dijo: {response.text}")

def load_last_scrobble():
    if os.path.exists(LAST_SCROBBLE_FILE):
        with open(LAST_SCROBBLE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_current_scrobble(title):
    with open(LAST_SCROBBLE_FILE, "w", encoding="utf-8") as f:
        f.write(title)

# One-shot scrobble check (no looping)
try:
    now_playing = network.get_user(USERNAME).get_now_playing()
    if now_playing:
        current_title = f"{now_playing.title} - {now_playing.artist.name}"
        previous_title = load_last_scrobble()

        if current_title != previous_title:
            safe_console(f"🎵 Nuevo tema: {current_title}")
            log_scrobble(current_title)
            save_current_scrobble(current_title)
            send_webhook()
        else:
            safe_console("Sin cambios en el tema actual")
    else:
        safe_console("No hay música en reproducción")
except Exception as e:
    safe_console(f"Error: {e}")
