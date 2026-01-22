import subprocess
import pandas as pd
import warnings
from pathlib import Path
from minio import Minio
from PIL import Image
from io import BytesIO

# -----------------------------
# Pillow Settings
# -----------------------------
Image.MAX_IMAGE_PIXELS = None
warnings.simplefilter('ignore', Image.DecompressionBombWarning)

# -------------------------------
# Docker-Container starten
# -------------------------------
print("Starte Docker-Container...")
subprocess.run([
    "docker-compose",
    "-f",
    "/Users/dodo/Dateien/Studium/GitHub/5Semester/web-kraken/docker-compose.yaml",
    "up",
    "-d"
], check=True)

# -----------------------------
# CSV einlesen
# -----------------------------
file_path = Path("..") / "domain_lists" / "current.csv"
df = pd.read_csv(file_path)

# -----------------------------
# Länder und TLDs
# -----------------------------
countries_tlds = {
    # Europa
    "Deutschland": [".de"], "Frankreich": [".fr"], "UK": [".uk"], "Italien": [".it"], "Spanien": [".es"],
    "Niederlande": [".nl"], "Polen": [".pl"], "Schweden": [".se"], "Belgien": [".be"], "Österreich": [".at"],
    # Asien
    "Japan": [".jp"], "China": [".cn"], "Indien": [".in"], "Südkorea": [".kr"], "Singapur": [".sg"],
    "Thailand": [".th"], "VAE": [".ae"], "Malaysia": [".my"], "Philippinen": [".ph"], "Israel": [".il"],
    # Afrika
    "Südafrika": [".za"], "Nigeria": [".ng"], "Ägypten": [".eg"], "Kenia": [".ke"], "Marokko": [".ma"],
    "Ghana": [".gh"], "Tansania": [".tz"], "Uganda": [".ug"], "Senegal": [".sn"], "Tunesien": [".tn"],
    # Nordamerika
    "USA": [".us"], "Kanada": [".ca"], "Mexiko": [".mx"], "Guatemala": [".gt"], "Costa Rica": [".cr"],
    "Panama": [".pa"], "Dominikanische Republik": [".do"], "Honduras": [".hn"], "El Salvador": [".sv"], "Nicaragua": [".ni"],
    # Südamerika
    "Brasilien": [".br"], "Argentinien": [".ar"], "Chile": [".cl"], "Peru": [".pe"], "Kolumbien": [".co"],
    "Venezuela": [".ve"], "Bolivien": [".bo"], "Ecuador": [".ec"], "Paraguay": [".py"], "Uruguay": [".uy"],
    # Ozeanien
    "Australien": [".au"], "Neuseeland": [".nz"], "Samoa": [".ws"], "Tonga": [".to"],
    "Niue": [".nu"], "Palau": [".pw"], "Mikronesien": [".fm"], "Tuvalu": [".tv"]
}

# -----------------------------
# Country → Continent
# -----------------------------
COUNTRY_TO_CONTINENT = {}
for country, tlds in countries_tlds.items():
    if country in ["Deutschland", "Frankreich", "UK", "Italien", "Spanien", "Niederlande", "Polen", "Schweden", "Belgien", "Österreich"]:
        COUNTRY_TO_CONTINENT[country] = "Europa"
    elif country in ["Japan","China","Indien","Südkorea","Singapur","Thailand","VAE","Malaysia","Philippinen","Israel"]:
        COUNTRY_TO_CONTINENT[country] = "Asien"
    elif country in ["Südafrika","Nigeria","Ägypten","Kenia","Marokko","Ghana","Tansania","Uganda","Senegal","Tunesien"]:
        COUNTRY_TO_CONTINENT[country] = "Afrika"
    elif country in ["USA","Kanada","Mexiko","Guatemala","Costa Rica","Panama","Dominikanische Republik","Honduras","El Salvador","Nicaragua"]:
        COUNTRY_TO_CONTINENT[country] = "Nordamerika"
    elif country in ["Brasilien","Argentinien","Chile","Peru","Kolumbien","Venezuela","Bolivien","Ecuador","Paraguay","Uruguay"]:
        COUNTRY_TO_CONTINENT[country] = "Südamerika"
    else:
        COUNTRY_TO_CONTINENT[country] = "Ozeanien"

# -----------------------------
# Domains nach Ländern sammeln (Top 100)
# -----------------------------
country_domains = {}
for country, tlds in countries_tlds.items():
    domains = df[df['origin'].str.endswith(tuple(tlds))]['origin'].tolist()[:100]
    country_domains[country] = domains

# -----------------------------
# MinIO Verbindung
# -----------------------------
client = Minio(
    "s3.vs.uni-kassel.de",
    access_key="duhl",
    secret_key="norxot-Xypva6-byrguc",
    secure=False
)

bucket_screenshot = "crawler-screenshots"

# -----------------------------
# Screenshots auslesen und CSV vorbereiten
# -----------------------------
relevant_bases = set()
for domains in country_domains.values():
    for domain in domains:
        base = domain.replace("https://","").replace("www.","")
        relevant_bases.add(base)

rows = []
seen_bases = set()
counter = 0

for obj in client.list_objects(bucket_screenshot, recursive=True):
    if counter == len(relevant_bases):
        break
    name = obj.object_name

    if not name.endswith(".png"):
        continue

    # Domain extrahieren
    if "/http/" in name:
        domain_part = name.split("/http/")[-1]
    elif "/https/" in name:
        domain_part = name.split("/https/")[-1]
    else:
        continue

    base = domain_part.replace(".full.png","").replace(".png","")

    if base not in relevant_bases or base in seen_bases:
        continue

    seen_bases.add(base)
    counter +=1
    print(f"{counter} / {len(relevant_bases)} -> {base}")

    # Größe und Dimensionen
    response = client.get_object(bucket_screenshot, name)
    img_bytes = response.read()
    response.close()
    response.release_conn()

    size_bytes = len(img_bytes)
    with Image.open(BytesIO(img_bytes)) as img:
        width_px, height_px = img.size

    # Country & Continent ermitteln
    country = None
    for ctry, domains in country_domains.items():
        if any(base.endswith(d.replace("https://","").replace("www.","")) for d in domains):
            country = ctry
            break
    if country is None:
        country = "Unbekannt"
    continent = COUNTRY_TO_CONTINENT.get(country,"Unbekannt")

    # Row speichern
    rows.append({
        "continent": continent,
        "country": country,
        "domain": base,
        "size_bytes": size_bytes,
        "height_px": height_px,
        "width_px": width_px
    })

# -----------------------------
# CSV schreiben
# -----------------------------
df_out = pd.DataFrame(rows)
file_path = Path("..") / "csv" / "screenshot" / "crawler_minio_screenshots.csv"
df_out.to_csv(file_path, index=False)
print("CSV erstellt")
