import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from pathlib import Path
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Peta Risiko DBD Garut",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme colors - Professional Light Theme
THEME = {
    "bg": "#f8f9fa",
    "sidebar_bg": "#1e2530",
    "card_bg": "#ffffff",
    "text": "#2c3e50",
    "text_muted": "#6c757d",
    "text_very_muted": "#adb5bd",
    "border": "#e9ecef",
    "accent": "#2c3e50",
    "map_tiles": "CartoDB positron"
}

# Cluster colors - Professional muted tones
CLUSTER_COLORS = {
    0: "#28a745",  # Green - Rendah
    1: "#ffc107",  # Yellow/Amber - Sedang  
    2: "#dc3545"   # Red - Tinggi
}

# Custom CSS - PROFESSIONAL LIGHT THEME
st.markdown(f"""
<style>
    /* ===== GLOBAL ===== */
    .stApp {{
        background-color: {THEME["bg"]};
        overflow: hidden;
    }}
    .main {{
        overflow: hidden !important;
    }}
    .main .block-container {{
        padding: 0.5rem 1rem 0.3rem 1rem !important;
        max-width: 100% !important;
        height: calc(100vh - 1rem);
        overflow: hidden !important;
    }}
    
    /* Remove iframe border */
    iframe {{
        border: none !important;
    }}
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {{
        background: {THEME["sidebar_bg"]};
        color: white;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 0.5rem;
    }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        gap: 0.5rem !important;
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h5 {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    
    /* NAV BUTTONS */
    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        background: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 14px;
        font-weight: 600;
        text-align: left;
        transition: all 0.2s ease;
        margin-bottom: 2px;
    }}
    [data-testid="stSidebar"] .stButton > button span {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(255,255,255,0.15) !important;
        border-color: rgba(255,255,255,0.25) !important;
    }}
    [data-testid="stSidebar"] .stButton > button[kind="primary"],
    [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {{
        background: #3498db !important;
        border-color: #3498db !important;
    }}
    
    /* Sidebar selectbox fix */
    [data-testid="stSidebar"] .stSelectbox label {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        background: rgba(255,255,255,0.1) !important;
        border-color: rgba(255,255,255,0.2) !important;
        color: #ffffff !important;
        cursor: pointer !important;
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div > div {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] span {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] input {{
        caret-color: transparent !important;
        cursor: pointer !important;
    }}
    /* Show dropdown arrow */
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        display: block !important;
        visibility: visible !important;
        fill: #ffffff !important;
        opacity: 1 !important;
    }}
    
    /* ===== HEADER - override stMarkdown inside main-header ===== */
    .main-header {{
        background: {THEME["sidebar_bg"]};
        padding: 20px 28px;
        border-radius: 10px;
        color: #ffffff;
        margin-bottom: 24px;
    }}
    .main-header h1 {{
        color: #ffffff !important;
        margin: 0 0 6px 0;
        font-size: 1.5em;
        font-weight: 600;
    }}
    .main-header p {{
        color: #e0e0e0 !important;
        margin: 0;
        font-size: 0.9em;
    }}
    .stMarkdown .main-header h1 {{
        color: #ffffff !important;
    }}
    .stMarkdown .main-header p {{
        color: #e0e0e0 !important;
    }}
    
    /* ===== METRIC CARDS ===== */
    .metric-card {{
        background: {THEME["card_bg"]};
        border-radius: 8px;
        padding: 16px 20px;
        border: none;
        border-left: 4px solid {THEME["accent"]};
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }}
    .metric-card h3 {{
        margin: 0 0 6px 0;
        font-size: 0.75em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: {THEME["text_muted"]} !important;
        font-weight: 600;
    }}
    .metric-card .value {{
        font-size: 2.4em;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
        color: {THEME["text"]} !important;
    }}
    .metric-card .sub {{
        font-size: 0.8em;
        color: {THEME["text_muted"]} !important;
        margin-top: 4px;
    }}
    
    /* ===== CLUSTER CARDS ===== */
    .cluster-card {{
        background: {THEME["card_bg"]};
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
        border: none;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }}
    .cluster-card .stat-val {{
        font-weight: 700;
        font-size: 1.4em;
        color: {THEME["text"]} !important;
    }}
    .cluster-card .stat-label {{
        color: {THEME["text_muted"]} !important;
        font-size: 0.85em;
    }}
    
    /* Cluster badges */
    .cluster-badge {{
        display: inline-block;
        padding: 5px 14px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78em;
        color: white;
    }}
    .cluster-0 {{ background: {CLUSTER_COLORS[0]}; }}
    .cluster-1 {{ background: {CLUSTER_COLORS[1]}; color: #212529 !important; }}
    .cluster-2 {{ background: {CLUSTER_COLORS[2]}; }}
    
    /* ===== SECTION TITLE ===== */
    .section-title {{
        font-size: 2em;
        font-weight: 600;
        color: {THEME["text"]} !important;
        margin: 0 0 16px 0;
        padding: 0;
    }}
    [data-testid="stMain"] .stMarkdown p.section-title {{
        font-size: 1.5em !important;
        font-weight: 600 !important;
        margin: 0 0 16px 0 !important;
    }}
    
    /* ===== DIVIDER ===== */
    .custom-divider {{
        height: 1px;
        background: rgba(255,255,255,0.15);
        border: none;
        margin: 5px 0 20px 0;
    }}
    
    /* ===== FOOTER ===== */
    .footer {{
        text-align: center;
        padding: 16px;
        color: {THEME["text_muted"]};
        font-size: 0.8em;
        border-top: 1px solid {THEME["border"]};
        margin-top: 20px;
    }}
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{ 
        gap: 8px; 
        background: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{ 
        padding: 10px 20px; 
        font-size: 0.9em;
        background: {THEME["card_bg"]};
        border: 1px solid {THEME["border"]};
        border-radius: 6px 6px 0 0;
        color: {THEME["text"]} !important;
    }}
    .stTabs [data-baseweb="tab"] span {{
        color: {THEME["text"]} !important;
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        border-bottom: 2px solid {THEME["accent"]};
    }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] span {{
        color: {THEME["accent"]} !important;
        font-weight: 600;
    }}
    
    /* ===== MAIN CONTENT TEXT ===== */
    [data-testid="stMain"] .stMarkdown p,
    [data-testid="stMain"] .stMarkdown h1,
    [data-testid="stMain"] .stMarkdown h2,
    [data-testid="stMain"] .stMarkdown h3,
    [data-testid="stMain"] .stMarkdown h4,
    [data-testid="stMain"] .stMarkdown li,
    [data-testid="stMain"] .stMarkdown strong {{
        color: {THEME["text"]} !important;
    }}
    
    /* Force header whites (higher specificity) */
    [data-testid="stMain"] .stMarkdown .main-header h1,
    [data-testid="stMain"] .stMarkdown .main-header p,
    [data-testid="stMain"] .stMarkdown .main-header span {{
        color: #ffffff !important;
    }}
    [data-testid="stMain"] .stMarkdown .main-header p {{
        color: #e0e0e0 !important;
    }}
    
    /* FAQ footer styling */
    [data-testid="stMain"] .stMarkdown .faq-footer h3,
    [data-testid="stMain"] .stMarkdown .faq-footer p {{
        color: #ffffff !important;
    }}
    [data-testid="stMain"] .stMarkdown .faq-footer p {{
        opacity: 0.85;
    }}
    
    /* ===== DATAFRAME / TABLE - Light theme ===== */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] div,
    [data-testid="stDataFrame"] span,
    .stDataFrame {{
        background-color: {THEME["card_bg"]} !important;
        color: {THEME["text"]} !important;
    }}
    
    /* Force dataframe cell text visibility */
    [data-testid="stDataFrame"] [data-testid="stDataFrameResizable"],
    [data-testid="stDataFrame"] .dvn-scroller,
    [data-testid="stDataFrame"] table,
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] td,
    [data-testid="stDataFrame"] [role="gridcell"],
    [data-testid="stDataFrame"] [role="columnheader"] {{
        background-color: {THEME["card_bg"]} !important;
        color: {THEME["text"]} !important;
    }}
    
    /* Glide data grid styling for dataframe */
    .dvn-scroller {{
        background-color: {THEME["card_bg"]} !important;
    }}
    [data-testid="stDataFrame"] canvas {{
        background-color: {THEME["card_bg"]} !important;
    }}
    
    /* Main content download button fix */
    [data-testid="stMain"] .stDownloadButton {{
        margin-top: 16px !important;
    }}
    [data-testid="stMain"] .stDownloadButton > button {{
        background: {THEME["accent"]} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }}
    [data-testid="stMain"] .stDownloadButton > button:hover {{
        background: #3a5068 !important;
    }}
    [data-testid="stMain"] .stDownloadButton > button span {{
        color: #ffffff !important;
    }}
    [data-testid="stMain"] .stDownloadButton > button svg {{
        fill: #ffffff !important;
    }}
    
    /* Selectbox & multiselect in main content */
    [data-testid="stMain"] .stSelectbox > div > div,
    [data-testid="stMain"] .stMultiSelect > div > div {{
        background: {THEME["card_bg"]} !important;
        color: {THEME["text"]} !important;
        border-color: {THEME["border"]} !important;
        cursor: pointer !important;
    }}
    [data-testid="stMain"] .stSelectbox label,
    [data-testid="stMain"] .stMultiSelect label {{
        color: {THEME["text"]} !important;
    }}
    [data-testid="stMain"] [data-baseweb="select"] span,
    [data-testid="stMain"] [data-baseweb="tag"] span {{
        color: {THEME["text"]} !important;
    }}
    [data-testid="stMain"] [data-baseweb="select"] input {{
        caret-color: transparent !important;
        cursor: pointer !important;
    }}
    
    /* Multiselect tag styling - default */
    [data-testid="stMain"] [data-baseweb="tag"] {{
        border-radius: 6px !important;
        padding: 2px 8px !important;
        margin: 2px !important;
        height: 28px !important;
    }}
    [data-testid="stMain"] [data-baseweb="tag"] span {{
        color: #ffffff !important;
        font-size: 12px !important;
    }}
    
    /* Cluster 0 - Rendah (Hijau) */
    [data-testid="stMain"] .stMultiSelect [data-baseweb="tag"]:nth-child(1) {{
        background-color: #28a745 !important;
    }}
    /* Cluster 1 - Sedang (Kuning) */
    [data-testid="stMain"] .stMultiSelect [data-baseweb="tag"]:nth-child(2) {{
        background-color: #ffc107 !important;
    }}
    [data-testid="stMain"] .stMultiSelect [data-baseweb="tag"]:nth-child(2) span {{
        color: #2c3e50 !important;
    }}
    /* Cluster 2 - Tinggi (Merah) */
    [data-testid="stMain"] .stMultiSelect [data-baseweb="tag"]:nth-child(3) {{
        background-color: #dc3545 !important;
    }}
    
    /* Match multiselect and selectbox height & border */
    [data-testid="stMain"] .stSelectbox [data-baseweb="select"] > div,
    [data-testid="stMain"] .stMultiSelect [data-baseweb="select"] > div {{
        min-height: 44px !important;
        border-radius: 8px !important;
        border: 1px solid {THEME["border"]} !important;
        padding: 4px 12px !important;
        display: flex !important;
        align-items: center !important;
    }}
    
    /* Selectbox text tidak kepotong */
    [data-testid="stMain"] .stSelectbox [data-baseweb="select"] > div > div {{
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: nowrap !important;
    }}
    
    /* Align columns vertically */
    [data-testid="stHorizontalBlock"] {{
        gap: 20px !important;
        align-items: flex-end !important;
    }}
    
    /* Sidebar section titles */
    [data-testid="stSidebar"] h5 {{
        font-size: 0.75em !important;
        margin-bottom: 6px !important;
        margin-top: 0 !important;
        color: #e0e0e0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Sidebar horizontal rule */
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.2) !important;
        margin: 8px 0 !important;
    }}
</style>
""", unsafe_allow_html=True)

