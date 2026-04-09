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
# CSV einlesen
# -----------------------------
csv_path = Path("../../csv/screenshot_color/color_analysis_results.csv")
df = pd.read_csv(csv_path)

# -----------------------------
# TLD für Diagramm
# -----------------------------
df["tld"] = df["Domain"].str.extract(r'(\.[a-z]{2,})$')
tld_per_country = df.groupby("Country")["tld"] \
    .agg(lambda x: x.value_counts().idxmax()) \
    .to_dict()
# -----------------------------
# Metriken, die wir plotten wollen
# -----------------------------
metrics = ["mean_hue", "mean_saturation", "mean_value", "color_ratio", "diversity", "score"]

# Mapping für deutsche Bezeichnungen
metric_labels = {
    "mean_hue": "Durchschnittlicher Farbton",
    "mean_saturation": "Durchschnittliche Sättigung",
    "mean_value": "Durchschnittliche Helligkeit",
    "color_ratio": "Anteil farbiger Fläche",
    "diversity": "Farbdifferenzierung",
    "score": "Farbreichtum (Score)"
}

country_to_continent = df.drop_duplicates("Country").set_index("Country")["Continent"].to_dict()
used_continents = set(country_to_continent.values())

handles = [
    mpatches.Patch(color=continent_colors[c], label=c)
    for c in used_continents
]
# -----------------------------
# Gruppierung nach Land
# -----------------------------
country_avg = df.groupby("Country")[metrics].mean()
country_count = df.groupby("Country").size()

for metric in metrics:
    data = country_avg[metric].sort_values(ascending=False)
    plot_colors = [
        continent_colors.get(country_to_continent[c], "gray")
        for c in data.index
    ]
    plt.figure(figsize=(10, 10))
    plt.barh(range(len(data)), data.values, color=plot_colors)
    plt.title(f"{metric_labels[metric]} pro Land")
    plt.xlabel(metric_labels[metric])
    plt.ylabel("Land")
    # Zeige Anzahl der Screenshots pro Land
    labels = [f"{c}({tld_per_country.get(c, '')}) ({country_count[c]})" for c in data.index]
    plt.yticks(range(len(labels)), labels)
    plt.gca().invert_yaxis()
    plt.legend(handles=handles, title="Continent")

    plt.tight_layout()
    save_path = Path(f"../../charts/screenshot_color/avg_country_{metric}.png")
    plt.savefig(save_path)
    plt.close()
# -----------------------------
# Gruppierung nach Kontinent
# -----------------------------
continent_avg = df.groupby("Continent")[metrics].mean()
continent_count = df.groupby("Continent").size()

for metric in metrics:
    data = continent_avg[metric].sort_values(ascending=False)
    
    plt.figure(figsize=(8, 6))
    plt.barh(range(len(data)), data.values)
    plt.title(f"{metric_labels[metric]} pro Kontinent")
    plt.xlabel(metric_labels[metric])
    plt.ylabel("Kontinent")
    # Zeige Anzahl der Screenshots pro Kontinent
    labels = [f"{c} ({continent_count[c]})" for c in data.index]
    plt.yticks(range(len(labels)), labels)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    save_path = Path(f"../../charts/screenshot_color/avg_continent_{metric}.png")
    plt.savefig(save_path)
    plt.close()
