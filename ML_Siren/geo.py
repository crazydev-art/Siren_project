import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
import os

# Step 1: Load cluster data
with open('/Users/yassineoc/Desktop/DATASCIENTEST/Project_Siren_Siret_data/DataEng2024Cont_yasss/ML_Siren/cluster_circles.json', 'r') as f:
    cluster_data = json.load(f)

# Convert to DataFrame
clusters_df = pd.DataFrame(cluster_data)
# Filter out noise clusters (if needed)
clusters_df = clusters_df[clusters_df['cluster_label'] >= 0]

# Step 2: Convert to GeoDataFrame with points
geometry = [Point(lon, lat) for lon, lat in zip(clusters_df['centroid_lon'], clusters_df['centroid_lat'])]
clusters_gdf = gpd.GeoDataFrame(clusters_df, geometry=geometry, crs="EPSG:4326")

# Step 3: Download or load département boundaries (France)
geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
local_geojson = "departements.geojson"
if not os.path.exists(local_geojson):
    print("Downloading département boundaries...")
    response = requests.get(geojson_url)
    with open(local_geojson, 'wb') as f:
        f.write(response.content)

departements_gdf = gpd.read_file(local_geojson)

# Focus on Île-de-France if desired (optional filter)
idf_depts = ['75', '77', '78', '91', '92', '93', '94', '95']
departements_gdf = departements_gdf[departements_gdf['code'].isin(idf_depts)]

# Step 4: Spatial join to assign clusters to départements
joined_gdf = gpd.sjoin(clusters_gdf, departements_gdf, how="left", predicate="within")

# Step 5: Aggregate point_count by département
result = joined_gdf.groupby(['code', 'nom'])['point_count'].sum().reset_index()
result.columns = ['Dept_Code', 'Dept_Name', 'Company_Count']

# Print results
print("\nNumber of Companies per Département (Île-de-France):")
print(result.sort_values('Company_Count', ascending=False).to_string(index=False))

# Step 6: Save aggregated GeoJSON for visualization
agg_geojson = departements_gdf.merge(result, left_on='code', right_on='Dept_Code', how='left')
agg_geojson['Company_Count'] = agg_geojson['Company_Count'].fillna(0).astype(int)
agg_geojson[['code', 'nom', 'Company_Count', 'geometry']].to_file('companies_per_dept.geojson')
print("\nSaved aggregated data to 'companies_per_dept.geojson' for visualization.")
