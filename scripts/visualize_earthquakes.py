import pandas as pd
import plotly.express as px
from google.cloud import bigquery
import os

# 1. Setup BigQuery Client
# Ensure your .env or gcloud auth is active
client = bigquery.Client()

# 2. Query the CLEAN dbt table
# Replace with your actual Project ID
PROJECT_ID = "earthquake-data-project-12345" 
QUERY = f"""
    SELECT 
        latitude, 
        longitude, 
        magnitude, 
        magnitude_category, 
        place,
        event_time
    FROM `{PROJECT_ID}.earthquake_analytics.stg_earthquakes`
    WHERE magnitude IS NOT NULL
"""

print("Fetching data from BigQuery...")
df = client.query(QUERY).to_dataframe()

# 3. Create the Interactive Map
print("Generating map...")

# FILTER out negative magnitudes so Plotly doesn't crash
df_positive = df[df['magnitude'] > 0].copy()

fig = px.scatter_map(  # Updated from scatter_mapbox to scatter_map
    df_positive, 
    lat="latitude", 
    lon="longitude", 
    color="magnitude_category", 
    size="magnitude",            
    hover_name="place",          
    hover_data=["magnitude", "event_time"],
    color_discrete_map={         
        "Major": "red", 
        "Strong": "orange", 
        "Minor": "yellow", 
        "Micro": "green"
    },
    zoom=1, 
    height=800,
    title="Phase 4: Global Seismic Activity Analysis"
)

# Use a standard map style that doesn't require a Mapbox token
fig.update_layout(map_style="open-street-map")

# 4. Show the result
fig.show()

# 5. Create a Time-Series Chart (Earthquakes per Day)
# Convert event_time to just the date for grouping
df_positive['date'] = pd.to_datetime(df_positive['event_time']).dt.date
df_daily = df_positive.groupby('date').size().reset_index(name='count')

fig_line = px.line(
    df_daily, 
    x='date', 
    y='count',
    title="Daily Earthquake Frequency (Last 30 Days)",
    labels={'count': 'Number of Events', 'date': 'Date'},
    markers=True
)

fig_line.update_traces(line_color='#1f77b4')
fig_line.show()

# 6. Export as high-quality HTML files
fig.write_html("earthquake_map.html")
fig_line.write_html("earthquake_trends.html")
print("Phase 4 Complete: Interactive files saved as 'earthquake_map.html' and 'earthquake_trends.html'")