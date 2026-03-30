import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# -----------------------------
# CSVs einlesen
# -----------------------------
request_path = Path("../../csv/har_files/screenshot_and_dom_size.csv.gz")
charts_path = Path("../../charts/har_files")
charts_path.mkdir(parents=True, exist_ok=True)

df_request = pd.read_csv(
    request_path, 
    compression="gzip",
    header=None,
    names=['continent', 'country', 'url', 'dom_size', 'screenshot_size']
)

df_request['dom_size'] = df_request['dom_size'] / 1024
df_request['screenshot_size'] = df_request['screenshot_size'] / 1024

#  -----------------------------
# Durchschnitt und Anzahl pro Land (dom_size)
# -----------------------------
agg_country = df_request.groupby(['continent', 'country'], as_index=False).agg(
    avg_dom_size=('dom_size', 'mean'),
    count=('dom_size', 'count')
)

agg_country = agg_country[agg_country['count'] > 30]
country_labels = {row['country']: f"{row['country']} ({row['count']})" for _, row in agg_country.iterrows()}
data = agg_country.set_index('country')['avg_dom_size'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Land
# -----------------------------
plt.figure(figsize=(10, 10))
plt.barh(y=[country_labels[c] for c in data.index], width=data.values)
plt.xlabel('Average HTML Size (KiB)')
plt.ylabel('Country')
plt.title('Average HTML Size per Country')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_dom_size_country.png")
plt.close()

#  -----------------------------
# Durchschnitt und Anzahl pro Land (screenshot_size)
# -----------------------------
agg_country = df_request.groupby(['continent', 'country'], as_index=False).agg(
    avg_screenshot_size=('screenshot_size', 'mean'),
    count=('screenshot_size', 'count')
)

agg_country = agg_country[agg_country['count'] > 30]
country_labels = {row['country']: f"{row['country']} ({row['count']})" for _, row in agg_country.iterrows()}
data = agg_country.set_index('country')['avg_screenshot_size'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Land
# -----------------------------
plt.figure(figsize=(10, 10))
plt.barh(y=[country_labels[c] for c in data.index], width=data.values)
plt.xlabel('Average Screenshot Size (KiB)')
plt.ylabel('Country')
plt.title('Average Screenshot Size per Country')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_screenshot_size_country.png")
plt.close()

# -----------------------------
# Durchschnitt und Anzahl pro Kontinent (dom_size)
# -----------------------------
agg_continent = df_request.groupby('continent', as_index=False).agg(
    avg_dom_size=('dom_size', 'mean'),
    count=('dom_size', 'count')
)

continent_labels = {row['continent']: f"{row['continent']} ({row['count']})" for _, row in agg_continent.iterrows()}
data_cont = agg_continent.set_index('continent')['avg_dom_size'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Kontinent
# -----------------------------
plt.figure(figsize=(8, 6))
plt.barh(y=[continent_labels[c] for c in data_cont.index], width=data_cont.values)
plt.xlabel('Average HTML Size (KiB)')
plt.ylabel('Continent')
plt.title('Average HTML Size per Continent')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_dom_size_continent.png")
plt.close()


# -----------------------------
# Durchschnitt und Anzahl pro Kontinent (screenshot_size)
# -----------------------------
agg_continent = df_request.groupby('continent', as_index=False).agg(
    avg_screenshot_size=('screenshot_size', 'mean'),
    count=('screenshot_size', 'count')
)

continent_labels = {row['continent']: f"{row['continent']} ({row['count']})" for _, row in agg_continent.iterrows()}
data_cont = agg_continent.set_index('continent')['avg_screenshot_size'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Kontinent
# -----------------------------
plt.figure(figsize=(8, 6))
plt.barh(y=[continent_labels[c] for c in data_cont.index], width=data_cont.values)
plt.xlabel('Average Screenshot Size (KiB)')
plt.ylabel('Continent')
plt.title('Average Screenshot Size per Continent')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_screenshot_size_continent.png")
plt.close()