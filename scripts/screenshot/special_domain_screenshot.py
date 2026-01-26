import subprocess
import os
from PIL import Image
import io
import asyncio
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright
from minio import Minio
import warnings

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

# ======================================
# Konfiguration
# ======================================
INPUT_CSV = Path("../../domain_lists/current.csv")
OUTPUT_CSV = Path("../../csv/screenshot/all_screenshots.csv")
SCREENSHOT_DIR = Path("screenshots")

countries_tlds = {
    "Commercial": [".com"], "Network": [".net"], "Government": [".gov"], "Organisation": [".org"]
}
COUNTRY_TO_CONTINENT = {"Commercial": "Commercial", "Network": "Network", "Government": "Government",
    "Organisation": "Organisation",
}

SCREENSHOT_DIR.mkdir(exist_ok=True)

# ======================================
# CSV laden & Domains filtern
# ======================================
df = pd.read_csv(INPUT_CSV)

country_domains = {}
for country, tlds in countries_tlds.items():
    domains = df[df['origin'].str.endswith(tuple(tlds))]['origin'].tolist()[:100]
    filtered = []
    for origin in domains:
        base = (
            origin
            .replace("https://", "")
            .replace("http://", "")
            .replace("www.", "")
        )
        filtered.append(origin)

    country_domains[country] = filtered

# -----------------------------
# Fortschritts-Counter
# -----------------------------
counter = 0
total_screenshots = sum(len(domains) for domains in country_domains.values())

# ======================================
# Screenshot-Funktion
# ======================================
async def capture(country, url, semaphore):
    global counter
    async with semaphore:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()

            try:
                url_to_visit = url
                if not url.startswith("http://") and not url.startswith("https://"):
                    url_to_visit = "https://" + url

                await page.goto(url_to_visit, timeout=30000)
                await page.wait_for_timeout(1000)

                # Screenshot speichern
                file_path = SCREENSHOT_DIR / f"{country}_{url_to_visit.replace('https://','').replace('http://','').replace('/','_')}.png"
                await page.screenshot(path=file_path, full_page=True)

                counter += 1
                print(f"[{counter}/{total_screenshots}] OK: {country} - {url}")

                # Rückgabe nur mit Pfad, keine Dimensionen oder Größe
                return {
                    "country": country,
                    "domain": url,
                    "file_path": str(file_path)
                }

            except Exception as e:
                counter += 1
                print(f"[{counter}/{total_screenshots}] Fehler: {country} - {url} ({e})")
                return None

            finally:
                await browser.close()

# -----------------------------
# Screenshots erstellen
# -----------------------------
async def main():
    semaphore = asyncio.Semaphore(10)
    tasks = []
    for country, domains in country_domains.items():
        for url in domains:
            tasks.append(capture(country, url, semaphore))
    return await asyncio.gather(*tasks)

# ======================================
# Ergebnisse speichern (anhängen)
# ======================================
def save_results():
    client = Minio(
        "localhost:9100",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    bucket_name = "screenshots-crux"
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

        continent = COUNTRY_TO_CONTINENT.get(country)
        if continent is None:
            continue 
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
    df_new = pd.DataFrame(rows)

    if OUTPUT_CSV.exists():
        df_existing = pd.read_csv(OUTPUT_CSV, sep=";")
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(OUTPUT_CSV, sep=";", index=False)
    print(f"✅ {len(df_new)} Einträge an all_screenshots.csv angehängt")

    
# ======================================
# Upload zu MinIO
# ======================================
def upload_to_minio():
    client = Minio(
        "localhost:9100",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

    bucket = "screenshots-crux"
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    for img in SCREENSHOT_DIR.glob("*.png"):
        client.fput_object(bucket, img.name, str(img))

# ======================================
# Screenshots lokal löschen
# ======================================
def cleanup(results):
    for r in results:
        if r and Path(r["file_path"]).exists():
            Path(r["file_path"]).unlink()

    try:
        SCREENSHOT_DIR.rmdir()
    except OSError:
        pass

    print("Lokale Screenshots gelöscht")

# ======================================
# Main
# ======================================
if __name__ == "__main__":
    results = asyncio.run(main())
    upload_to_minio()
    cleanup(results)
    save_results()
    
