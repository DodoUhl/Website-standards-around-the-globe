import requests
from pathlib import Path
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import os
import re

# ----------------------------------------
# URL → Länder-Mapping
# ----------------------------------------
url_to_country = {
    "https://www.toyota.de": "Deutschland",
    "https://www.toyota.fr": "Frankreich",
    "https://www.toyota.co.uk": "UK",
    "https://www.toyota.it": "Italien",
    "https://www.toyota.es": "Spanien",
    "https://www.toyota.com": "USA",
    "https://www.toyota.com.br": "Brasilien",
    "https://www.toyota.com.ar": "Argentinien",
    "https://www.toyota.jp": "Japan",
    "https://www.toyota.co.ke": "Kenia",
    "https://www.toyota.co.ug": "Uganda",
    "https://www.toyota.co.tz": "Tansania",
    "https://www.toyota.co.nz": "Neuseeland",
}

urls = list(url_to_country.keys())

# ----------------------------------------
# HTML-Analyse
# ----------------------------------------
def analyze_html(url):
    print(f"----------------------------------------")
    print(f"Analysiere {url} ...")
    print(f"----------------------------------------")

    response = requests.get(url, timeout=10, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # -------------------
    # Bilder zählen
    # -------------------
    img_tags_count = len(soup.find_all("img"))
    img_extensions = [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]
    unique_files = set()
    data_uri_count = 0

    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            if src.startswith("data:image/"):
                data_uri_count += 1
            elif any(src.lower().endswith(ext) for ext in img_extensions):
                unique_files.add(src)

    for tag in soup.find_all(["link", "script"]):
        href = tag.get("href") or tag.get("src")
        if href and any(href.lower().endswith(ext) for ext in img_extensions):
            unique_files.add(href)

    total_images = img_tags_count + len(unique_files) + data_uri_count

    # -------------------
    # Sichtbaren Text extrahieren
    # -------------------
    for tag in soup(["script", "style", "head", "meta", "noscript"]):
        tag.extract()

    visible_text = soup.get_text(separator=" ", strip=True)
    clean_text = re.sub(r"\s+", " ", visible_text)

    clean_text = soup.get_text(separator=" ", strip=True)

    # -------------------
    # Infos zurückgeben
    # -------------------
    info = {
        "URL": url,
        "Land": url_to_country[url],
        "Kanonische HTML Größe (KB)": round(len(re.sub(r"\s+", " ", soup.encode(formatter="minimal").decode()).strip()) / 1024, 2),
        "Download HTML Größe (KB)": round(len(response.text) / 1024, 2),
        "Anzahl <meta>": len(soup.find_all("meta")),
        "Anzahl <script>": len(soup.find_all("script")),
        "Anzahl <link>": len(soup.find_all("link")),
        "Anzahl <img>": img_tags_count,
        "Gesamt Bilder": total_images,
        "Anzahl Zeichen": clean_text
    }

    return info


# ----------------------------------------
# Diagramme erstellen
# ----------------------------------------
def create_comparison_charts(df):
    numeric_cols = df.select_dtypes(include=["number"]).columns 

    # -------------------
    # generische Diagramme
    # -------------------
    for col in numeric_cols:
        plt.figure(figsize=(16, 6)) 
        sorted_df = df.sort_values(by=col, ascending=False) 
        plt.barh(sorted_df["Land"], sorted_df[col]) 
        plt.gca().invert_yaxis() 
        plt.title(f"Vergleich: {col}") 
        plt.xlabel("Wert") 
        plt.ylabel("Land") 
        plt.tight_layout() 
        file_path = Path("..") / "charts" / f"{col.replace('<','').replace('>','')}.png"
        plt.savefig(file_path, dpi=300) 
        plt.close()

    # -------------------
    # Bilderdiagramm
    # -------------------
    sorted_idx = df["Gesamt Bilder"].argsort()[::-1]
    y_sorted = df["Land"].iloc[sorted_idx]
    x_img_sorted = df["Anzahl <img>"].iloc[sorted_idx]
    x_files_sorted = df["Bilddateien"].iloc[sorted_idx]
    x_datauri_sorted = df["Data-URI Bilder"].iloc[sorted_idx]

    plt.figure(figsize=(12, 7))
    plt.barh(y_sorted, x_img_sorted, label="<img>-Tags")
    plt.barh(y_sorted, x_files_sorted, left=x_img_sorted, label="Bilddateien")
    plt.barh(y_sorted, x_datauri_sorted, left=x_img_sorted + x_files_sorted, label="Data-URI Bilder")
    plt.gca().invert_yaxis()
    plt.xlabel("Anzahl Bilder")
    plt.title("Vergleich: <img>-Tags, Bilddateien, Data-URI Bilder")
    plt.legend()
    plt.tight_layout()
    plt.savefig("charts/Vergleich_Bilder.png", dpi=300)
    plt.close()


# ----------------------------------------
# Hauptprogramm
# ----------------------------------------
if __name__ == "__main__":
    results = [analyze_html(url) for url in urls]
    df = pd.DataFrame(results)

    create_comparison_charts(df)

    file_path = Path("..") / "csv" / "toyota_compare.csv"
    df.to_csv("file_path", index=False)
    print("CSV gespeichert")
    print("Diagramme gespeichert")
