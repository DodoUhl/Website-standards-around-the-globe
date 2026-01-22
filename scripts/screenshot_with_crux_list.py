import asyncio
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright
import matplotlib.pyplot as plt
from PIL import Image
from minio import Minio


# -----------------------------
# CSV einlesen
# -----------------------------
file_path = Path("..") / "domain_lists" / "current.csv"
df = pd.read_csv(file_path)
file_path = Path("..") / "csv" / "screenshot" / "crawler_minio_screenshots.csv"
df_png = pd.read_csv(file_path, sep=";")
processed_bases = set(df_png["domain"])
# -----------------------------
# Länder und TLDs (10 pro Kontinent)
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
    "Panama": [".pa"], "Dominikanische Republik": [".do"], "Honduras": [".hn"],
    "El Salvador": [".sv"], "Nicaragua": [".ni"],

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
    filtered = []
    for origin in domains:
        base = (
            origin
            .replace("https://", "")
            .replace("http://", "")
            .replace("www.", "")
        )

        if base not in processed_bases:
            filtered.append(origin)

    country_domains[country] = filtered

# -----------------------------
# Verzeichnisse
# -----------------------------
screenshot_dir = Path("screenshots")
screenshot_dir.mkdir(exist_ok=True)

# -----------------------------
# Fortschritts-Counter
# -----------------------------
counter = 0
total_screenshots = sum(len(domains) for domains in country_domains.values())

## -----------------------------
# Screenshot-Funktion
# -----------------------------
async def capture(country, url, semaphore):
    global counter
    async with semaphore:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(viewport={"width":1920,"height":1080})
            page = await context.new_page()

            try:
                url_to_visit = url
                if not url.startswith("http://") and not url.startswith("https://"):
                    url_to_visit = "https://" + url

                await page.goto(url_to_visit, timeout=30000)
                await page.wait_for_timeout(1000)

                # Screenshot speichern
                file_path = screenshot_dir / f"{country}_{url_to_visit.replace('https://','').replace('http://','').replace('/','_')}.png"
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

# -----------------------------
# Ergebnisse speichern
# -----------------------------
def save_results(results):
    client = Minio(
        "localhost:9100",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    bucket_screenshot = "screenshots-crux"
    if not client.bucket_exists(bucket_screenshot):
        client.make_bucket(bucket_screenshot)

    for img in Path("screenshots").glob("*.png"):
        client.fput_object(
            bucket_screenshot,
            img.name,
            str(img)
        )
    return df

# -----------------------------
# Screenshots löschen
# -----------------------------
def delete_screenshots(results):
    folders_to_check = set()

    for item in results:
        if item and item.get("file_path"):
            path = Path(item["file_path"])

            if path.exists() and path.is_file():
                folders_to_check.add(path.parent)
                path.unlink()

    # Leere Ordner löschen
    for folder in folders_to_check:
        try:
            folder.rmdir()
        except OSError:
            pass
    print("Alle Screenshots wurden gelöscht.")

# -----------------------------
# Skript starten
# -----------------------------
if __name__ == "__main__":
    results = asyncio.run(main())
    df = save_results(results)
    delete_screenshots(results)
