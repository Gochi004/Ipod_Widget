import time
import requests
import pylast
import sys

try:
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
except:
    pass

API_KEY = ""
API_SECRET = ""
USERNAME = ""
PASSWORD_HASH = pylast.md5("")

WEBHOOK_URL = "https://api.github.com/repos/Gochi004/Gochi004/dispatches"
GITHUB_TOKEN = ""  # reemplaza por el real
LAST_SCROBBLE_FILE = "last_scrobble.txt"

network = pylast.LastFMNetwork(
    api_key=API_KEY, api_secret=API_SECRET,
    username=USERNAME, password_hash=PASSWORD_HASH
)

def log_scrobble(text):
    with open("scrobble_log.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

def safe_console(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print("Srobble con caracteres especiales guardado en el log")

def send_webhook():
    payload = {"event_type": "new_scrobble"}
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    safe_console(f"📡 Webhook enviado: {response.status_code}")

def load_last_scrobble():
    try:
        with open(LAST_SCROBBLE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def save_current_scrobble(title):
    with open(LAST_SCROBBLE_FILE, "w", encoding="utf-8") as f:
        f.write(title)

while True:
    try:
        now_playing = network.get_user(USERNAME).get_now_playing()
        if now_playing:
            track = now_playing
            current_title = f"{track.title} - {track.artist.name}"
            previous_title = load_last_scrobble()

            if current_title != previous_title:
                safe_console(f"🎶 Nuevo Now Playing: {current_title}")
                log_scrobble(current_title)
                save_current_scrobble(current_title)
                send_webhook()
            else:
                safe_console("Sin cambios en el tema actual")
        else:
            safe_console("No hay música en reproducción")
    except Exception as e:
        safe_console(f"Error en el watcher: {e}")

    time.sleep(30)