# Define paths
project_root = Path(__file__).resolve().parents[2]
shapefile_path = project_root / "GARUT" / "KECAMATANGARUT.shp"
csv_path = project_root / "processed_data" / "merge_data_clustered.csv"

# Load data
@st.cache_data
def load_data():
    gdf = gpd.read_file(shapefile_path)
    df = pd.read_csv(csv_path)
    return gdf, df

gdf, df = load_data()

# ===================== SIDEBAR NAVIGATION =====================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding-bottom: 32px;'>
        <span style='font-size: 2.2em; display: block; margin-bottom: 16px;'>🦟</span>
        <h2 style='color: #ffffff !important; font-size: 1.3em; font-weight: 600; line-height: 1.2; margin: 0;'>Dashboard Peta Risiko DBD</h2>
        <h3 style='color: #b0b8c1 !important; font-size: 1.2em; font-weight: 400; line-height: 1.2; margin: 0;'>Kabupaten Garut</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    if st.button("🏠  Home", key="nav_home", width="stretch",
                  type="primary" if st.session_state.page == "home" else "secondary"):
        st.session_state.page = "home"
        st.rerun()
    
    if st.button("📊  Lihat Data", key="nav_data", width="stretch",
                  type="primary" if st.session_state.page == "data" else "secondary"):
        st.session_state.page = "data"
        st.rerun()
    
    if st.button("❓  FAQ", key="nav_faq", width="stretch",
                  type="primary" if st.session_state.page == "faq" else "secondary"):
        st.session_state.page = "faq"
        st.rerun()
    
    if st.session_state.page in ["home", "data"]:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("##### 📅 Filter Tahun")
        years = sorted(df['year'].unique())
        selected_year = st.selectbox("Pilih Tahun:", years, key="year_filter", label_visibility="collapsed")
    else:
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        years = sorted(df['year'].unique())
        selected_year = years[-1]

