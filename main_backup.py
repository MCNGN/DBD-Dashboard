import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import io

st.title("Interactive Map Dashboard with Shapefile")

def show_table(csv_df=None, gdf=None, full_display=False, max_height=1600, row_height=28):
    """Display table from CSV (preferred) or from GeoDataFrame attributes.
    If full_display=True the table is rendered fully (no internal scroll).
    Otherwise st.dataframe is used with a computed height to avoid excessive internal scrolling.
    Provides download buttons for CSV and Excel (.xlsx)."""
    st.subheader("Attribute Table")
    if csv_df is not None:
        df = csv_df
    elif gdf is not None:
        df = gdf.drop(columns="geometry", errors='ignore')
    else:
        st.info("No table to display.")
        return

    if full_display:
        # Renders the whole dataframe without internal scrolling (page will be long if large)
        st.write(df)
    else:
        # compute a reasonable height so small tables show fully without large blank space
        n_rows = len(df)
        header_height = 45
        calc_height = header_height + n_rows * row_height
        height = min(calc_height, max_height)
        st.dataframe(df, use_container_width=True, height=height)

    # CSV download
    csv = df.to_csv(index=False)

    # Excel download (write to bytes buffer)
    excel_buffer = io.BytesIO()
    try:
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
    except Exception:
        # fallback to default engine if openpyxl not available
        with pd.ExcelWriter(excel_buffer) as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_buffer.seek(0)
    excel_bytes = excel_buffer.getvalue()

    col1, col2 = st.columns(2)
    col1.download_button("Download CSV", csv, file_name="attributes.csv", mime="text/csv")
    col2.download_button(
        "Download Excel",
        excel_bytes,
        file_name="attributes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ...existing code...

def show_map(gdf, height=800):
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles=None, width='100%', height=f'{height}px')

    label_col = gdf.columns[1] if len(gdf.columns) > 1 else gdf.columns[0]
    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            'fillColor': '#3186cc',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.5,
        },
        name="Polygons",
        tooltip=folium.GeoJsonTooltip(fields=[label_col], aliases=["Label:"])
    ).add_to(m)

    for _, row in gdf.iterrows():
        centroid = row.geometry.centroid
        folium.Marker(
            location=[centroid.y, centroid.x],
            icon=folium.DivIcon(html=f"""<div style="font-size: 10pt; color: black;">{row[label_col]}</div>""")
        ).add_to(m)

    m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])
    st_folium(m, use_container_width=True, height=height)

# sidebar navigation
page = st.sidebar.selectbox("Page", ["Map", "Table"])

shp_folder = st.text_input("Enter the path to the folder containing your shapefile and/or CSV:")

if shp_folder and os.path.isdir(shp_folder):
    # find shapefile and CSV files
    shp_files = [f for f in os.listdir(shp_folder) if f.lower().endswith('.shp')]
    csv_files = [f for f in os.listdir(shp_folder) if f.lower().endswith('.csv')]

    gdf = None
    if shp_files:
        shp_path = os.path.join(shp_folder, shp_files[0])
        try:
            gdf = gpd.read_file(shp_path)
        except Exception as e:
            st.error(f"Failed to read shapefile: {e}")
            gdf = None

    if page == "Map":
        if gdf is not None:
            show_map(gdf, height=900)
        else:
            st.warning("No valid .shp file found in the specified folder for the map.")
    elif page == "Table":
        # let user choose which source to use for the table
        source = st.selectbox("Table source", ["CSV file (if available)", "Shapefile attributes"])
        # checkbox to control full display (no internal scroll)
        full_display = st.checkbox("Show full table without internal scroll (may be very long)", value=False)

        if source.startswith("CSV"):
            if csv_files:
                csv_choice = st.selectbox("Choose CSV", csv_files)
                csv_path = os.path.join(shp_folder, csv_choice)
                try:
                    csv_df = pd.read_csv(csv_path)
                    show_table(csv_df=csv_df, full_display=full_display)
                except Exception as e:
                    st.error(f"Failed to read CSV: {e}")
            else:
                st.warning("No CSV file found in the specified folder.")
        else:
            if gdf is not None:
                show_table(gdf=gdf, full_display=full_display)
            else:
                st.warning("No shapefile found to extract attributes from.")
else:
    st.info("Please enter the path to a folder containing a shapefile and/or CSV.")