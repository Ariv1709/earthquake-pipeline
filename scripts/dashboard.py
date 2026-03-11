import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Seismic Command Center",
    page_icon="🌋",
    layout="wide", 
)

# --- UPDATED CSS FOR WHITE TEXT & BLACK BG ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #000000;
    }
    
    /* Force all text to White */
    h1, h2, h3, p, span, label {
        color: #FFFFFF !important;
    }

    /* Target Metrics specifically */
    [data-testid="stMetricValue"] {
        color: #00d4ff !important; /* Keeping the neon blue for the numbers */
        font-family: 'Courier New', Courier, monospace;
    }
    [data-testid="stMetricLabel"] {
        color: #FFFFFF !important; /* Metric labels now white */
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Sidebar text and background */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #FFFFFF !important;
    }
    
    /* Divider lines */
    hr {
        border-color: #444444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. DATA FETCHING (Cached)
@st.cache_data
def get_data():
    client = bigquery.Client()
    PROJECT_ID = "earthquake-data-project-12345" # Ensure this is your ID
    QUERY = f"SELECT * FROM `{PROJECT_ID}.earthquake_analytics.stg_earthquakes` WHERE magnitude IS NOT NULL"
    df = client.query(QUERY).to_dataframe()
    df['event_time'] = pd.to_datetime(df['event_time'])
    return df

try:
    df = get_data()
except Exception as e:
    st.error(f"BigQuery Connection Error: {e}")
    st.stop()

# 3. SIDEBAR CONTROLS
st.sidebar.title("⚡ SYS CONTROL")
st.sidebar.markdown("---")
min_mag = st.sidebar.slider("Mag Threshold", float(df['magnitude'].min()), float(df['magnitude'].max()), 1.5)
df_filtered = df[df['magnitude'] >= min_mag].copy()

# 4. MAIN DASHBOARD HEADER
st.title("🛰️ GLOBAL SEISMIC MONITOR")
st.markdown("<p style='color: #FFFFFF;'>REAL-TIME ANALYTICS ENGINE </p>", unsafe_allow_html=True)

# --- ROW 1: SCORECARDS ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("EVENT_COUNT", len(df_filtered))
m2.metric("MEAN_MAG", f"{df_filtered['magnitude'].mean():.2f}")
m3.metric("PEAK_INTENSITY", f"{df_filtered['magnitude'].max():.1f}")
m4.metric("LOC_UNITS", df_filtered['place'].nunique())

st.markdown("---")

# --- ROW 2: FULL WIDTH MAP ---
st.subheader("GEOSPATIAL THERMAL VIEW")

fig_map = px.scatter_map(
    df_filtered,
    lat="latitude",
    lon="longitude",
    color="magnitude_category",
    size="magnitude",
    hover_name="place",
    color_discrete_map={
        "Major": "#FF0000",   
        "Strong": "#FF5E00",  
        "Minor": "#FFD700",   
        "Micro": "#00FF00"    
    },
    zoom=1.5,
    height=650 
)

fig_map.update_layout(
    map_style="carto-darkmatter", 
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font_color="#ffffff", # Set Plotly text to white
    legend=dict(yanchor="top", y=0.95, xanchor="left", x=0.01, bgcolor="rgba(0,0,0,0.8)", font=dict(color="white"))
)
st.plotly_chart(fig_map, use_container_width=True)

# --- ROW 3: ANALYTICS SPLIT ---
st.markdown("---")
b_left, b_right = st.columns([1, 1])

with b_left:
    st.subheader("TEMPORAL FREQUENCY")
    df_filtered['date'] = df_filtered['event_time'].dt.date
    df_daily = df_filtered.groupby('date').size().reset_index(name='count')
    fig_line = px.line(df_daily, x='date', y='count', markers=True, template="plotly_dark")
    fig_line.update_traces(line_color='#00d4ff', line_width=2)
    fig_line.update_layout(
        paper_bgcolor="#000000", 
        plot_bgcolor="#000000",
        font_color="#ffffff"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with b_right:
    st.subheader("RISC DISTRIBUTION")
    fig_pie = px.pie(
        df_filtered, names='magnitude_category', hole=0.6,
        color='magnitude_category',
        color_discrete_map={"Major": "#FF0000", "Strong": "#FF5E00", "Minor": "#FFD700", "Micro": "#00FF00"},
        template="plotly_dark"
    )
    fig_pie.update_layout(
        paper_bgcolor="#000000", 
        plot_bgcolor="#000000",
        font_color="#ffffff"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #FFFFFF; font-size: 12px;'>SYSTEM STATUS: ONLINE | DATABASE: BIGQUERY</p>", unsafe_allow_html=True)