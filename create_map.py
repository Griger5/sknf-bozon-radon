import folium
import pandas as pd
import numpy as np

m = folium.Map([50, 20], tiles="OpenStreetMap")

coords_df = pd.read_excel("DETEKTORY DANE.xlsx")
coords_df = coords_df.dropna(subset=["Latitude", "Longitude"])
detector_df = pd.read_excel("wyniki.xlsx").set_index("Detector ID")

colors = ["green", "lightgreen", "orange", "red", "black"]

density_bins = [detector_df["Track density"].quantile(0.2 * i) for i in range(5)]

for i in range(len(coords_df)):
    try: 
        density = detector_df.loc[coords_df.iloc[i]["Nr detektora"].replace(" ", ""), "Track density"]
    except:
        denisty = "?"

    if density != "?":
        color = colors[int(np.digitize(density, density_bins)) - 1]
    else:
        color = "blue"

    html=f"""
        <h1>{coords_df.iloc[i]["Nr detektora"]}</h1>
        <h4>Dane:</h4>
        <p>
            Track density: {density}<br/>
            Data startu: {coords_df.iloc[i]["Start data"]}<br/>
            Data końca: {coords_df.iloc[i]["Koniec data"]}<br/>
            Czas ekspozycji: {coords_df.iloc[i]["Czas ekspozycji (dni)"]} dni<br/>
            Rok budowy: {coords_df.iloc[i]["Rok Budowy"]}<br/>
            Uwagi: {coords_df.iloc[i]["Uwagi"]}<br/>
        </p>
        """
    iframe = folium.IFrame(html=html, width=400, height=300)
    popup = folium.Popup(iframe, max_width=2650)
    folium.Marker(
        location=[coords_df.iloc[i]["Latitude"], coords_df.iloc[i]["Longitude"]],
        popup=popup,
        icon=folium.Icon(color=color)
    ).add_to(m)

m.save("map.html")