# Filter data
df_filtered = df[df['year'] == selected_year].copy()

# Find kecamatan column
kecamatan_col = None
for col in gdf.columns:
    if 'WADMKC' in col.upper():
        kecamatan_col = col
        break
if kecamatan_col is None:
    kecamatan_col = gdf.columns[0]

# ===================== HOME PAGE =====================
if st.session_state.page == "home":    
    # Metrics row
    total_kasus = df_filtered['jumlah_kasus'].sum()
    avg_ir = df_filtered['ir'].mean()
    total_kecamatan = df_filtered['kecamatan'].nunique()
    num_clusters = df_filtered['cluster'].nunique()
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #e74c3c;">
            <h3>Total Kasus</h3>
            <p class="value">{int(total_kasus):,}</p>
            <p class="sub">Tahun {selected_year}</p>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #3498db;">
            <h3>Rata-rata Incidence Rate</h3>
            <p class="value">{avg_ir:.2f}</p>
            <p class="sub">Incidence Rate</p>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #2ecc71;">
            <h3>Kecamatan</h3>
            <p class="value">{total_kecamatan}</p>
            <p class="sub">Terdata</p>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #9b59b6;">
            <h3>Cluster</h3>
            <p class="value">{num_clusters}</p>
            <p class="sub">Kelompok Risiko</p>
        </div>""", unsafe_allow_html=True)
    
    # Map + Stats
    col_map, col_stats = st.columns([3, 1])
    
    with col_map:
        st.markdown(f'<p class="section-title">🗺️ Peta Clustering Tahun {selected_year}</p>', unsafe_allow_html=True)
        
        gdf_copy = gdf.copy()
        gdf_copy['kecamatan_merge'] = gdf_copy[kecamatan_col].astype(str).str.upper().str.strip()
        df_filtered_map = df_filtered.copy()
        df_filtered_map['kecamatan_merge'] = df_filtered_map['kecamatan'].astype(str).str.upper().str.strip()
        gdf_merged = gdf_copy.merge(df_filtered_map, on='kecamatan_merge', how='left')
        gdf_merged = gdf_merged.to_crs(epsg=4326)
        
        def get_cluster_color(cluster):
            return '#95a5a6' if pd.isna(cluster) else CLUSTER_COLORS.get(int(cluster), '#95a5a6')
        
        bounds = gdf_merged.total_bounds
        center = [(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2]
        m = folium.Map(location=center, zoom_start=9, tiles=THEME["map_tiles"], attr=' ')
        
        for idx, row in gdf_merged.iterrows():
            cluster = row.get('cluster', -1)
            color = get_cluster_color(cluster)
            
            # Get all data
            ir_val = row.get('ir')
            ir_disp = f"{ir_val:.2f}" if pd.notna(ir_val) else 'N/A'
            cl_disp = int(cluster) if pd.notna(cluster) else 'N/A'
            kasus_disp = int(row['jumlah_kasus']) if pd.notna(row.get('jumlah_kasus')) else 'N/A'
            penduduk_disp = f"{int(row['jumlah_penduduk']):,}" if pd.notna(row.get('jumlah_penduduk')) else 'N/A'
            
            # Additional variables
            curah_hujan = row.get('curah_hujan')
            curah_hujan_disp = f"{curah_hujan:.1f} mm" if pd.notna(curah_hujan) else 'N/A'
            kelembapan = row.get('kelembapan')
            kelembapan_disp = f"{kelembapan:.1f}%" if pd.notna(kelembapan) else 'N/A'
            temperature = row.get('temperature')
            temperature_disp = f"{temperature:.1f}°C" if pd.notna(temperature) else 'N/A'
            kepadatan = row.get('kepadatan_penduduk')
            kepadatan_disp = f"{int(kepadatan):,}/km²" if pd.notna(kepadatan) else 'N/A'
            
            cl_map = {0: "Rendah", 1: "Sedang", 2: "Tinggi"}
            cl_label = cl_map.get(cl_disp, "N/A")
            
            # Professional popup
            popup = f"""
            <style>
                .leaflet-popup-content-wrapper {{
                    padding: 0 !important;
                    border-radius: 8px !important;
                    overflow: hidden;
                }}
                .leaflet-popup-content {{
                    margin: 0 !important;
                    width: auto !important;
                }}
                .leaflet-popup-close-button {{
                    display: none !important;
                }}
            </style>
            <div style="font-family:'Segoe UI',sans-serif;min-width:280px;background:#fff;color:#2c3e50;padding:0;border-radius:8px;overflow:hidden;">
                <div style="background:{color};padding:14px 18px;color:white;position:relative;">
                    <a href="#" onclick="this.closest('.leaflet-popup').remove(); return false;" style="position:absolute;right:12px;top:50%;transform:translateY(-50%);color:white;font-size:18px;text-decoration:none;opacity:0.8;">✕</a>
                    <h4 style="margin:0;font-size:15px;font-weight:600;">📍 {row[kecamatan_col]}</h4>
                    <span style="font-size:12px;opacity:0.9;">Cluster: {cl_label}</span>
                </div>
                <div style="padding:16px 18px;">
                    <table style="width:100%;font-size:13px;color:#495057;border-collapse:collapse;">
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">🦠 Jumlah Kasus</td>
                            <td style="text-align:right;padding:10px 0;font-weight:600;">{kasus_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">📊 Incidence Rate</td>
                            <td style="text-align:right;padding:10px 0;font-weight:600;">{ir_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">👥 Jumlah Penduduk</td>
                            <td style="text-align:right;padding:10px 0;">{penduduk_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">🏘️ Kepadatan Penduduk</td>
                            <td style="text-align:right;padding:10px 0;">{kepadatan_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">🌧️ Curah Hujan</td>
                            <td style="text-align:right;padding:10px 0;">{curah_hujan_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">💧 Kelembapan</td>
                            <td style="text-align:right;padding:10px 0;">{kelembapan_disp}</td>
                        </tr>
                        <tr>
                            <td style="padding:10px 0;">🌡️ Suhu Rata-rata</td>
                            <td style="text-align:right;padding:10px 0;">{temperature_disp}</td>
                        </tr>
                    </table>
                </div>
            </div>
            """
            
            def style_fn(feature, fc=color):
                return {'fillColor': fc, 'color': '#495057', 'weight': 1, 'fillOpacity': 0.7}
            def highlight_fn(feature):
                return {'weight': 2, 'color': '#2c3e50', 'fillOpacity': 0.85}
            
            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=style_fn,
                highlight_function=highlight_fn,
                popup=folium.Popup(popup, max_width=320),
                tooltip=row[kecamatan_col]
            ).add_to(m)
        
        # Legend
        legend_html = f"""
        <div style="position:fixed;bottom:20px;left:20px;z-index:1000;
             background:white;padding:14px 18px;border-radius:8px;
             box-shadow:0 2px 8px rgba(0,0,0,0.12);font-size:12px;color:#2c3e50;border:1px solid #e9ecef;">
            <b style="font-size:12px;color:#495057;">Keterangan</b>
            <div style="margin-top:10px;"><span style="background:{CLUSTER_COLORS[0]};width:14px;height:14px;display:inline-block;border-radius:3px;vertical-align:middle;"></span><span style="margin-left:10px;vertical-align:middle;">Rendah</span></div>
            <div style="margin-top:6px;"><span style="background:{CLUSTER_COLORS[1]};width:14px;height:14px;display:inline-block;border-radius:3px;vertical-align:middle;"></span><span style="margin-left:10px;vertical-align:middle;">Sedang</span></div>
            <div style="margin-top:6px;"><span style="background:{CLUSTER_COLORS[2]};width:14px;height:14px;display:inline-block;border-radius:3px;vertical-align:middle;"></span><span style="margin-left:10px;vertical-align:middle;">Tinggi</span></div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Hide Leaflet attribution
        hide_attr_css = """
        <style>
            .leaflet-control-attribution {
                display: none !important;
            }
        </style>
        """
        m.get_root().html.add_child(folium.Element(hide_attr_css))
        
        st_folium(m, height=580, width="stretch")
    
    with col_stats:
        st.markdown('<p class="section-title">📈 Ringkasan Cluster</p>', unsafe_allow_html=True)
        
        for cid in sorted(df_filtered['cluster'].dropna().unique()):
            cdata = df_filtered[df_filtered['cluster'] == cid]
            names = {0: "Rendah", 1: "Sedang", 2: "Tinggi"}
            css = {0: "cluster-0", 1: "cluster-1", 2: "cluster-2"}
            
            st.markdown(f"""
            <div class="cluster-card">
                <span class="cluster-badge {css.get(int(cid),'cluster-0')}">C{int(cid)} - {names.get(int(cid),'?')}</span>
                <div style="display:flex;justify-content:space-between;margin-top:12px;">
                    <div style="text-align:center;flex:1;"><div class="stat-val">{len(cdata)}</div><div class="stat-label">Kecamatan</div></div>
                    <div style="text-align:center;flex:1;"><div class="stat-val">{int(cdata['jumlah_kasus'].sum())}</div><div class="stat-label">Kasus</div></div>
                    <div style="text-align:center;flex:1;"><div class="stat-val">{cdata['ir'].mean():.1f}</div><div class="stat-label">Avg IR</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Distribusi
        st.markdown('<p class="section-title" style="margin-top:16px;">📊 Distribusi</p>', unsafe_allow_html=True)
        for cid in sorted(df_filtered['cluster'].dropna().unique()):
            cdata = df_filtered[df_filtered['cluster'] == cid]
            pct = len(cdata) / len(df_filtered) * 100
            names = {0: "Rendah", 1: "Sedang", 2: "Tinggi"}
            st.markdown(f"""
            <div style="display:flex;align-items:center;margin-bottom:8px;">
                <span style="background:{CLUSTER_COLORS[int(cid)]};width:14px;height:14px;border-radius:3px;margin-right:10px;"></span>
                <span style="flex:1;color:{THEME["text_muted"]};font-size:0.9em;">{names.get(int(cid))}</span>
                <span style="color:{THEME["text"]};font-weight:600;font-size:0.95em;">{len(cdata)} ({pct:.0f}%)</span>
            </div>
            """, unsafe_allow_html=True)
    



# ===================== DATA PAGE =====================
elif st.session_state.page == "data":
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 Lihat Data</h1>
        <p>Eksplorasi data DBD Kabupaten Garut tahun {selected_year}</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Tabel Data", "📈 Grafik Analisis", "🔍 Perbandingan Tahunan"])
    
    with tab1:
        fc1, fc2 = st.columns(2)
        with fc1:
            cluster_filter = st.multiselect(
                "Filter Cluster:",
                options=sorted(df_filtered['cluster'].dropna().unique()),
                default=sorted(df_filtered['cluster'].dropna().unique()),
                format_func=lambda x: f"Cluster {int(x)} - {['Rendah','Sedang','Tinggi'][int(x)]}"
            )
        with fc2:
            sort_options = {
                'kecamatan': 'Kecamatan',
                'ir': 'Incidence Rate',
                'jumlah_kasus': 'Jumlah Kasus',
                'jumlah_penduduk': 'Jumlah Penduduk',
                'kepadatan_penduduk': 'Kepadatan Penduduk',
                'cluster': 'Cluster'
            }
            sort_col = st.selectbox("Urutkan:", options=list(sort_options.keys()), format_func=lambda x: sort_options[x])
        
        df_display = df_filtered[df_filtered['cluster'].isin(cluster_filter)].copy()
        df_display = df_display.sort_values(sort_col, ascending=(sort_col == 'kecamatan'))
        
        display_cols = ['kecamatan', 'jumlah_penduduk', 'kepadatan_penduduk', 'jumlah_kasus', 'ir', 
                        'curah_hujan', 'kelembapan', 'temperature', 'cluster', 'risk_category']
        display_cols = [c for c in display_cols if c in df_display.columns]
        
        # Mapping nama kolom agar lebih rapih
        column_rename = {
            'kecamatan': 'Kecamatan',
            'jumlah_penduduk': 'Jumlah Penduduk',
            'kepadatan_penduduk': 'Kepadatan Penduduk',
            'jumlah_kasus': 'Jumlah Kasus',
            'ir': 'Incidence Rate',
            'curah_hujan': 'Curah Hujan (mm)',
            'kelembapan': 'Kelembapan (%)',
            'temperature': 'Suhu (°C)',
            'cluster': 'Cluster',
            'risk_category': 'Kategori Risiko'
        }
        
        # Create styled HTML table
        def create_styled_table(dataframe):
            # Add color badges for risk_category
            df_styled = dataframe.copy()
            
            # Format numbers
            # Thousands separator
            for col in ['jumlah_penduduk', 'jumlah_kasus']:
                if col in df_styled.columns:
                    df_styled[col] = df_styled[col].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "0")
            
            # Decimals and separators
            for col in ['kepadatan_penduduk']:
                if col in df_styled.columns:
                    df_styled[col] = df_styled[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "0")

            # 2 Decimal places
            for col in ['ir', 'curah_hujan', 'kelembapan', 'temperature']:
                if col in df_styled.columns:
                    df_styled[col] = df_styled[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
            if 'risk_category' in df_styled.columns:
                risk_colors = {
                    'Rendah': '#28a745',
                    'Sedang': '#ffc107', 
                    'Tinggi': '#dc3545'
                }
                risk_text_colors = {
                    'Rendah': '#ffffff',
                    'Sedang': '#212529',
                    'Tinggi': '#ffffff'
                }
                df_styled['risk_category'] = df_styled['risk_category'].apply(
                    lambda x: f'<span style="background:{risk_colors.get(x, "#6c757d")};color:{risk_text_colors.get(x, "#fff")};padding:4px 10px;border-radius:12px;font-size:11px;font-weight:600;">{x}</span>' if pd.notna(x) else 'N/A'
                )
            if 'cluster' in df_styled.columns:
                cluster_colors = {0: '#28a745', 1: '#ffc107', 2: '#dc3545'}
                cluster_text = {0: '#ffffff', 1: '#212529', 2: '#ffffff'}
                df_styled['cluster'] = df_styled['cluster'].apply(
                    lambda x: f'<span style="background:{cluster_colors.get(int(x), "#6c757d")};color:{cluster_text.get(int(x), "#fff")};padding:4px 10px;border-radius:12px;font-size:11px;font-weight:600;">{int(x)}</span>' if pd.notna(x) else 'N/A'
                )
            
            # Rename kolom agar lebih rapih
            df_styled = df_styled.rename(columns=column_rename)
            
            styled_html = df_styled.to_html(index=False, escape=False, classes='custom-table')
            return f'''
            <div style="max-height: 420px; overflow-y: auto; border: 1px solid #e9ecef; border-radius: 8px;">
                <style>
                    .custom-table {{
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 13px;
                        background-color: #ffffff;
                    }}
                    .custom-table th {{
                        background-color: #f8f9fa;
                        color: #2c3e50;
                        padding: 12px 10px;
                        text-align: left;
                        font-weight: 600;
                        border-bottom: 2px solid #dee2e6;
                        position: sticky;
                        top: 0;
                    }}
                    .custom-table td {{
                        padding: 10px;
                        color: #2c3e50;
                        border-bottom: 1px solid #e9ecef;
                        background-color: #ffffff;
                    }}
                    .custom-table tr:hover td {{
                        background-color: #f8f9fa;
                    }}
                </style>
                {styled_html}
            </div>
            '''
        
        st.markdown(create_styled_table(df_display[display_cols]), unsafe_allow_html=True)
        
        csv_dl = df_display[display_cols].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv_dl, f"data_dbd_garut_{selected_year}.csv", "text/csv")
    
    with tab2:
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<p class="section-title">Jumlah Kasus per Kecamatan</p>', unsafe_allow_html=True)
            df_sorted = df_filtered.sort_values('jumlah_kasus', ascending=True)
            fig_bar = px.bar(df_sorted, x='jumlah_kasus', y='kecamatan', orientation='h',
                color='cluster', color_discrete_map=CLUSTER_COLORS,
                labels={'jumlah_kasus':'Jumlah Kasus','kecamatan':'','cluster':'Cluster'})
            fig_bar.update_layout(height=520, margin=dict(t=10,b=10,l=0,r=10),
                font=dict(family="Segoe UI",size=10,color=THEME["text"]),
                yaxis=dict(tickfont=dict(size=9)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color=THEME["text"])))
            fig_bar.update_xaxes(gridcolor='rgba(0,0,0,0.06)')
            st.plotly_chart(fig_bar, width='stretch')
        
        with g2:
            st.markdown('<p class="section-title">Scatter: IR vs Jumlah Kasus</p>', unsafe_allow_html=True)
            fig_sc = px.scatter(df_filtered, x='ir', y='jumlah_kasus', color='cluster',
                color_discrete_map=CLUSTER_COLORS,
                size='jumlah_kasus', hover_name='kecamatan',
                labels={'ir':'Incidence Rate','jumlah_kasus':'Jumlah Kasus','cluster':'Cluster'})
            fig_sc.update_layout(height=520, margin=dict(t=10,b=10),
                font=dict(family="Segoe UI",size=10,color=THEME["text"]),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(font=dict(color=THEME["text"])))
            fig_sc.update_xaxes(gridcolor='rgba(0,0,0,0.06)')
            fig_sc.update_yaxes(gridcolor='rgba(0,0,0,0.06)')
            st.plotly_chart(fig_sc, width='stretch')
    
    with tab3:
        yearly_stats = df.groupby('year').agg({'jumlah_kasus':'sum','ir':'mean'}).reset_index()
        t1, t2 = st.columns(2)
        with t1:
            st.markdown('<p class="section-title">Trend Total Kasus</p>', unsafe_allow_html=True)
            fig_t = px.line(yearly_stats, x='year', y='jumlah_kasus', markers=True,
                labels={'year':'Tahun','jumlah_kasus':'Total Kasus'})
            fig_t.update_traces(line_color=THEME["accent"], line_width=2.5, marker_size=8)
            fig_t.update_layout(height=280, margin=dict(t=10,b=10),
                font=dict(family="Segoe UI",size=10,color=THEME["text"]),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            fig_t.update_xaxes(gridcolor='rgba(0,0,0,0.06)')
            fig_t.update_yaxes(gridcolor='rgba(0,0,0,0.06)')
            st.plotly_chart(fig_t, width='stretch')
        with t2:
            st.markdown('<p class="section-title">Trend Rata-rata IR</p>', unsafe_allow_html=True)
            fig_i = px.line(yearly_stats, x='year', y='ir', markers=True,
                labels={'year':'Tahun','ir':'Rata-rata IR'})
            fig_i.update_traces(line_color='#6c757d', line_width=2.5, marker_size=8)
            fig_i.update_layout(height=280, margin=dict(t=10,b=10),
                font=dict(family="Segoe UI",size=10,color=THEME["text"]),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            fig_i.update_xaxes(gridcolor='rgba(0,0,0,0.06)')
            fig_i.update_yaxes(gridcolor='rgba(0,0,0,0.06)')
            st.plotly_chart(fig_i, width='stretch')
        
        st.markdown('<p class="section-title">Distribusi Cluster per Tahun</p>', unsafe_allow_html=True)
        yearly_cl = df.groupby(['year','cluster']).size().reset_index(name='count')
        yearly_cl['label'] = yearly_cl['cluster'].map({0:'Rendah',1:'Sedang',2:'Tinggi'})
        fig_s = px.bar(yearly_cl, x='year', y='count', color='label',
            color_discrete_map={'Rendah':CLUSTER_COLORS[0],'Sedang':CLUSTER_COLORS[1],'Tinggi':CLUSTER_COLORS[2]},
            labels={'year':'Tahun','count':'Jumlah Kecamatan','label':'Cluster'}, barmode='stack')
        fig_s.update_layout(height=280, margin=dict(t=10,b=10),
            font=dict(family="Segoe UI",size=10,color=THEME["text"]),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color=THEME["text"])))
        fig_s.update_xaxes(gridcolor='rgba(0,0,0,0.06)')
        fig_s.update_yaxes(gridcolor='rgba(0,0,0,0.06)')
        st.plotly_chart(fig_s, width='stretch')


# ===================== FAQ PAGE =====================
elif st.session_state.page == "faq":
    st.markdown("""
    <div class="main-header">
        <h1>❓ Frequently Asked Questions</h1>
        <p>Pertanyaan umum mengenai dashboard dan metodologi penelitian</p>
    </div>
    """, unsafe_allow_html=True)
    
    faq_items = [
        ("🌐 Apa itu Dashboard Peta Risiko DBD ini?",
         """Dashboard ini merupakan **Sistem Informasi Geografis (GIS) berbasis web** yang dikembangkan untuk memvisualisasikan dan menganalisis tingkat risiko penyakit Demam Berdarah Dengue (DBD) di **42 kecamatan Kabupaten Garut**.

Dashboard ini menggunakan **metode K-Means Clustering** untuk mengelompokkan wilayah berdasarkan tingkat risiko penularan DBD. Tujuan utamanya adalah membantu pengambilan keputusan dalam upaya pencegahan dan pengendalian DBD di tingkat kecamatan."""),

        ("🔬 Metode apa yang digunakan dalam analisis?",
         """Penelitian ini menggunakan **K-Means Clustering**, sebuah algoritma machine learning untuk mengelompokkan data menjadi beberapa cluster berdasarkan kemiripan karakteristik.

**6 Variabel yang digunakan:**
- 🏥 **Jumlah Kasus** - Total kasus DBD yang tercatat
- 📊 **Incidence Rate (IR)** - Tingkat kejadian per 100.000 penduduk
- 🌧️ **Curah Hujan** - Rata-rata curah hujan tahunan (mm)
- 💧 **Kelembapan** - Rata-rata kelembapan udara (%)
- 🌡️ **Suhu** - Rata-rata suhu udara (°C)
- 👥 **Kepadatan Penduduk** - Jumlah penduduk per km²

**Hasil clustering menghasilkan 3 kelompok risiko:**
- **Cluster 0** - Risiko Rendah
- **Cluster 1** - Risiko Sedang
- **Cluster 2** - Risiko Tinggi"""),

        ("🎨 Apa arti warna pada peta?",
         """Warna pada peta menunjukkan **tingkat risiko DBD** di setiap kecamatan:

🟢 **Hijau** = **Risiko Rendah** (Cluster 0)
Wilayah dengan kombinasi faktor risiko yang relatif rendah, jumlah kasus dan IR cenderung minimal.

🟡 **Kuning** = **Risiko Sedang** (Cluster 1)
Wilayah dengan tingkat risiko menengah yang memerlukan perhatian dan tindakan pencegahan.

🔴 **Merah** = **Risiko Tinggi** (Cluster 2)
Wilayah prioritas dengan risiko penularan DBD tertinggi yang memerlukan intervensi segera."""),

        ("📈 Apa itu Incidence Rate (IR)?",
         """**Incidence Rate (IR)** adalah ukuran epidemiologi yang menunjukkan **jumlah kasus baru penyakit per 100.000 penduduk** dalam periode waktu tertentu (biasanya satu tahun).

**Rumus perhitungan:**
```
IR = (Jumlah Kasus / Jumlah Penduduk) × 100.000
```

**Interpretasi IR:**
- **IR < 20** → Risiko rendah
- **IR 20-50** → Risiko sedang
- **IR > 50** → Risiko tinggi (KLB potensial)

Semakin tinggi nilai IR, semakin besar kemungkinan penularan DBD di wilayah tersebut."""),

        ("📂 Data apa saja yang digunakan?",
         """Dashboard ini menggunakan berbagai sumber data:

**1. Data Kesehatan** 🏥
- Jumlah kasus DBD per kecamatan per tahun
- Data jumlah penduduk
- Sumber: **Dinas Kesehatan Kabupaten Garut**

**2. Data Iklim & Cuaca** 🌦️
- Curah hujan rata-rata (mm)
- Kelembapan udara (%)
- Suhu rata-rata (°C)
- Sumber: **Google Earth Engine (CHIRPS & ERA5)**

**3. Data Geospasial** 🗺️
- Shapefile batas administrasi kecamatan
- Data kepadatan penduduk
- Sumber: **BPS & Badan Informasi Geospasial**"""),

        ("📖 Bagaimana cara menggunakan dashboard?",
         """**Panduan Penggunaan Dashboard:**

**1️⃣ Navigasi Halaman**
Gunakan menu di sidebar kiri untuk berpindah antar halaman:
- 🏠 **Home** - Peta utama dan ringkasan statistik
- 📊 **Lihat Data** - Tabel data dan grafik analisis
- ❓ **FAQ** - Informasi dan bantuan

**2️⃣ Filter Tahun**
Pilih tahun yang ingin ditampilkan menggunakan dropdown di sidebar.

**3️⃣ Interaksi Peta**
- **Hover** pada wilayah untuk melihat nama kecamatan
- **Klik** pada wilayah untuk melihat popup detail lengkap
- Gunakan kontrol zoom untuk memperbesar/memperkecil

**4️⃣ Analisis Data**
Di halaman "Lihat Data", Anda dapat:
- Melihat tabel lengkap dengan filter cluster
- Menganalisis grafik visualisasi
- Mengunduh data dalam format CSV"""),

        ("⚠️ Apa batasan dashboard ini?",
         """**Batasan yang perlu diperhatikan:**

1. **Ketergantungan Data** 📊
   Akurasi hasil clustering sangat bergantung pada kelengkapan dan keakuratan data input.

2. **Klasifikasi Relatif** 📅
   Pengelompokkan risiko bersifat relatif per tahun, sehingga perbandingan antar tahun harus dilakukan dengan hati-hati.

3. **Bukan Pengganti Analisis Profesional** 🔬
   Dashboard ini adalah alat bantu dan bukan pengganti analisis epidemiologi profesional oleh tenaga kesehatan.

4. **Faktor Lain** 🏘️
   Ada faktor risiko lain yang belum tercakup seperti perilaku masyarakat, kondisi sanitasi, dan keberadaan vektor nyamuk.

5. **Pembaruan Data** 🔄
   Data perlu diperbarui secara berkala untuk menjaga relevansi analisis."""),

        ("💻 Teknologi apa yang digunakan?",
         """**Stack Teknologi Dashboard:**

**Backend & Processing:**
- 🐍 **Python** - Bahasa pemrograman utama
- 📊 **Pandas** - Manipulasi dan analisis data
- 🗺️ **GeoPandas** - Pemrosesan data geospasial
- 🤖 **Scikit-learn** - Implementasi K-Means Clustering
- 🌍 **Google Earth Engine** - Akuisisi data iklim

**Frontend & Visualisasi:**
- 🎯 **Streamlit** - Framework web aplikasi
- 🗺️ **Folium** - Pembuatan peta interaktif
- 📈 **Plotly** - Grafik interaktif

**Data Sources:**
- 🌧️ **CHIRPS** - Data curah hujan satelit
- 🌡️ **ERA5** - Data reanalysis iklim"""),

    ]
    
    for q, a in faq_items:
        with st.expander(q, expanded=False):
            st.markdown(a)
    
    st.markdown(f"""
    <div class="faq-footer" style="background:{THEME["sidebar_bg"]};border-radius:12px;
         padding:28px;text-align:center;margin-top:24px;border:1px solid rgba(255,255,255,0.1);">
        <h3 style="margin-bottom:1px;font-size:1.2em;font-weight:600;">💬 Masih ada pertanyaan?</h3>
        <p style="font-size:0.95em;margin:0;">Hubungi developer untuk informasi lebih lanjut.</p>
    </div>
    """, unsafe_allow_html=True)

