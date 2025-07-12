import pylast
import requests
import xml.etree.ElementTree as ET
import base64

API_KEY = "7c6d303ef29f29d821dfacd2552defa0"
API_SECRET = "d95baa4faec4630ea6ec0226ce807916"
USERNAME = "U773R1Y1NS4N3"
PASSWORD_HASH = pylast.md5("Julio411#")

DEFAULT_COVER = "https://i.imgur.com/wt3P9ol.jpg"  # imagen por defecto

ET.register_namespace('', "http://www.w3.org/2000/svg")
ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
ET.register_namespace('html', "http://www.w3.org/1999/xhtml")
ns_svg = "http://www.w3.org/2000/svg"
ns_xlink = "http://www.w3.org/1999/xlink"

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

    base_speed = 0.35
    text_content = f"{title} - by {artist}"
    text_length = len(text_content)
    animation_duration = max(6, min(round(text_length * base_speed, 1), 30))

    scroll_text = ET.Element(f"{{{ns_svg}}}text", {
        "x": "340", "y": "63",
        "fill": "#e8e8e8",
        "font-size": "16",
        "font-family": "Verdana",
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
            print("⚠️ No se pudo obtener el cover.")
    except Exception as e:
        print("❌ Error al descargar el cover:", e)

    tree.write("ipodbase_updated.svg", encoding="utf-8", xml_declaration=True)
    print("✅ SVG actualizado con el último scrobble")

else:
    print("⛔ No hay scrobbles recientes.")
