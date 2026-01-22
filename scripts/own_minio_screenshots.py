import subprocess
from minio import Minio
from PIL import Image
from pathlib import Path
import pandas as pd
import warnings
import io
import os

Image.MAX_IMAGE_PIXELS = None
warnings.simplefilter("ignore", Image.DecompressionBombWarning)
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

# -------------------------
# MinIO Verbindung
# -------------------------
client = Minio(
    "localhost:9100",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "screenshots-crux"

# -------------------------
# Country → Continent
# -------------------------
COUNTRY_TO_CONTINENT = {
    "Deutschland": "Europa", "Frankreich": "Europa", "UK": "Europa",
    "Italien": "Europa", "Spanien": "Europa", "Niederlande": "Europa",
    "Polen": "Europa", "Schweden": "Europa", "Belgien": "Europa", "Österreich": "Europa",

    "Japan": "Asien", "China": "Asien", "Indien": "Asien", "Südkorea": "Asien",
    "Singapur": "Asien", "Thailand": "Asien", "VAE": "Asien", "Malaysia": "Asien",
    "Philippinen": "Asien", "Israel": "Asien",

    "Südafrika": "Afrika", "Nigeria": "Afrika", "Ägypten": "Afrika",
    "Kenia": "Afrika", "Marokko": "Afrika", "Ghana": "Afrika",
    "Tansania": "Afrika", "Uganda": "Afrika", "Senegal": "Afrika", "Tunesien": "Afrika",

    "USA": "Nordamerika", "Kanada": "Nordamerika", "Mexiko": "Nordamerika",
    "Guatemala": "Nordamerika", "Costa Rica": "Nordamerika", "Panama": "Nordamerika",
    "Dominikanische Republik": "Nordamerika", "Honduras": "Nordamerika",
    "El Salvador": "Nordamerika", "Nicaragua": "Nordamerika",

    "Brasilien": "Südamerika", "Argentinien": "Südamerika", "Chile": "Südamerika",
    "Peru": "Südamerika", "Kolumbien": "Südamerika", "Venezuela": "Südamerika",
    "Bolivien": "Südamerika", "Ecuador": "Südamerika",
    "Paraguay": "Südamerika", "Uruguay": "Südamerika",

    "Australien": "Ozeanien", "Neuseeland": "Ozeanien", "Samoa": "Ozeanien",
    "Tonga": "Ozeanien", "Niue": "Ozeanien", "Palau": "Ozeanien",
    "Mikronesien": "Ozeanien", "Tuvalu": "Ozeanien",
}

# -------------------------
# CSV Daten sammeln
# -------------------------
rows = []

objects = client.list_objects(bucket_name, recursive=True)

for obj in objects:
    if not obj.object_name.lower().endswith(".png"):
        continue

    filename = os.path.basename(obj.object_name)

    # Erwartetes Format: Land_Domain.png
    try:
        country, domain_png = filename.split("_", 1)
        domain = domain_png.replace(".png", "")
    except ValueError:
        print(f"⚠️ Übersprungen (falsches Format): {filename}")
        continue

    continent = COUNTRY_TO_CONTINENT.get(country, "Unbekannt")
    if continent == "Unbekannt":
        print("Unbekannt")
    # Datei laden
    response = client.get_object(bucket_name, obj.object_name)
    image_bytes = response.read()
    response.close()
    response.release_conn()

    size_bytes = len(image_bytes)

    # Bilddimensionen
    with Image.open(io.BytesIO(image_bytes)) as img:
        width_px, height_px = img.size

    rows.append({
        "continent": continent,
        "country": country,
        "domain": domain,
        "size_bytes": size_bytes,
        "height_px": height_px,
        "width_px": width_px
    })

# -------------------------
# CSV schreiben
# -------------------------
df = pd.DataFrame(rows)
file_path = Path("..") / "csv" / "screenshot" / "own_minio_screenshots.csv"
df.to_csv(file_path, index=False)
print("CSV erstellt")

