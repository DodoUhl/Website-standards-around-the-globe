import subprocess
from minio import Minio
import pandas as pd
import cv2
import numpy as np
import csv
from pathlib import Path
from PIL import Image
from io import BytesIO
import warnings

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
file_path = Path("../../domain_lists/current.csv")
df = pd.read_csv(file_path)

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
# Domains nach Ländern sammeln (Top 100)
# -----------------------------
country_domains = {}
for country, tlds in countries_tlds.items():
    domains = df[df['origin'].str.endswith(tuple(tlds))]['origin'].tolist()[:100]
    country_domains[country] = domains

# -------------------------
# MinIO Verbindung
# -------------------------
client = Minio(
    "s3.vs.uni-kassel.de",
    access_key="duhl",
    secret_key="norxot-Xypva6-byrguc",
    secure=False
)

bucket_name = "crawler-screenshots"

# -------------------------
# CSV vorbereiten
# ------------------------- 

objects = client.list_objects(bucket_name, recursive=True)
output_csv = Path("../../csv/screenshot_color/color_analysis_results.csv")
file_exists = output_csv.exists()

relevant_bases = set()
for domains in country_domains.values():
    for domain in domains:
        base = domain.replace("https://","").replace("www.","")
        relevant_bases.add(base)

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
    seen_bases = set()
    for obj in objects:
        object_name = obj.object_name
        base = Path(object_name).stem   

        if base not in relevant_bases or base in seen_bases:
            continue

        if not obj.object_name.lower().endswith(".png"):
            continue
        
        response = client.get_object(bucket_name, object_name)
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

        # -----------------------
        # Country & Continent
        # -----------------------
        country = None
        for ctry, domains in country_domains.items():
            if any(
                base.endswith(
                    d.replace("https://", "").replace("www.", "")
                ) for d in domains
            ):
                country = ctry
                break

        if country is None:
            country = "Unbekannt"

        continent = COUNTRY_TO_CONTINENT.get(country, "Unbekannt")

        if score > 0:
            # -----------------------
            # CSV schreiben
            # -----------------------
            writer.writerow([
                continent, country, base,
                round(mean_h, 4), round(mean_s, 4), round(mean_v, 4),
                round(color_ratio, 4),
                diversity, score
            ])
            seen_bases.add(base)
            print(f"Analysiert: {continent} | {country} | {base} → Score {score}")
