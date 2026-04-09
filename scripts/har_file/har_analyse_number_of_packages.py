import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Farbzuordnung pro Kontinent
continent_colors = {
    'Europa': '#0086D1',
    'Asien': '#FFB000',
    'Nordamerika': '#00B894',
    'Südamerika': '#FF6F00',
    'Afrika': '#E84393',
    'Ozeanien': '#00AEEF'
}

# -----------------------------
# CSVs einlesen
# -----------------------------
request_path = Path("../../csv/har_files/number_of_packages.csv.gz")
charts_path = Path("../../charts/har_files")
charts_path.mkdir(parents=True, exist_ok=True)

df_request = pd.read_csv(
    request_path, 
    compression="gzip",
    header=None,
    names=['continent', 'country', 'url', 'number_of_packages']
)
df_request = df_request[df_request['continent'] != 'Unbekannt']
df_request['tld'] = df_request['url'].str.extract(r'(\.[a-z]{2,})$')
tld_per_country = df_request.groupby(['continent', 'country'])['tld'] \
    .agg(lambda x: x.value_counts().idxmax()) \
    .reset_index()
#  -----------------------------
# Durchschnitt und Anzahl pro Land (number_of_packages)
# -----------------------------
agg_country = df_request.groupby(['continent', 'country'], as_index=False).agg(
    avg_number_of_packages=('number_of_packages', 'mean'),
    count=('number_of_packages', 'count')
)
agg_country = agg_country.merge(tld_per_country, on=['continent', 'country'], how='left')
agg_country = agg_country[agg_country['count'] > 30]
country_labels = {row['country']: f"{row['country']}({row['tld']}) ({row['count']})" for _, row in agg_country.iterrows()}
data = agg_country.set_index('country')['avg_number_of_packages'].sort_values(ascending=False)

# Mapping: country -> continent
country_to_continent = dict(zip(agg_country['country'], agg_country['continent']))
# Nur verwendete Kontinente
used_continents = set(country_to_continent[c] for c in data.index)

handles = [
    mpatches.Patch(color=continent_colors[cont], label=cont)
    for cont in used_continents
]
# Farben entsprechend der Reihenfolge der Daten
colors = [continent_colors.get(country_to_continent[c], 'gray') for c in data.index]
# -----------------------------
# Horizontales Balkendiagramm pro Land
# -----------------------------
plt.figure(figsize=(10, 10))
plt.barh(y=[country_labels[c] for c in data.index], width=data.values, color=colors)
plt.xlabel('Average Number of Requests')
plt.ylabel('Country')
plt.title('Average Number of Requests per Country')
plt.gca().invert_yaxis()
plt.legend(handles=handles, title="Continent")
plt.tight_layout()
plt.savefig(charts_path / f"avg_number_of_requests_country.png")
plt.close()

# -----------------------------
# Durchschnitt und Anzahl pro Kontinent (number_of_packages)
# -----------------------------
agg_continent = df_request.groupby('continent', as_index=False).agg(
    avg_number_of_packages=('number_of_packages', 'mean'),
    count=('number_of_packages', 'count')
)

continent_labels = {row['continent']: f"{row['continent']} ({row['count']})" for _, row in agg_continent.iterrows()}
data_cont = agg_continent.set_index('continent')['avg_number_of_packages'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Kontinent
# -----------------------------
plt.figure(figsize=(8, 6))
plt.barh(y=[continent_labels[c] for c in data_cont.index], width=data_cont.values)
plt.xlabel('Average Number of Requests')
plt.ylabel('Continent')
plt.title('Average Number of Requests per Continent')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_number_of_requests_continent.png")
plt.close()
