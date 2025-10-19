import folium
import pandas as pd

m = folium.Map([50, 20], tiles="OpenStreetMap")

coords_df = pd.read_excel("DETEKTORY DANE.xlsx")
coords_df = coords_df.dropna(subset=["Latitude", "Longitude"])

for i in range(len(coords_df)):
    html=f"""
        <h1>{coords_df.iloc[i]["Nr detektora"]}</h1>
        <h4>Dane:</h4>
        <p>Szerokość geograficzna: {coords_df.iloc[i]["Latitude"]}</p>
        <p>Długość geograficzna: {coords_df.iloc[i]["Longitude"]}</p>
        <p>Data startu: {coords_df.iloc[i]["Start data"]}</p>
        <p>Data końca: {coords_df.iloc[i]["Koniec data"]}</p>
        """
    iframe = folium.IFrame(html=html, width=400, height=200)
    popup = folium.Popup(iframe, max_width=2650)
    folium.Marker(
        location=[coords_df.iloc[i]["Latitude"], coords_df.iloc[i]["Longitude"]],
        popup=popup
    ).add_to(m)

m.save("map.html")