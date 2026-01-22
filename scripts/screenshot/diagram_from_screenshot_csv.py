import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pathlib import Path


# -----------------------------
# CSV einlesen
# -----------------------------
file_path = Path("../../csv/screenshot/all_screenshots.csv")
df = pd.read_csv(file_path, sep=";")

# -----------------------------
# Umrechnungen
# -----------------------------
df["size_kib"] = df["size_bytes"] / 1024
df["pixel_area"] = df["width_px"] * df["height_px"]
df["image_density"] = df["size_kib"] / df["pixel_area"]

# -----------------------------
# Aggregation pro Land
# -----------------------------

grouped = (
    df.groupby("country")
    .agg(
        avg_size_kib=("size_kib", "mean"),
        avg_width=("height_px", "mean"),
        avg_height=("width_px", "mean"),
        avg_density=("image_density", "mean"),
        count=("domain", "count")
    )
    .reset_index()
)

# Label mit Anzahl erzeugen
grouped["label"] = grouped["country"] + " (" + grouped["count"].astype(str) + ")"

# Sortierungen
size_sorted = grouped.sort_values("avg_size_kib")
width_sorted = grouped.sort_values("avg_width")
height_sorted = grouped.sort_values("avg_height")
density_sorted = grouped.sort_values("avg_density")

# -----------------------------
# Plot 1: Durchschnittliche Dateigröße
# -----------------------------
plt.figure(figsize=(10,10))
plt.barh(size_sorted["label"], size_sorted["avg_size_kib"])
plt.xlabel("Durchschnittliche Screenshot-Größe (KiB)")
plt.ylabel("Land")
plt.title("Durchschnittliche Screenshot-Größe pro Land")
plt.tight_layout()
file_path = Path("../../charts/screenshot/avg_screenshot_size_per_country.png")
plt.savefig(file_path)
plt.close()

# -----------------------------
# Plot 2: Durchschnittliche Breite
# -----------------------------
plt.figure(figsize=(10,10))
plt.barh(width_sorted["label"], width_sorted["avg_width"])
plt.xlabel("Durchschnittliche Screenshot-Breite (Pixel)")
plt.ylabel("Land")
plt.title("Durchschnittliche Screenshot-Breite pro Land")
plt.tight_layout()
file_path = Path("../../charts/screenshot/avg_screenshot_width_per_country.png")
plt.savefig(file_path)
plt.close()

# -----------------------------
# Plot 3: Durchschnittliche Höhe
# -----------------------------
plt.figure(figsize=(10,10))
plt.barh(height_sorted["label"], height_sorted["avg_height"])
plt.xlabel("Durchschnittliche Screenshot-Höhe (Pixel)")
plt.ylabel("Land")
plt.title("Durchschnittliche Screenshot-Höhe pro Land")
plt.tight_layout()
file_path = Path("../../charts/screenshot/avg_screenshot_height_per_country.png")
plt.savefig(file_path)
plt.close()

# -----------------------------
# Plot 4: Bilddichte
# -----------------------------
plt.figure(figsize=(10, 10))
plt.barh(grouped["label"], density_sorted["avg_density"])
plt.xlabel("Durchschnittliche Bilddichte (KiB)")
plt.ylabel("Land")
plt.title("Bilddichte von Webseiten-Screenshots pro Land")
plt.tight_layout()
file_path = Path("../../charts/screenshot/avg_screenshot_density_per_country.png")
plt.savefig(file_path)
plt.close()

# -----------------------------
# Aggregation pro Kontinent
# -----------------------------

continent_grouped = (
    df.groupby("continent")
    .agg(
        avg_size_kib=("size_kib", "mean"),
        avg_width=("width_px", "mean"),
        avg_height=("height_px", "mean"),
        avg_density=("image_density", "mean"),
        count=("domain", "count")
    )
    .reset_index()
)
continent_grouped["label"] = continent_grouped["continent"] + " (" + continent_grouped["count"].astype(str) + ")"

continent_size_sorted = continent_grouped.sort_values("avg_size_kib")
continent_width_sorted = continent_grouped.sort_values("avg_width")
continent_height_sorted = continent_grouped.sort_values("avg_height")
continent_density_sorted = continent_grouped.sort_values("avg_density")

# -----------------------------
# Plot 5: Durchschnittliche Größe Kontinent
# -----------------------------

plt.figure(figsize=(8,6))
plt.barh(continent_size_sorted["label"], continent_size_sorted["avg_size_kib"])
plt.xlabel("Durchschnittliche Screenshot-Größe (KiB)")
plt.ylabel("Kontinent")
plt.title("Durchschnittliche Screenshot-Größe pro Kontinent")
plt.tight_layout()
file_path = Path("../../charts/screenshot/avg_screenshot_size_per_continent.png")
plt.savefig(file_path)
plt.close()

# -----------------------------
# Plot 6: Durchschnittliche Breite Kontinent
# -----------------------------
plt.figure(figsize=(8,6))
plt.barh(continent_width_sorted["label"], continent_width_sorted["avg_width"])
plt.xlabel("Durchschnittliche Screenshot-Breite (Pixel)")
plt.ylabel("Kontinent")
plt.title("Durchschnittliche Screenshot-Breite pro Kontinent")
plt.tight_layout()
file_path = Path("../../charts/screenshot/avg_screenshot_width_per_continent.png")
plt.savefig(file_path)
plt.close()

# -----------------------------
# Plot 7: Durchschnittliche Höhe Kontinent
# -----------------------------
plt.figure(figsize=(8,6))
plt.barh(continent_height_sorted["label"], continent_height_sorted["avg_height"])
plt.xlabel("Durchschnittliche Screenshot-Höhe (Pixel)")
plt.ylabel("Kontinent")
plt.title("Durchschnittliche Screenshot-Höhe pro Kontinent")
plt.tight_layout()
file_path = Path("../../charts/screenshot/avg_screenshot_height_per_continent.png")
plt.savefig(file_path)
plt.close()

# -----------------------------
# Plot 8: Durchschnittliche Bilddichte Kontinent
# -----------------------------
plt.figure(figsize=(8,6))
plt.barh(continent_density_sorted["label"], continent_density_sorted["avg_density"])
plt.xlabel("Durchschnittliche Bilddichte (KiB)")
plt.ylabel("Kontinent")
plt.title("Durchschnittliche Bilddichte pro Kontinent")
plt.tight_layout()
file_path = Path("../../charts/screenshot/avg_screenshot_density_per_continent.png")
plt.savefig(file_path)
plt.close()

print("Diagramme erstellt")