import pylast
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 📻 Last.fm credentials
API_KEY = "7c6d303ef29f29d821dfacd2552defa0"
API_SECRET = "d95baa4faec4630ea6ec0226ce807916"
USERNAME = "U773R1Y1NS4N3"
PASSWORD_HASH = pylast.md5("Julio411#")

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=USERNAME, password_hash=PASSWORD_HASH)

recent_tracks = network.get_user(USERNAME).get_recent_tracks(limit=1)

if recent_tracks:
    track = recent_tracks[0].track
    title = track.title
    artist = track.artist.name
    album = track.get_album()
    image_url = album.get_cover_image() if album else None

    # Widget dimensions
    W, H = 400, 600
    bg = Image.new("RGB", (W, H), "#dadada")
    draw = ImageDraw.Draw(bg)

    # iPod body
    draw.rounded_rectangle((0, 0, W, H), radius=40, fill="#dadada")

    # Screen
    screen_x, screen_y, screen_w, screen_h = 40, 40, 320, 180
    draw.rounded_rectangle((screen_x, screen_y, screen_x + screen_w, screen_y + screen_h),
                           radius=10, fill="#262626")

    # Album cover inside screen
    if image_url:
        try:
            response = requests.get(image_url)
            cover = Image.open(BytesIO(response.content)).resize((140, 140))
            bg.paste(cover, (screen_x + 10, screen_y + 20))
        except Exception as e:
            print("Error loading cover:", e)

    # Song text
    font = ImageFont.load_default()
    draw.text((screen_x + 160, screen_y + 30), title, font=font, fill="#ffffff")
    draw.text((screen_x + 160, screen_y + 70), f"by {artist}", font=font, fill="#bbbbbb")

    # Controls: circular base
    ctrl_x, ctrl_y = W // 2 - 100, 270
    draw.ellipse((ctrl_x, ctrl_y, ctrl_x + 200, ctrl_y + 200), fill="#ffffff")

    # 🎛Button text and icons
    draw.text((W // 2 - 20, ctrl_y + 20), "MENU", font=font, fill="#b4bcc5")  # Menu
    draw.polygon([(W // 2 - 40, ctrl_y + 100), (W // 2 - 20, ctrl_y + 90), (W // 2 - 40, ctrl_y + 80)], fill="#b4bcc5")  # Prev
    draw.polygon([(W // 2 + 40, ctrl_y + 80), (W // 2 + 20, ctrl_y + 90), (W // 2 + 40, ctrl_y + 100)], fill="#b4bcc5")  # Next
    draw.polygon([(W // 2 - 10, ctrl_y + 160), (W // 2 - 10, ctrl_y + 180), (W // 2 + 10, ctrl_y + 170)], fill="#b4bcc5")  # Play

    # Save
    bg.save("ipod_widget_white.png")
    print("Widget generado: ipod_widget_white.png")

else:
    print("No hay scrobbles recientes.")
