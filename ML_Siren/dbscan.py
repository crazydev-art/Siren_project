import pandas as pd
import json
import numpy as np

# Load your DBSCAN results CSV (adjust path if needed)
csv_path = "/Users/yassineoc/Desktop/DATASCIENTEST/Project_Siren_Siret_data/DataEng2024Cont_yasss/ML_Siren/dbscan_results_batch_0.csv"
df = pd.read_csv(csv_path)

# Filter to Île-de-France region (optional, adjust or remove as needed)
min_lat, max_lat = 48.1, 49.2
min_lon, max_lon = 1.5, 3.5
idf_df = df[
    (df['y_latitude'].between(min_lat, max_lat)) &
    (df['x_longitude'].between(min_lon, max_lon))
]

# Limit to a manageable size if needed (optional)
#idf_df = idf_df.head(50000)

# Group by cluster_label to calculate centroid and rough radius
clusters = idf_df.groupby('cluster_label').agg({
    'y_latitude': ['mean', 'std', 'count'],
    'x_longitude': ['mean', 'std']
}).reset_index()

# Format for JSON
cluster_data = []
for _, row in clusters.iterrows():
    cluster_label = row['cluster_label'].iloc[0] if isinstance(row['cluster_label'], pd.Series) else row['cluster_label']
    centroid_lat = row['y_latitude']['mean']
    centroid_lon = row['x_longitude']['mean']
    # Estimate radius (in meters, rough approximation using std; adjust as needed)
    lat_std = row['y_latitude']['std'] if not np.isnan(row['y_latitude']['std']) else 0.01
    lon_std = row['x_longitude']['std'] if not np.isnan(row['x_longitude']['std']) else 0.01
    radius = max(lat_std, lon_std) * 111320  # Convert degrees to meters (approx)
    if radius < 1000:  # Minimum radius for visibility
        radius = 1000
    count = row['y_latitude']['count']
    cluster_data.append({
        'cluster_label': int(cluster_label),
        'centroid_lat': centroid_lat,
        'centroid_lon': centroid_lon,
        'radius': radius,
        'point_count': int(count)
    })

# Save to JSON in the current directory
output_path = "cluster_circles.json"
with open(output_path, 'w') as f:
    json.dump(cluster_data, f, indent=2)
print(f"Saved {len(cluster_data)} clusters to {output_path}")
