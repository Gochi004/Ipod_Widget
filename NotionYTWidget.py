import pylast
import requests
import xml.etree.ElementTree as ET
import base64
import os
from datetime import datetime

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
USERNAME = os.getenv("USERNAME")
PASSWORD_HASH = pylast.md5(os.getenv("PASSWORD"))

DEFAULT_COVER = "https://i.imgur.com/wt3P9ol.jpg"  # Imagen por defecto

# Namespaces SVG
ET.register_namespace('', "http://www.w3.org/2000/svg")
ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
ET.register_namespace('html', "http://www.w3.org/1999/xhtml")
ns_svg = "http://www.w3.org/2000/svg"
ns_xlink = "http://www.w3.org/1999/xlink"

# Conexión a Last.fm
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=USERNAME, password_hash=PASSWORD_HASH)
recent_tracks = network.get_user(USERNAME).get_recent_tracks(limit=1)

if recent_tracks:
    track_info = recent_tracks[0]
    track = track_info.track
    title = track.title
    artist = track.artist.name
    album_name = track_info.album
    image_url = None

    # Buscar carátula
    album = track.get_album()
    if album:
        try:
            image_url = album.get_cover_image(size=pylast.SIZE_LARGE)
        except:
            pass

    if not image_url and album_name:
        try:
            album_obj = network.get_album(artist, album_name)
            image_url = album_obj.get_cover_image(size=pylast.SIZE_LARGE)
        except:
            pass

    if not image_url:
        image_url = DEFAULT_COVER

    # Procesar SVG base
    tree = ET.parse("ipodbase.svg")
    root = tree.getroot()
    root.attrib["width"] = "641"
    root.attrib["height"] = "292"
    root.attrib["viewBox"] = "0 0 641 292"

    def remove_element(target, root):
        for parent in root.iter():
            for child in list(parent):
                if child is target:
                    parent.remove(child)
                    return True
        return False

    for elem in root.iter("{http://www.w3.org/1999/xhtml}font"):
        if "song" in (elem.text or ""):
            elem.text = ""

    clip_path = ET.Element(f"{{{ns_svg}}}clipPath", {"id": "clipText"})
    clip_rect = ET.Element(f"{{{ns_svg}}}rect", {
        "x": "54", "y": "43", "width": "280", "height": "30",
        "rx": "2.4", "ry": "2.4"
    })
    clip_path.append(clip_rect)
    defs = ET.Element(f"{{{ns_svg}}}defs")
    defs.append(clip_path)
    root.insert(0, defs)

    # Texto animado
    base_speed = 0.35
    text_content = f"{title} - by {artist}"
    text_length = len(text_content)
    animation_duration = max(6, min(round(text_length * base_speed, 1), 30))

    scroll_text = ET.Element(f"{{{ns_svg}}}text", {
        "x": "340", "y": "63",
        "fill": "#e8e8e8",
        "font-size": "16",
        "font-family": "Verdana, 'Noto Sans JP', sans-serif",
        "font-weight": "bold",
        "clip-path": "url(#clipText)"
    })
    scroll_text.text = text_content

    animate_elem = ET.Element(f"{{{ns_svg}}}animate", {
        "attributeName": "x",
        "from": "340",
        "to": "-400",
        "dur": f"{animation_duration}s",
        "repeatCount": "indefinite",
        "fill": "remove",
        "calcMode": "linear"
    })
    scroll_text.append(animate_elem)
    root.append(scroll_text)

    # Insertar carátula
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image_data = response.content
            mime_type = response.headers.get("Content-Type", "image/jpeg")
            base64_str = base64.b64encode(image_data).decode("utf-8")

            image_elem = ET.Element(f"{{{ns_svg}}}image", {
                f"{{{ns_xlink}}}href": f"data:{mime_type};base64,{base64_str}",
                "x": "126.5", "y": "89",
                "width": "135",
                "height": "135",
                "preserveAspectRatio": "xMidYMid slice"
            })

            for i, elem in enumerate(root.findall(".//{http://www.w3.org/2000/svg}rect")):
                if elem.attrib.get("x") == "126.5" and elem.attrib.get("y") == "89":
                    if remove_element(elem, root):
                        root.insert(i, image_elem)
                    break
        else:
            print("No se pudo descargar la carátula.")
    except Exception as e:
        print(f"Error al obtener la imagen: {e}")

    # Guardar SVG
    tree.write("ipodbase_updated.svg", encoding="utf-8", xml_declaration=True)
    print(f"SVG actualizado con: {text_content}")

    # Crear index.html con Google Fonts y cache busting
    version = datetime.now().strftime("%Y%m%d%H%M")
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Mi iPod Widget</title>
  <meta http-equiv="cache-control" content="no-cache">
  <meta http-equiv="expires" content="0">
  <meta http-equiv="pragma" content="no-cache">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP&display=swap" rel="stylesheet">
  <style>
    body {{
      background-color: #0f0f0f;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      font-family: 'Noto Sans JP', sans-serif;
    }}
    object {{
      box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }}
  </style>
</head>
<body>
  <object type="image/svg+xml" data="ipodbase_updated.svg?v={version}" width="700" height="800">
    No se pudo cargar el widget
  </object>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"index.html generado con versión: {version}")

else:
    print("No hay scrobbles recientes.")

