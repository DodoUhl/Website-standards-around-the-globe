import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# -----------------------------
# CSVs einlesen
# -----------------------------
request_path = Path("../../csv/har_files/request_duration.csv.gz")
charts_path = Path("../../charts/har_files")
charts_path.mkdir(parents=True, exist_ok=True)

df_request = pd.read_csv(
    request_path, 
    compression="gzip",
    header=None,
    names=['continent', 'country', 'request_url', 'request_duration']
)

#  -----------------------------
# Durchschnitt und Anzahl pro Land
# -----------------------------
agg_country = df_request.groupby(['continent', 'country'], as_index=False).agg(
    avg_request_duration=('request_duration', 'mean'),
    count=('request_duration', 'count')
)

agg_country = agg_country[agg_country['count'] > 30]
country_labels = {row['country']: f"{row['country']} ({row['count']})" for _, row in agg_country.iterrows()}
data = agg_country.set_index('country')['avg_request_duration'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Land
# -----------------------------
plt.figure(figsize=(10, 10))
plt.barh(y=[country_labels[c] for c in data.index], width=data.values)
plt.xlabel('Average Request Duration (ms)')
plt.ylabel('Country')
plt.title('Average Request Duration per Country')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_request_duration_country.png")
plt.close()

# -----------------------------
# Durchschnitt und Anzahl pro Kontinent
# -----------------------------
agg_continent = df_request.groupby('continent', as_index=False).agg(
    avg_request_duration=('request_duration', 'mean'),
    count=('request_duration', 'count')
)

continent_labels = {row['continent']: f"{row['continent']} ({row['count']})" for _, row in agg_continent.iterrows()}
data_cont = agg_continent.set_index('continent')['avg_request_duration'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Kontinent
# -----------------------------
plt.figure(figsize=(8, 6))
plt.barh(y=[continent_labels[c] for c in data_cont.index], width=data_cont.values)
plt.xlabel('Average Request Duration (ms)')
plt.ylabel('Continent')
plt.title('Average Request Duration per Continent')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_request_duration_continent.png")
plt.close()