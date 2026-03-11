# 🛰️ Global Seismic Command Center
**An End-to-End Data Engineering Pipeline | ECE Portfolio Project**

## 📖 Project Overview
This project is a high-performance data pipeline designed to monitor global seismic activity in real-time. It demonstrates a complete **ELT (Extract, Load, Transform)** workflow, moving data from a public API into a Cloud Data Warehouse and finally into a custom-built analytics dashboard.

## 🔬 Key Features
* **Automated Ingestion:** Fetches GeoJSON data from the USGS API.
* **Cloud Warehousing:** Managed storage in **Google Cloud BigQuery**.
* **Analytics Engineering:** Layered data modeling (Bronze ➔ Silver ➔ Gold) using **dbt**.
* **Command Center UI:** A pure-black, high-contrast **Streamlit** dashboard with interactive geospatial mapping.

---

## 🏗️ The Architecture
The pipeline is built on the **Modern Data Stack (MDS)** principles:

1.  **Extract & Load (Python):** `scripts/load_earthquakes.py` pulls raw data and loads it into BigQuery.
2.  **Transform (dbt):** Converts raw JSON strings into typed data, calculates risk categories, and handles spatial coordinates.
3.  **Visualize (Streamlit):** `scripts/dashboard.py` queries the production table and renders a "Command Center" view.



---

## 🛠️ Technical Stack
* **GCP BigQuery:** Enterprise data warehouse.
* **dbt (data build tool):** For modular, version-controlled SQL transformations.
* **Python 3.9:** Pipeline orchestration and visualization.
* **Plotly & Mapbox:** For high-resolution, interactive geospatial rendering.

---



## Phase 1: Ingestion & Cloud Sync
In this initial phase, the objective was to establish a reliable bridge between the external seismic data provider (USGS) and our internal cloud data warehouse (Google BigQuery).
### Objectives
1. Establish a secure connection to Google Cloud Platform (GCP).
2. Develop a Python-based Extraction script to interface with the USGS GeoJSON API.
3. Implement an automated "Load" process to populate the Bronze Layer (Raw Data) in BigQuery.

### 📋 Step-by-Step Implementation
1. **GCP Authentication:**
   * Configured service account credentials for secure API access.
   * Set up environment variables to manage authentication seamlessly.
2. **Data Extraction:**
   * Utilized the `requests` library to fetch real-time seismic data in GeoJSON format
    * Implemented error handling to manage API rate limits and connectivity issues.
3. **Data Loading:**
    * Used the `google-cloud-bigquery` library to load raw JSON data into the "Bronze" layer of BigQuery.
    * Ensured that the loading process was idempotent to prevent duplicate entries.     

### 🛠️ Technical execution:
To replicate Phase 1, ensure your virtual environment is active and run:
```bash
# Set your Google Application Credentials path
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"

# Run the ingestion script
python scripts/load_earthquakes.py
```
**Verification:**
```bash
SELECT count(*) FROM `earthquake-data-project-12345.raw_earthquake_data.usgs_raw`
```
## 🏛️ Phase 2: Data Warehouse Architecture & Schema Design
With the ingestion engine functional, Phase 2 focused on transforming the raw stream into a structured Data Warehouse environment. This stage is critical for ensuring data integrity and optimizing the warehouse for high-speed analytical queries.
### Objectives
1. Establish a multi-layered dataset architecture (Bronze/Silver/Gold).
2. Define strict schema constraints to prevent data corruption.
3. Validate geographic and temporal data types for downstream processing.

### 📋 Step-by-Step Implementation
   1. **Dataset Layering Strategy**
        To follow industry best practices, the BigQuery environment was partitioned into three distinct layers:

        * Bronze (Raw): stg_earthquakes_raw — Untouched data directly from the API.
        * Silver (Cleaned): stg_earthquakes — Data that has been cast to correct types (Float, Timestamp) but not yet aggregated.
        * Gold (Analytics): earthquake_summary — The final "Source of Truth" used by the dashboard.

    2. **Schema Hardening**
        In this phase, we moved away from "Auto-detect" schema to a Defined Schema. This ensures that if the USGS API changes its data format, our pipeline fails gracefully rather than ingesting "dirty" data.

        * The id field was designated as the unique identifier to prevent duplicate earthquake records.

  
        * The latitude and longitude fields were explicitly cast as FLOAT64 to prepare for BigQuery's ST_GEOGPOINT functions.

    3. **BigQuery Resource Allocation**
        * Dataset Location: Set to US (or a specific region like asia-south1) to minimize latency and manage data residency.

        * Access Control: Configured IAM (Identity and Access Management) to allow the dbt service account to read from Bronze and write to Silver/Gold.
