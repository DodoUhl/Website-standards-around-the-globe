import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# CSV einlesen
# -----------------------------
csv_path = Path("../../csv/screenshot_color/color_analysis_results.csv")
df = pd.read_csv(csv_path)

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

# -----------------------------
# Gruppierung nach Land
# -----------------------------
country_avg = df.groupby("Country")[metrics].mean()
country_count = df.groupby("Country").size()

for metric in metrics:
    data = country_avg[metric].sort_values(ascending=False)
    
    plt.figure(figsize=(10, 10))
    plt.barh(range(len(data)), data.values)
    plt.title(f"{metric_labels[metric]} pro Land")
    plt.xlabel(metric_labels[metric])
    plt.ylabel("Land")
    # Zeige Anzahl der Screenshots pro Land
    labels = [f"{c} ({country_count[c]})" for c in data.index]
    plt.yticks(range(len(labels)), labels)
    plt.gca().invert_yaxis()
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
