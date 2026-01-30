import subprocess
import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from minio import Minio
from deep_translator import GoogleTranslator

# -------------------------------
# Hilfsfunktionen
# -------------------------------

def extract_clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def translate_text(text: str, target="en", max_chars=4500) -> str:
    if not text:
        return ""

    translator = GoogleTranslator(source="auto", target=target)
    translated_parts = []

    for i in range(0, len(text), max_chars):
        chunk = text[i:i + max_chars]
        if not chunk.strip():
            continue

        try:
            translated = translator.translate(chunk)
            if isinstance(translated, str):
                translated_parts.append(translated)
            else:
                translated_parts.append(chunk)
            time.sleep(0.3)
        except Exception as e:
            print(f"Übersetzungsfehler: {e}")
            translated_parts.append(chunk)

    return " ".join(translated_parts)



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

# -----------------------------
# Länder und TLDs
# -----------------------------
countries_tlds = {
    "Commercial": [".com"], "Network": [".net"], "Government": [".gov"], "Organisation": [".org"]
}

# -----------------------------
# Country → Continent
# -----------------------------
COUNTRY_TO_CONTINENT = {
    "Commercial": "Commercial", "Network": "Network", "Government": "Government", "Organisation": "Organisation",
}

# -----------------------------
# Domains nach Ländern sammeln (Top 100)
# -----------------------------
country_domains = {}
for country, tlds in countries_tlds.items():
    domains = df[df['origin'].str.endswith(tuple(tlds))]['origin'].tolist()[:100]
    country_domains[country] = domains

# -----------------------------
# HTML Analyse + CSV schreiben
# -----------------------------
output_file = Path("../../csv/html/html_analysis_results.csv")
write_header = not output_file.exists()

done_domains = set()

if output_file.exists():
    df_done = pd.read_csv(output_file)
    done_domains = set(df_done['domain'].tolist())


with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    if write_header:
        writer.writerow([
            "continent",
            "country",
            "domain",
            "canonical_HTML_size",
            "downloaded_HTML_size",
            "number_of_meta_tags",
            "number_of_script_tags",
            "number_of_link_tags",
            "total_images",
            "character_count"
        ])
    counter = 0
    total_domains = sum(len(domains) for domains in country_domains.values())
    for country, domains in country_domains.items():
        continent = COUNTRY_TO_CONTINENT[country]

        for domain in domains:
            if domain in done_domains:
                counter+=1
                continue
            print(f"Analysiere {domain}")

            url = domain
            if not url.startswith("http"):
                url = "https://" + url

            try:
                response = requests.get(
                    url,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                downloaded_html = response.text
                downloaded_html_size = len(response.content)
            except Exception as e:
                print(f"Fehler beim Laden von {domain}: {e}")
                continue
            
            safe_domain = domain.replace("/", "_").replace(":", "_")
            html_file_path = Path(f"../../html/{country}_{safe_domain}.html")
            with open(html_file_path, "w", encoding="utf-8") as f:
                f.write(downloaded_html)

            counter += 1
            print(f"[{counter}/{total_domains}]")

            soup = BeautifulSoup(downloaded_html, "html.parser")

            canonical_html_size = round(len(re.sub(r"\s+", " ", soup.encode(formatter="minimal").decode()).strip()) / 1024,2)
            number_of_meta_tags = len(soup.find_all("meta"))
            number_of_script_tags = len(soup.find_all("script"))
            number_of_link_tags = len(soup.find_all("link"))
            total_images = len(soup.find_all("img"))

            clean_text = extract_clean_text(soup)
            translated_text = translate_text(clean_text)
            character_count = len(translated_text)

            writer.writerow([
                continent,
                country,
                domain,
                canonical_html_size,
                downloaded_html_size,
                number_of_meta_tags,
                number_of_script_tags,
                number_of_link_tags,
                total_images,
                character_count
            ])

            time.sleep(1)

client = Minio(
    "localhost:9100",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
bucket_html = "html-crux"
if not client.bucket_exists(bucket_html):
    client.make_bucket(bucket_html)

for html in Path("../../html").glob("*.html"):
    client.fput_object(
        bucket_html,
        html.name,
        str(html)
    )
print("Analyse abgeschlossen. CSV wurde erstellt.")