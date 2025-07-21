import requests
import pylast
import sys
import time
import os

# 📦 UTF-8 safe output (mostly for Windows, harmless on macOS)
try:
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
except:
    pass

# 🔐 Config — replace with actual credentials or use environment variables
API_KEY = "API_KEY"
API_SECRET = "API_SECRET"
USERNAME = "USERNAME"
PASSWORD_HASH = pylast.md5("PASSWORD")

GITHUB_TOKEN = "GH_TK"
WEBHOOK_URL = "https://api.github.com/repos/Gochi004/Ipod_Widget/dispatches"

LAST_SCROBBLE_FILE = "/Users/fercho/scripts/last_scrobble.txt"
LOG_FILE = "/Users/fercho/scripts/scrobble_log.txt"

# 🎧 Connect to Last.fm
network = pylast.LastFMNetwork(
    api_key=API_KEY,
    api_secret=API_SECRET,
    username=USERNAME,
    password_hash=PASSWORD_HASH
)

# 💬 Safe console print
def safe_console(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print("⚠️ Texto con caracteres especiales")

# 📁 Log new scrobble to file with timestamp
def log_scrobble(text):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

# 📡 Send webhook to GitHub
def send_webhook():
    payload = {"event_type": "new_scrobble"}
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    safe_console(f"📤 Webhook enviado → {response.status_code}")
    if response.status_code != 204:
        safe_console(f"⚠️ GitHub dijo: {response.text}")

# 📂 Load last saved track data
def load_last_scrobble():
    if os.path.exists(LAST_SCROBBLE_FILE):
        with open(LAST_SCROBBLE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

for _ in range(3):
    try:
        now_playing = network.get_user(USERNAME).get_now_playing()
        if now_playing:
            current_title = now_playing.title.strip()
            current_artist = now_playing.artist.name.strip()
            current_scrobble = f"{current_title}||{current_artist}"
            previous_scrobble = load_last_scrobble()

            if current_scrobble != previous_scrobble:
                safe_console(f"🎵 Nuevo tema detectado: {current_title} — {current_artist}")
                log_scrobble(current_scrobble)
                save_current_scrobble(current_scrobble)
                send_webhook()
            else:
                safe_console("🔁 Mismo tema — no se envía webhook")
        else:
            safe_console("🛑 No hay música en reproducción")
    except Exception as e:
        safe_console(f"💥 Error: {e}")

    time.sleep(20)  # Wait ~20 seconds before next check

