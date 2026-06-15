import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.title("🌍 Fossil Cat Site Map")
st.write("A simple map showing the fossil sites and species in a clickable popup.")

@st.cache_data
def load_fossil_data():
    try:
        df = pd.read_excel("Fossil cats in europe.xlsx", engine="openpyxl")
    except ImportError:
        st.error("The app requires the openpyxl package to read Excel files. Install it with `pip install openpyxl` or `pip install -r requirements.txt`.")
        st.stop()

    df.columns = df.columns.str.strip()

    def parse_age(age):
        if pd.isna(age):
            return None
        age_str = str(age).lower().replace("ma", "").strip()
        try:
            return float(age_str)
        except ValueError:
            return None

    location_coords = {
        "Kvabebi, Georgia": (41.8751527, 45.5134570, "Georgia"),
        "Perrier-Les Etouaires, France": (45.5445494, 3.2032288, "Central France, estimated"),
        "Roca-Neyra, France": (44.7995467, 1.6181714, "Southwestern France, estimated"),
        "Vallparadís Section, Iberia": (41.5665425, 2.0215824, "Terrassa, Spain"),
        "Château Breccia, France": (46.5272244, 4.4326164, "Eastern France, estimated"),
        "Olivola, Italy": (45.0373877, 8.3675266, "Olivola, Italy"),
        "Gerakarou, Greece": (40.6281509, 23.2171109, "Greece"),
    }

    coords = df["Location"].map(lambda location: location_coords.get(location, (None, None, "unknown")))
    df[["lat", "lon", "Location note"]] = pd.DataFrame(coords.tolist(), index=df.index)
    df["AgeMa"] = df["Age"].map(parse_age)
    return df

fossils = load_fossil_data()

st.subheader("Fossil site table")
st.dataframe(fossils)

if "selected_age_range" not in st.session_state:
    st.session_state.selected_age_range = "All ages"

st.subheader("Filter by age range")
col1, col2, col3, col4 = st.columns(4)
if col1.button("All ages"):
    st.session_state.selected_age_range = "All ages"
if col2.button("0.0-0.99 Ma"):
    st.session_state.selected_age_range = "0.0-0.99 Ma"
if col3.button("1.0-1.99 Ma"):
    st.session_state.selected_age_range = "1.0-1.99 Ma"
if col4.button("2.0-2.99 Ma"):
    st.session_state.selected_age_range = "2.0-2.99 Ma"

selected_range = st.session_state.selected_age_range
st.write(f"Showing fossils in age range: **{selected_range}**")

ranges = {
    "0.0-0.99 Ma": (0.0, 0.99),
    "1.0-1.99 Ma": (1.0, 1.99),
    "2.0-2.99 Ma": (2.0, 2.99),
}
map_points = fossils.dropna(subset=["lat", "lon"])
if selected_range != "All ages":
    map_points = map_points.dropna(subset=["AgeMa"])
    low, high = ranges[selected_range]
    map_points = map_points[(map_points["AgeMa"] >= low) & (map_points["AgeMa"] <= high)]

if not map_points.empty:
    st.subheader("Map of fossil sites")
    center_lat = map_points["lat"].mean()
    center_lon = map_points["lon"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=4, tiles="OpenStreetMap")

    for _, row in map_points.iterrows():
        popup_html = (
            f"<b>Species:</b> {row['Species']}<br>"
            f"<b>Location:</b> {row['Location']}<br>"
            f"<b>Age:</b> {row['Age']}"
        )
        folium.Marker(
            location=(row["lat"], row["lon"]),
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row["Species"],
        ).add_to(m)

    st_folium(m, width=700, height=500)
    st.write("Click a marker to see the species and site details.")
else:
    st.write("No valid fossil sites found for this age range.")
