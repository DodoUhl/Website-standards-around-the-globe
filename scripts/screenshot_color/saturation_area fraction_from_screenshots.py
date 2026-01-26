import subprocess
from minio import Minio
import cv2
import numpy as np

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
# Screenshots analysieren
# -------------------------

objects = client.list_objects(bucket_name, recursive=True)
results = []
for obj in objects:
    if not obj.object_name.lower().endswith(".png"):
        continue
    
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

    mean_saturation = np.mean(s)
    color_ratio = np.sum(s > 50) / s.size

    hist = cv2.calcHist([h], [0], None, [30], [0, 180])
    diversity = np.count_nonzero(hist)

    score = round(mean_saturation * color_ratio * diversity, 2)

    print(f"{obj.object_name}: Color-Score = {score}")

    results.append((obj.object_name, score))

    # Nach 2 Bildern abbrechen
    if len(results) == 2:
        break
    
# -------------------------
# Vergleich
# -------------------------
if len(results) == 2:
    (name1, score1), (name2, score2) = results

    print("\nVergleich der Webseiten:")
    if score1 > score2:
        print(f"➡️ {name1} ist farbreicher als {name2}")
    elif score2 > score1:
        print(f"➡️ {name2} ist farbreicher als {name1}")
    else:
        print("➡️ Beide Seiten sind ähnlich farbreich")
else:
    print("Nicht genügend Screenshots gefunden.")