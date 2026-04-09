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
request_path = Path("../../csv/har_files/page_timing_load.csv.gz")
charts_path = Path("../../charts/har_files")
charts_path.mkdir(parents=True, exist_ok=True)

df_request = pd.read_csv(
    request_path, 
    compression="gzip",
    header=None,
    names=['continent', 'country', 'url', 'page_timing_content_load', 'page_timing_load']
)
df_request['tld'] = df_request['url'].str.extract(r'(\.[a-z]{2,})$')
tld_per_country = df_request.groupby(['continent', 'country'])['tld'] \
    .agg(lambda x: x.value_counts().idxmax()) \
    .reset_index()
#  -----------------------------
# Durchschnitt und Anzahl pro Land (page_timing_content_load)
# -----------------------------
agg_country = df_request.groupby(['continent', 'country'], as_index=False).agg(
    avg_page_timing_content_load=('page_timing_content_load', 'mean'),
    count=('page_timing_content_load', 'count')
)
agg_country = agg_country.merge(tld_per_country, on=['continent', 'country'], how='left')

agg_country = agg_country[agg_country['count'] > 30]
country_labels = {row['country']: f"{row['country']}({row['tld']}) ({row['count']})" for _, row in agg_country.iterrows()}
data = agg_country.set_index('country')['avg_page_timing_content_load'].sort_values(ascending=False)

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
plt.xlabel('Average Page Timing Content Load (ms)')
plt.ylabel('Country')
plt.title('Average Page Timing Content Load per Country')
plt.gca().invert_yaxis()
plt.legend(handles=handles, title="Continent")
plt.tight_layout()
plt.savefig(charts_path / f"avg_page_timing_content_load_country.png")
plt.close()

#  -----------------------------
# Durchschnitt und Anzahl pro Land (page_timing_load)
# -----------------------------
agg_country = df_request.groupby(['continent', 'country'], as_index=False).agg(
    avg_page_timing_load=('page_timing_load', 'mean'),
    count=('page_timing_load', 'count')
)
agg_country = agg_country.merge(tld_per_country, on=['continent', 'country'], how='left')

agg_country = agg_country[agg_country['count'] > 30]
country_labels = {row['country']: f"{row['country']}({row['tld']}) ({row['count']})" for _, row in agg_country.iterrows()}
data = agg_country.set_index('country')['avg_page_timing_load'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Land
# -----------------------------
plt.figure(figsize=(10, 10))
plt.barh(y=[country_labels[c] for c in data.index], width=data.values, color=colors)
plt.xlabel('Average Page Timing Load (ms)')
plt.ylabel('Country')
plt.title('Average Page Timing Load per Country')
plt.gca().invert_yaxis()
plt.legend(handles=handles, title="Continent")
plt.tight_layout()
plt.savefig(charts_path / f"avg_page_timing_load_country.png")
plt.close()

# -----------------------------
# Durchschnitt und Anzahl pro Kontinent (avg_page_timing_content_load)
# -----------------------------
agg_continent = df_request.groupby('continent', as_index=False).agg(
    avg_page_timing_content_load=('page_timing_content_load', 'mean'),
    count=('page_timing_content_load', 'count')
)


continent_labels = {row['continent']: f"{row['continent']} ({row['count']})" for _, row in agg_continent.iterrows()}
data_cont = agg_continent.set_index('continent')['avg_page_timing_content_load'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Kontinent
# -----------------------------
plt.figure(figsize=(8, 6))
plt.barh(y=[continent_labels[c] for c in data_cont.index], width=data_cont.values)
plt.xlabel('Average Page Timing Content Load  (ms)')
plt.ylabel('Continent')
plt.title('Average Page Timing Content Load  per Continent')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_page_timing_content_load_continent.png")
plt.close()


# -----------------------------
# Durchschnitt und Anzahl pro Kontinent (avg_page_timing_load)
# -----------------------------
agg_continent = df_request.groupby('continent', as_index=False).agg(
    avg_page_timing_load=('page_timing_load', 'mean'),
    count=('page_timing_load', 'count')
)

continent_labels = {row['continent']: f"{row['continent']} ({row['count']})" for _, row in agg_continent.iterrows()}
data_cont = agg_continent.set_index('continent')['avg_page_timing_load'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Kontinent
# -----------------------------
plt.figure(figsize=(8, 6))
plt.barh(y=[continent_labels[c] for c in data_cont.index], width=data_cont.values)
plt.xlabel('Average Page Timing Load  (ms)')
plt.ylabel('Continent')
plt.title('Average Page Timing Load  per Continent')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_page_timing_load_continent.png")
plt.close()