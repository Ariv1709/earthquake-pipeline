import requests
import os
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

def fetch_and_load():
    # 1. Fetch data from USGS
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
    print("Fetching data from USGS...")
    response = requests.get(url)
    response.raise_for_status()
    data = response.json().get("features", [])

    # 2. Transform into a simple list of dicts for BigQuery
    rows_to_insert = []
    for event in data:
        rows_to_insert.append({
            "id": event["id"],
            "mag": event["properties"]["mag"],
            "place": event["properties"]["place"],
            "time": event["properties"]["time"],
            "updated": event["properties"]["updated"],
            "tz": event["properties"]["tz"],
            "url": event["properties"]["url"],
            "detail": event["properties"]["detail"],
            "felt": event["properties"]["felt"],
            "cdi": event["properties"]["cdi"],
            "mmi": event["properties"]["mmi"],
            "alert": event["properties"]["alert"],
            "status": event["properties"]["status"],
            "tsunami": event["properties"]["tsunami"],
            "sig": event["properties"]["sig"],
            "net": event["properties"]["net"],
            "code": event["properties"]["code"],
            "ids": event["properties"]["ids"],
            "sources": event["properties"]["sources"],
            "types": event["properties"]["types"],
            "nst": event["properties"]["nst"],
            "dmin": event["properties"]["dmin"],
            "rms": event["properties"]["rms"],
            "gap": event["properties"]["gap"],
            "magType": event["properties"]["magType"],
            "type": event["properties"]["type"],
            "longitude": event["geometry"]["coordinates"][0],
            "latitude": event["geometry"]["coordinates"][1],
            "depth": event["geometry"]["coordinates"][2]
        })

    # 3. Setup BigQuery Client
    client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID"))
    table_id = f"{os.getenv('GCP_PROJECT_ID')}.{os.getenv('DATASET_NAME')}.earthquakes"

    # 4. Configure the Load Job (This is the 'Free Tier' safe way)
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition="WRITE_TRUNCATE", # Replaces the table each time
    )

    print(f"Loading {len(rows_to_insert)} rows into {table_id}...")
    job = client.load_table_from_json(rows_to_insert, table_id, job_config=job_config)
    
    job.result()  # Wait for the job to complete
    print("Job finished successfully!")

if __name__ == "__main__":
    fetch_and_load()