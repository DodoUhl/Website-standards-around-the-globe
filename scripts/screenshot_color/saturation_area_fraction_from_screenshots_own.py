import subprocess
from minio import Minio
import cv2
import numpy as np
import csv
from pathlib import Path

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

    "Commercial": "Commercial", "Network": "Network",
    "Government": "Government", "Organisation": "Organisation",
}

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
# CSV vorbereiten
# ------------------------- 

objects = client.list_objects(bucket_name, recursive=True)
output_csv = Path("../../csv/screenshot_color/color_analysis_results.csv")
file_exists = output_csv.exists()

with open(output_csv, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow([
            "Continent", "Country", "Domain",
            "mean_hue", "mean_saturation", "mean_value",
            "color_ratio", "diversity", "score"
        ])

    # -------------------------
    # Screenshots analysieren
    # -------------------------    
    for obj in objects:
        if not obj.object_name.lower().endswith(".png"):
            continue
        
        filename = Path(obj.object_name).stem  # Country_Domain
        if "_" not in filename:
            continue
        
        country, domain = filename.split("_", 1)
        continent = COUNTRY_TO_CONTINENT.get(country, "Unknown")

        response = client.get_object(bucket_name, obj.object_name)
        image_bytes = response.read()
        response.close()
        response.release_conn()

        # Bild aus Bytes laden
        img_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img is None:
            continue

        # HSV Analyse (H-Farbton, S-Sättigung, V-Helligkeit)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #(RGB in HSV)
        h, s, v = cv2.split(hsv)

        mean_h = np.mean(h) # Durchschnittlicher Farbton
        mean_s = np.mean(s) # Durchschnittliche Sättigung
        mean_v = np.mean(v) # Durchschnittliche Helligkeit

        color_ratio = np.sum(s > 50) / s.size # Anteil farbiger Fläche (s > 50)-> Filtert weiß,grau,Text,Schatten und somit nur farbige Flächen

        hist = cv2.calcHist([h], [0], None, [30], [0, 180])
        diversity = np.count_nonzero(hist) # Wie viele unterschiedliche Farbtöne kommen vor

        score = round(mean_s * color_ratio * diversity, 4)

        writer.writerow([
            continent, country, domain,
            round(mean_h, 4), round(mean_s, 4), round(mean_v, 4),
            round(color_ratio, 4),
            diversity, score
        ])

        print(f"Analysiert: {continent} | {country} | {domain} → Score {score}")
