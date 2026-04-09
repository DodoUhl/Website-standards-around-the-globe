import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# Farbzuordnung pro Kontinent
continent_colors = {
    'Europa': '#0086D1',
    'Asien': '#FFB000',
    'Nordamerika': '#00B894',
    'Südamerika': '#FF6F00',
    'Afrika': '#E84393',
    'Ozeanien': '#00AEEF',
    'Organisation': '#6C5CE7',   
    'Commercial': '#D63031',  
    'Network': '#2D3436',
    'Government': '#2E7D32'
}

# -----------------------------
# Pfade
# -----------------------------
csv_path = Path("../../csv/html/html_analysis_results.csv")
charts_path = Path("../../charts/html")
charts_path.mkdir(parents=True, exist_ok=True)

# -----------------------------
# CSV laden
# -----------------------------
df = pd.read_csv(csv_path)

# -----------------------------
# Filter:
# Nur relevante Webseiten
# -----------------------------
df = df[df["downloaded_HTML_size"] >= 10000]

# -----------------------------
# downloaded_HTML_size -> KiB
# -----------------------------
df["downloaded_HTML_size_kib"] = df["downloaded_HTML_size"] / 1024

# -----------------------------
# TLD zu Land
# -----------------------------
df["tld"] = df["domain"].str.extract(r'(\.[a-z]{2,})$')
tld_per_country = df.groupby("country")["tld"] \
    .agg(lambda x: x.value_counts().idxmax()) \
    .to_dict()

# -----------------------------
# Metriken (für Diagramme)
# -----------------------------
metrics = [
    "canonical_HTML_size",
    "downloaded_HTML_size_kib",
    "number_of_meta_tags",
    "number_of_script_tags",
    "number_of_link_tags",
    "total_images",
    "character_count",
]

# Lesbare Labels
metric_labels = {
    "canonical_HTML_size": "Canonical HTML Size (KB)",
    "downloaded_HTML_size_kib": "Downloaded HTML Size (KiB)",
    "number_of_meta_tags": "Number of Meta Tags",
    "number_of_script_tags": "Number of Script Tags",
    "number_of_link_tags": "Number of Link Tags",
    "total_images": "Total Images",
    "character_count": "Character Count",
}

# =============================
# DURCHSCHNITT + COUNT pro LAND
# =============================
country_avg = df.groupby("country")[metrics].mean()
country_count = df.groupby("country").size()

country_labels = {
    c: f"{c}({tld_per_country.get(c,'')}) ({country_count[c]})"
    for c in country_avg.index
}
country_to_continent = df.drop_duplicates("country").set_index("country")["continent"].to_dict()

colors = [
    continent_colors.get(country_to_continent[c], "gray")
    for c in country_avg.index
]
used_continents = set(country_to_continent.values())

handles = [
    mpatches.Patch(color=continent_colors[c], label=c)
    for c in used_continents
]
for metric in metrics:
    data = country_avg[metric].sort_values(ascending=False)
    colors = [
    continent_colors.get(country_to_continent[c], "gray")
    for c in data.index
    ]

    plt.figure(figsize=(10, 10))
    plt.barh(y=[country_labels[c] for c in data.index], width=data.values, color=colors)
    plt.xlabel(metric_labels[metric])
    plt.ylabel("Country")
    plt.title(
        f"Average {metric_labels[metric]} per Country"
    )
    plt.gca().invert_yaxis()
    plt.legend(handles=handles, title="Continent")
    plt.tight_layout()
    plt.savefig(charts_path / f"html_avg_country_{metric}.png")
    plt.close()

# =============================
# DURCHSCHNITT + COUNT pro KONTINENT
# =============================
continent_avg = df.groupby("continent")[metrics].mean()
continent_count = df.groupby("continent").size()

continent_labels = {
    c: f"{c} ({continent_count[c]})"
    for c in continent_avg.index
}

for metric in metrics:
    data = continent_avg[metric].sort_values(ascending=False)

    plt.figure(figsize=(8, 6))
    plt.barh(y=[continent_labels[c] for c in data.index], width=data.values)

    plt.xlabel(metric_labels[metric])
    plt.ylabel("Continent")
    plt.title(
        f"Average {metric_labels[metric]} per Continent"
    )

    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(charts_path / f"html_avg_continent_{metric}.png")
    plt.close()

print("Alle Diagramme erfolgreich erstellt")
