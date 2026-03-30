import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# -----------------------------
# CSVs einlesen
# -----------------------------
request_path = Path("../../csv/har_files/packages_and_dependencies.csv.gz")
charts_path = Path("../../charts/har_files")
charts_path.mkdir(parents=True, exist_ok=True)

df_request = pd.read_csv(
    request_path, 
    compression="gzip",
    header=None,
    names=['continent', 'country', 'url', 'number_of_packages', 'number_of_dependencies']
)
df_request = df_request[df_request['continent'] != 'Unbekannt']
#  -----------------------------
# Durchschnitt und Anzahl pro Land (number_of_packages)
# -----------------------------
agg_country = df_request.groupby(['continent', 'country'], as_index=False).agg(
    avg_number_of_packages=('number_of_packages', 'mean'),
    count=('number_of_packages', 'count')
)

agg_country = agg_country[agg_country['count'] > 30]
country_labels = {row['country']: f"{row['country']} ({row['count']})" for _, row in agg_country.iterrows()}
data = agg_country.set_index('country')['avg_number_of_packages'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Land
# -----------------------------
plt.figure(figsize=(10, 10))
plt.barh(y=[country_labels[c] for c in data.index], width=data.values)
plt.xlabel('Average Number of Packages')
plt.ylabel('Country')
plt.title('Average Number of Packages per Country')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_number_of_packages_country.png")
plt.close()

#  -----------------------------
# Durchschnitt und Anzahl pro Land (number_of_dependencies)
# -----------------------------
agg_country = df_request.groupby(['continent', 'country'], as_index=False).agg(
    avg_number_of_dependencies=('number_of_dependencies', 'mean'),
    count=('number_of_dependencies', 'count')
)

agg_country = agg_country[agg_country['count'] > 30]
country_labels = {row['country']: f"{row['country']} ({row['count']})" for _, row in agg_country.iterrows()}
data = agg_country.set_index('country')['avg_number_of_dependencies'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Land
# -----------------------------
plt.figure(figsize=(10, 10))
plt.barh(y=[country_labels[c] for c in data.index], width=data.values)
plt.xlabel('Average Number of Dependencies')
plt.ylabel('Country')
plt.title('Average Number of Dependencies per Country')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_number_of_dependencies_country.png")
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
plt.xlabel('Average Number of Packages')
plt.ylabel('Continent')
plt.title('Average Number of Packages per Continent')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_number_of_packages_continent.png")
plt.close()


# -----------------------------
# Durchschnitt und Anzahl pro Kontinent (number_of_dependencies)
# -----------------------------
agg_continent = df_request.groupby('continent', as_index=False).agg(
    avg_number_of_dependencies=('number_of_dependencies', 'mean'),
    count=('number_of_dependencies', 'count')
)

continent_labels = {row['continent']: f"{row['continent']} ({row['count']})" for _, row in agg_continent.iterrows()}
data_cont = agg_continent.set_index('continent')['avg_number_of_dependencies'].sort_values(ascending=False)

# -----------------------------
# Horizontales Balkendiagramm pro Kontinent
# -----------------------------
plt.figure(figsize=(8, 6))
plt.barh(y=[continent_labels[c] for c in data_cont.index], width=data_cont.values)
plt.xlabel('Average Number of Dependencies')
plt.ylabel('Continent')
plt.title('Average Number of Dependencies per Continent')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(charts_path / f"avg_number_of_dependencies_continent.png")
plt.close()