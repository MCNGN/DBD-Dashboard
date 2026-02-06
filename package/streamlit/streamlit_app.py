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
    }}
    .main .block-container {{
        padding: 1.5rem 2rem 1.5rem 2rem !important;
        max-width: 100% !important;
    }}
    
    /* Remove iframe border */
    iframe {{
        border: none !important;
    }}
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {{
        background: {THEME["sidebar_bg"]};
        color: white;
        min-width: 260px;
        width: 260px !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem;
    }}
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h5 {{
        color: #ffffff !important;
    }}
    
    /* NAV BUTTONS */
    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        background: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px;
        padding: 12px 18px;
        font-size: 14px;
        font-weight: 600;
        text-align: left;
        transition: all 0.2s ease;
        margin-bottom: 6px;
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
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div > div {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] span {{
        color: #ffffff !important;
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
        border-radius: 10px;
        padding: 24px 28px;
        border: none;
        border-left: 4px solid {THEME["accent"]};
        margin-bottom: 16px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }}
    .metric-card h3 {{
        margin: 0 0 12px 0;
        font-size: 0.85em;
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
        font-size: 0.9em;
        color: {THEME["text_muted"]} !important;
        margin-top: 8px;
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
        font-size: 4em;
        font-weight: 600;
        color: {THEME["text"]} !important;
        margin: 12px 0 14px 0;
        padding: 0;
    }}
    
    /* ===== DIVIDER ===== */
    .custom-divider {{
        height: 1px;
        background: rgba(255,255,255,0.15);
        border: none;
        margin: 16px 0;
    }}
    
    /* ===== FOOTER ===== */
    .footer {{
        text-align: center;
        padding: 16px;
        color: {THEME["text_muted"]};
        font-size: 0.8em;
        border-top: 1px solid {THEME["border"]};
        margin-top: 28px;
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
    }}
    [data-testid="stMain"] .stSelectbox label,
    [data-testid="stMain"] .stMultiSelect label {{
        color: {THEME["text"]} !important;
    }}
    [data-testid="stMain"] [data-baseweb="select"] span,
    [data-testid="stMain"] [data-baseweb="tag"] span {{
        color: {THEME["text"]} !important;
    }}
    
    /* Multiselect tag styling */
    [data-testid="stMain"] [data-baseweb="tag"] {{
        background-color: #3498db !important;
    }}
    [data-testid="stMain"] [data-baseweb="tag"] span {{
        color: #ffffff !important;
    }}
    
    /* Expander */
    [data-testid="stMain"] .streamlit-expanderHeader p,
    [data-testid="stMain"] .streamlit-expanderHeader span {{
        color: {THEME["text"]} !important;
    }}
    [data-testid="stExpander"] summary span {{
        color: {THEME["text"]} !important;
    }}
    
    /* ===== SPACING FOR COLUMNS ===== */
    [data-testid="stHorizontalBlock"] {{
        gap: 20px !important;
    }}
    
    /* Sidebar section titles */
    [data-testid="stSidebar"] h5 {{
        font-size: 0.75em !important;
        margin-bottom: 10px !important;
        color: #e0e0e0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Sidebar horizontal rule */
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.2) !important;
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
    <div style='text-align: center; padding: 16px 0 20px 0;'>
        <span style='font-size: 2.5em;'>🦟</span>
        <h2 style='color: #ffffff !important; margin: 8px 0 4px 0; font-size: 1.2em; font-weight: 600;'>Dashboard DBD</h2>
        <p style='color: #b0b8c1 !important; font-size: 0.8em; margin: 0;'>Kabupaten Garut</p>
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
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    if st.session_state.page in ["home", "data"]:
        st.markdown("##### 📅 Filter Tahun")
        years = sorted(df['year'].unique())
        selected_year = st.selectbox("Pilih Tahun:", years, key="year_filter", label_visibility="collapsed")
    else:
        years = sorted(df['year'].unique())
        selected_year = years[-1]
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 10px 0;'>
        <p style='color: #8a939e !important; font-size: 0.72em; margin: 0;'>Skripsi © 2026 · Rifqi</p>
    </div>
    """, unsafe_allow_html=True)

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
    st.markdown(f"""
    <div class="main-header">
        <h1>🗺️ Peta Risiko DBD Kabupaten Garut</h1>
        <p>Visualisasi clustering risiko DBD tahun {selected_year}</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        m = folium.Map(location=center, zoom_start=9, tiles=THEME["map_tiles"])
        
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
            <div style="font-family:'Segoe UI',sans-serif;min-width:280px;background:#fff;color:#2c3e50;padding:0;border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,0.15);overflow:hidden;">
                <div style="background:{color};padding:14px 18px;color:white;">
                    <h4 style="margin:0;font-size:15px;font-weight:600;">📍 {row[kecamatan_col]}</h4>
                    <span style="font-size:12px;opacity:0.9;">Cluster: {cl_label}</span>
                </div>
                <div style="padding:16px 18px;">
                    <table style="width:100%;font-size:13px;color:#495057;border-collapse:collapse;">
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">Jumlah Kasus</td>
                            <td style="text-align:right;padding:10px 0;font-weight:600;">{kasus_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">Incidence Rate</td>
                            <td style="text-align:right;padding:10px 0;font-weight:600;">{ir_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">Jumlah Penduduk</td>
                            <td style="text-align:right;padding:10px 0;">{penduduk_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">Kepadatan Penduduk</td>
                            <td style="text-align:right;padding:10px 0;">{kepadatan_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">Curah Hujan</td>
                            <td style="text-align:right;padding:10px 0;">{curah_hujan_disp}</td>
                        </tr>
                        <tr style="border-bottom:1px solid #e9ecef;">
                            <td style="padding:10px 0;">Kelembapan</td>
                            <td style="text-align:right;padding:10px 0;">{kelembapan_disp}</td>
                        </tr>
                        <tr>
                            <td style="padding:10px 0;">Suhu Rata-rata</td>
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
            sort_col = st.selectbox("Urutkan:", ['kecamatan', 'ir', 'jumlah_kasus', 'jumlah_penduduk', 'kepadatan_penduduk', 'cluster'])
        
        df_display = df_filtered[df_filtered['cluster'].isin(cluster_filter)].copy()
        df_display = df_display.sort_values(sort_col, ascending=(sort_col == 'kecamatan'))
        
        display_cols = ['kecamatan', 'jumlah_penduduk', 'kepadatan_penduduk', 'jumlah_kasus', 'ir', 
                        'curah_hujan', 'kelembapan', 'temperature', 'cluster', 'risk_category']
        display_cols = [c for c in display_cols if c in df_display.columns]
        
        # Create styled HTML table
        def create_styled_table(dataframe):
            # Style the dataframe
            styled_html = dataframe.to_html(index=False, escape=False, classes='custom-table')
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
            st.plotly_chart(fig_bar)
        
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
            st.plotly_chart(fig_sc, use_container_width=True)
    
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
            st.plotly_chart(fig_t, use_container_width=True)
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
            st.plotly_chart(fig_i, use_container_width=True)
        
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
        st.plotly_chart(fig_s, use_container_width=True)


# ===================== FAQ PAGE =====================
elif st.session_state.page == "faq":
    st.markdown("""
    <div class="main-header">
        <h1>❓ Frequently Asked Questions</h1>
        <p>Pertanyaan umum mengenai dashboard dan metodologi penelitian</p>
    </div>
    """, unsafe_allow_html=True)
    
    faq_items = [
        ("Apa itu Dashboard Peta Risiko DBD ini?",
         "Dashboard GIS berbasis web untuk menampilkan hasil clustering risiko DBD di 42 kecamatan Kabupaten Garut menggunakan metode K-Means Clustering."),
        ("Metode apa yang digunakan?",
         "**K-Means Clustering** dengan 6 variabel: Jumlah Kasus, Incidence Rate, Curah Hujan, Kelembapan, Suhu, dan Kepadatan Penduduk. Menghasilkan 3 cluster: Rendah, Sedang, Tinggi."),
        ("Apa arti warna pada peta?",
         "**Hijau** = Risiko Rendah · **Kuning** = Risiko Sedang · **Merah** = Risiko Tinggi"),
        ("Apa itu Incidence Rate (IR)?",
         "Jumlah kasus baru per 100.000 penduduk per tahun. Semakin tinggi IR, semakin besar risiko penularan DBD di wilayah tersebut."),
        ("Data apa saja yang digunakan?",
         "Data kasus DBD dan penduduk dari Dinkes Garut, data curah hujan, kelembapan & suhu dari BMKG, serta shapefile batas administrasi kecamatan."),
        ("Bagaimana cara menggunakan dashboard?",
         "1. Pilih halaman di sidebar (Home/Lihat Data/FAQ)\n2. Pilih tahun yang ingin dilihat\n3. Klik area pada peta untuk melihat detail\n4. Gunakan 'Lihat Data' untuk tabel & grafik"),
        ("Apa batasan dashboard ini?",
         "Hasil clustering bergantung pada kelengkapan data, klasifikasi bersifat relatif per tahun, dan dashboard ini bukan pengganti analisis epidemiologi profesional."),
        ("Teknologi apa yang digunakan?",
         "**Python**, **Streamlit**, **Folium**, **GeoPandas**, **Plotly**, **Scikit-learn** untuk K-Means Clustering"),
    ]
    
    for q, a in faq_items:
        with st.expander(q, expanded=False):
            st.markdown(a)
    
    st.markdown(f"""
    <div style="background:{THEME["sidebar_bg"]};border-radius:8px;
         padding:24px;color:white;text-align:center;margin-top:20px;">
        <h3 style="color:white;margin-bottom:8px;font-size:1.1em;font-weight:600;">Masih ada pertanyaan?</h3>
        <p style="color:rgba(255,255,255,0.7);font-size:0.9em;margin:0;">Hubungi peneliti untuk informasi lebih lanjut.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="footer">Dashboard Peta Risiko DBD Kabupaten Garut | Skripsi © 2026</div>', unsafe_allow_html=True)