### 🛠️ Technical execution:
1. **Schema Validation Query**
        To ensure Phase 2 was successful, the following "Sanity Check" SQL was executed in the BigQuery console:
        ```sql
        SELECT 
            column_name, 
            data_type 
        FROM `earthquake-data-project-12345.earthquake_analytics.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = 'stg_earthquakes';
        ```
    
2. **Data Quality Check**
        ```sql
            SELECT 
                count(*) as total_rows,
                count(id) as non_null_ids,
                count(magnitude) as valid_magnitudes
            FROM `earthquake-data-project-12345.earthquake_analytics.stg_earthquakes`;
        ```
## ⚡Phase 3: Analytics Engineering with dbt
Phase 3 is the "brain" of the pipeline. Here, we shifted from raw data storage to Analytics Engineering. Using dbt (data build tool), we turned messy JSON outputs into a structured, modeled, and high-performance analytical dataset.
### Objectives
1. Implement Version-Controlled SQL for data transformations.
2. Standardize Unix timestamps into human-readable UTC formats.
3. Develop a Seismic Severity Classification logic (Feature Engineering).
4. Cleanse geographic data for high-precision mapping.

### 📋 Step-by-Step Implementation
1. **dbt Project Initialization**
    * Project Scaffolding: Initialized the earthquake_transform directory and configured dbt_project.yml.
    * Profile Connection: Created a profiles.yml to securely connect dbt to BigQuery using the Service Account JSON key.
2. **Developing the Staging Model (stg_earthquakes.sql)**
    * Temporal Transformation: USGS provides time in milliseconds. We converted this using:
                              **TIMESTAMP_MILLIS(event_time)**
    * Feature Engineering (Severity Logic): We implemented a CASE statement to categorize earthquakes based on the Richter scale, allowing the dashboard to filter by risk level:
                Major:  >=7.0
                Strong: 5.0 - 6.9
                Minor: 3.0 - 4.9
                Micro: < 3.0
    * Coordinate Parsing: Extracted individual latitude and longitude fields to ensure compatibility with Plotly's mapping engine.
3. **Materialization Strategy** 
To optimize BigQuery costs, we configured the models to materialize as Tables rather than Views. This ensures that the heavy calculation happens once during the dbt run, and the Streamlit dashboard only has to read pre-calculated results.

### 🛠️ Technical execution:
1. Running the Transformations
To execute the models and update the BigQuery tables, run:
```bash
cd earthquake_transform
dbt run
```
2. dbt Lineage & Documentation
One of the most powerful features used was dbt's ability to generate documentation. This provides a visual map of how data flows from the raw table to the final dashboard source.
```bash
dbt docs generate
dbt docs serve
```

## 🛰️ Phase 4: High-Fidelity Visualization (The Command Center)
The final phase of the pipeline is the Presentation Layer. Moving beyond static reports, we developed a real-time, interactive Command Center using Streamlit and Plotly. This phase transforms abstract coordinates and magnitudes into a "Google Labs" style visual experience.
### Objectives
1. Develop a Single-Page Application (SPA) to host all analytical modules.
2. Implement High-Resolution Geospatial Mapping with custom dark themes.
3. Enable Dynamic Filtering to allow end-users to drill down into seismic data by intensity.
4. Optimize Dashboard Performance using Streamlit Caching.

### 📋 Step-by-Step Implementation
1. **UI/UX Design & Theming**
To achieve a professional "Engineering" aesthetic, the dashboard was built with a Pure Black (#000000) background.

 * Custom CSS Injection: Utilized st.markdown with unsafe_allow_html=True to override Streamlit’s default grey theme.

 * Neon Accents: Categorical colors were mapped to high-contrast neon hex codes (e.g., #39FF14 for Micro, #FF3131 for Major) for maximum readability against the dark map.

2. **Geospatial Engineering**
The map is the "Hero Component" of Phase 4.

 * Engine: Utilized plotly.express.scatter_map for modern, GPU-accelerated rendering.

 * Map Style: Integrated carto-darkmatter, a minimalist dark map that highlights data points without visual clutter.

 * Spatial Logic: Bubbles are dynamically sized based on the Richter Scale (Magnitude) and colored based on the dbt Classification from Phase 3.

3. **Integrated Analytics Modules**
The dashboard was partitioned into three functional zones:

 * Metric Scorecards: Real-time counts of active events and peak intensities.

 * Temporal Trend Analysis: A Plotly Line Chart tracking the frequency of earthquakes over the last 30 days to identify seismic "swarms."

 * Risk Distribution: A Donut Chart visualizing the ratio of minor vs. major events.

## 💻 Technical Execution
1. **Running the Dashboard**
To launch the final product, ensure your GCP credentials are set and run:
```bash
streamlit run scripts/dashboard.py
```
2. **Key Logic: The Sidebar Filter**
A core feature of Phase 4 is the reactive sidebar. Moving the slider triggers an immediate re-query and re-render of the entire dashboard:
```python
min_mag = st.sidebar.slider("Magnitude Threshold", 1.0, 10.0)
df_filtered = df[df['magnitude'] >= min_mag]
```

