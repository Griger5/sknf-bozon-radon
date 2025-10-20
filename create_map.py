import folium
from folium.plugins import TagFilterButton
import pandas as pd
import numpy as np
import branca.colormap as cmp

m = folium.Map([50, 20], tiles="OpenStreetMap")

main_excel = pd.ExcelFile("DETEKTORY DANE.xlsx")

coords_df = pd.read_excel(main_excel, "Sheet1")
coords_df = coords_df.dropna(subset=["Latitude", "Longitude"])
detector_df = pd.read_excel("wyniki.xlsx").set_index("Detector ID")
categories_df = pd.read_excel(main_excel, "Info_Bool").fillna(0)

age_categories = ["<1900", "1900-1920", "1920-1940", "1940-1960", "1960-1980", "1980-2000", "2000-2020", "2020-2040"]
building_categories = ["blok", "kamienica", "szeregowy", "wolnostojący"]
material_categories = ["cegła", "beton", "pustak", "drewno", "kamień", "styropian", "wylewka", "wielka płyta"]
connections_categories = ["woda", "gaz", "kanalizacja", "wentylacja", "CO", "klimatyzacja"]

categories = [*age_categories, *building_categories, *material_categories, *connections_categories]

colors = ["green", "lightgreen", "orange", "red", "black"]

density_bins = [detector_df["Track density"].quantile(0.2 * i) for i in range(5)]

cmp.StepColormap(
    colors,
    index=[0] + density_bins[1:],
    vmin=0,
    vmax=detector_df["Track density"].max()/2.5,
    caption="Wartość gęstości śladu [ślad / mm^2]"
).add_to(m)

TagFilterButton(categories).add_to(m)

for i in range(len(coords_df)):
    try: 
        density = detector_df.loc[coords_df.iloc[i]["Nr detektora"].replace(" ", ""), "Track density"]
    except:
        denisty = "?"

    if density != "?":
        color = colors[int(np.digitize(density, density_bins)) - 1]
    else:
        color = "blue"

    building = str(coords_df.iloc[i]["Typ budynku"]).removesuffix("/blok")
    materials = []
    connections = []

    for cat in material_categories:
        if categories_df.iloc[i][cat]:
            materials.append(cat)

    for cat in connections_categories:
        if categories_df.iloc[i][cat]:
            connections.append(cat)

    age = "?"
    for val in range(1900,2040,20):
        if coords_df.iloc[i]["Rok Budowy"] == "?" or pd.isna(coords_df.iloc[i]["Rok Budowy"]):
            break
        elif int(coords_df.iloc[i]["Rok Budowy"].removeprefix("? ")) >= val and int(coords_df.iloc[i]["Rok Budowy"].removeprefix("? ")) < val + 20:
            age = f"{val}-{val+20}"
            break
    else:
        age = "<1900"

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
        icon=folium.Icon(color=color),
        tags=[building, *materials, *connections, age]
    ).add_to(m)

m.save("map.html")