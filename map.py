import folium
from folium.plugins import TagFilterButton
import pandas as pd
import numpy as np
import branca.colormap as cmp
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from folium import Element

# Funkcja do tworzenia wykresów base64
def plot_to_base64():
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    return image_base64

# Funkcja do generowania statystyk
def generate_statistics(coords_df, detector_df, categories_df):
    stats_html = """
    <style>
        .stat-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #f9f9f9;
        }
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin: 10px 0;
        }
        .stat-card {
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            background: white;
        }
        h2 { color: #2c3e50; }
        h3 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
    </style>
    <h2> Opcje statystyczne</h2>
    """
    
    # Podstawowe statystyki
    densities = []
    for i in range(len(coords_df)):
        try:
            detector_id = coords_df.iloc[i]["Nr detektora"].replace(" ", "")
            density_value = detector_df.loc[detector_id, "Stężenie radonu"]
            if hasattr(density_value, 'item'):
                density_value = density_value.item()
            densities.append(float(density_value))
        except:
            continue
    
    if densities:
        # Histogram ogólny
        plt.figure(figsize=(10, 6))
        plt.hist(densities, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Rozkład stężenia radonu - wszystkie detektory')
        plt.xlabel('Stęzenie radonu [Bq/m³]')
        plt.ylabel('Liczba detektorów')
        plt.grid(True, alpha=0.3)
        hist_all = plot_to_base64()
        
        stats_html += f"""
        <div class="stat-section">
            <h3>Statystyki ogólne (stężenia radonu)</h3>
            <p><b>Liczba detektorów z danymi:</b> {len(densities)}</p>
            <p><b>Średnie stężenie:</b> {np.mean(densities):.2f} ± {np.std(densities):.2f} Bq/m³</p>
            <p><b>Mediana:</b> {np.median(densities):.2f} Bq/m³</p>
            <p><b>Zakres:</b> {np.min(densities):.2f} - {np.max(densities):.2f} Bq/m³</p>
            <p><b>Odchylenie standardowe:</b> {np.std(densities):.2f}</p>
            <p><b>Współczynnik zmienności:</b> {(np.std(densities)/np.mean(densities)*100):.1f}%</p>
            <img src="data:image/png;base64,{hist_all}" style="width:100%; max-width:600px;">
        </div>
        """
    
    # Statystyki per typ budynku
    building_stats = {}
    for building_type in ["kamienica", "blok", "wolnostojący", "szeregowy"]:
        building_densities = []
        for i in range(len(coords_df)):
            try:
                building = str(coords_df.iloc[i]["Typ budynku"]).removesuffix("/blok")
                if building == building_type:
                    detector_id = coords_df.iloc[i]["Nr detektora"].replace(" ", "")
                    density_value = detector_df.loc[detector_id, "Stężenie radonu"]
                    if hasattr(density_value, 'item'):
                        density_value = density_value.item()
                    building_densities.append(float(density_value))
            except:
                continue
        
        if building_densities:
            building_stats[building_type] = {
                'mean': np.mean(building_densities),
                'std': np.std(building_densities),
                'count': len(building_densities),
                'median': np.median(building_densities),
                'min': np.min(building_densities),
                'max': np.max(building_densities),
                'data': building_densities
            }
    
    if building_stats:
        # Wykres pudełkowy dla ttypow budynkow
        plt.figure(figsize=(12, 6))
        box_data = [data['data'] for data in building_stats.values()]
        box_labels = [f"{k}\n(n={v['count']})" for k, v in building_stats.items()]
        
        plt.boxplot(box_data, tick_labels=box_labels)
        plt.title('Porównanie stężenia radonu wg typu budynku')
        plt.ylabel('Stężenie radonu [Bq/m³]')
        plt.grid(True, alpha=0.3)
        boxplot_buildings = plot_to_base64()
        
        stats_html += f"""
        <div class="stat-section">
            <h3>Statystyki wg typu budynku</h3>
            <div class="grid-container">
        """
        
        for building_type, stats in building_stats.items():
            stats_html += f"""
                <div class="stat-card">
                    <h4>{building_type.capitalize()}</h4>
                    <p><b>Średnia:</b> {stats['mean']:.2f} ± {stats['std']:.2f}</p>
                    <p><b>Mediana:</b> {stats['median']:.2f}</p>
                    <p><b>Liczba:</b> {stats['count']}</p>
                    <p><b>Zakres:</b> {stats['min']:.2f}-{stats['max']:.2f}</p>
                </div>
            """
        
        stats_html += f"""
            </div>
            <img src="data:image/png;base64,{boxplot_buildings}" style="width:100%; max-width:700px; margin-top:20px;">
        </div>
        """
    
    # Statystyki per wiek budynku
    age_stats = {}
    age_categories_list = ["<1900", "1900-1920", "1920-1940", "1940-1960", "1960-1980", "1980-2000", "2000-2020", "2020-2040"]
    
    for age_cat in age_categories_list:
        age_densities = []
        for i in range(len(coords_df)):
            try:
                #okreslenie katergroii wieku budynku 
                rok_budowy = coords_df.iloc[i]["Rok Budowy"]
                age = "?"
                
                if pd.isna(rok_budowy) or rok_budowy == "?":
                    continue
                else:
                    rok_str = str(rok_budowy)
                    if rok_str.startswith("? "):
                        rok_str = rok_str[2:]
                    
                    try:
                        rok_int = int(rok_str)
                        if rok_int < 1900:
                            calculated_age = "<1900"
                        else:
                            for val in range(1900, 2040, 20):
                                if val <= rok_int < val + 20:
                                    calculated_age = f"{val}-{val+20}"
                                    break
                            else:
                                calculated_age = "2020-2040"
                    except:
                        continue
                
                if calculated_age == age_cat:
                    detector_id = coords_df.iloc[i]["Nr detektora"].replace(" ", "")
                    density_value = detector_df.loc[detector_id, "Stężenie radonu"]
                    if hasattr(density_value, 'item'):
                        density_value = density_value.item()
                    age_densities.append(float(density_value))
            except:
                continue
        
        if age_densities:
            age_stats[age_cat] = {
                'mean': np.mean(age_densities),
                'std': np.std(age_densities),
                'count': len(age_densities),
                'median': np.median(age_densities),
                'data': age_densities
            }
    
    if age_stats:
        # Wykres slupkowy dla wieku
        plt.figure(figsize=(12, 6))
        age_labels = list(age_stats.keys())
        age_means = [stats['mean'] for stats in age_stats.values()]
        age_stds = [stats['std'] for stats in age_stats.values()]
        
        bars = plt.bar(range(len(age_means)), age_means, yerr=age_stds, 
                      capsize=5, alpha=0.7, color='lightcoral')
        plt.xticks(range(len(age_means)), age_labels, rotation=45)
        plt.title('Średnie stężenie radonu wg wieku budynku')
        plt.ylabel('Stężenie radonu [Bq/m³]')
        
        
        for bar, mean, count in zip(bars, age_means, [stats['count'] for stats in age_stats.values()]):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{mean:.1f}\nn={count}', ha='center', va='bottom', fontsize=9)
        
        plt.grid(True, alpha=0.3)
        age_chart = plot_to_base64()
        
        stats_html += f"""
        <div class="stat-section">
            <h3>Statystyki wg wieku budynku</h3>
            <img src="data:image/png;base64,{age_chart}" style="width:100%; max-width:800px;">
        </div>
        """
    
    # Statystyki per materiały budowlane
    material_stats = {}
    material_categories_list = ["cegła", "beton", "pustak", "drewno", "kamień", "styropian", "wylewka", "wielka płyta"]
    
    for material in material_categories_list:
        material_densities = []
        for i in range(len(coords_df)):
            try:
                if categories_df.iloc[i][material]:
                    detector_id = coords_df.iloc[i]["Nr detektora"].replace(" ", "")
                    density_value = detector_df.loc[detector_id, "Stężenie radonu"]
                    if hasattr(density_value, 'item'):
                        density_value = density_value.item()
                    material_densities.append(float(density_value))
            except:
                continue
        
        if material_densities:
            material_stats[material] = {
                'mean': np.mean(material_densities),
                'std': np.std(material_densities),
                'count': len(material_densities),
                'median': np.median(material_densities)
            }
    
    if material_stats:
        stats_html += f"""
        <div class="stat-section">
            <h3>Statystyki wg materiałów budowlanych</h3>
            <div class="grid-container">
        """
        
        for material, stats in material_stats.items():
            stats_html += f"""
                <div class="stat-card">
                    <b>{material.capitalize()}</b><br>
                    Średnia: {stats['mean']:.2f} ± {stats['std']:.2f}<br>
                    Mediana: {stats['median']:.2f}<br>
                    n={stats['count']}
                </div>
            """
        
        stats_html += "</div></div>"

        ####################################################################################################
    # ############################################################################################
    
    # Podstawowe statystyki
    densities = []
    for i in range(len(coords_df)):
        try:
            detector_id = coords_df.iloc[i]["Nr detektora"].replace(" ", "")
            density_value = detector_df.loc[detector_id, "a"]
            if hasattr(density_value, 'item'):
                density_value = density_value.item()
            densities.append(float(density_value))
        except:
            continue
    
    if densities:
        # Histogram ogólny
        plt.figure(figsize=(10, 6))
        plt.hist(densities, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Rozkład średniorocznego stężenia radonu - wszystkie detektory')
        plt.xlabel('Średnioroczne stężenie radonu [Bq/m³]')
        plt.ylabel('Liczba detektorów')
        plt.grid(True, alpha=0.3)
        hist_all = plot_to_base64()
        
        stats_html += f"""
        <div class="stat-section">
            <h3>Statystyki ogólne (średniorocznego stężenia radonu)</h3>
            <p><b>Liczba detektorów z danymi:</b> {len(densities)}</p>
            <p><b>Średnie stężenie:</b> {np.mean(densities):.2f} ± {np.std(densities):.2f} Bq/m³</p>
            <p><b>Mediana:</b> {np.median(densities):.2f} Bq/m³</p>
            <p><b>Zakres:</b> {np.min(densities):.2f} - {np.max(densities):.2f} Bq/m³</p>
            <p><b>Odchylenie standardowe:</b> {np.std(densities):.2f}</p>
            <p><b>Współczynnik zmienności:</b> {(np.std(densities)/np.mean(densities)*100):.1f}%</p>
            <img src="data:image/png;base64,{hist_all}" style="width:100%; max-width:600px;">
        </div>
        """
    
    # Statystyki per typ budynku
    building_stats = {}
    for building_type in ["kamienica", "blok", "wolnostojący", "szeregowy"]:
        building_densities = []
        for i in range(len(coords_df)):
            try:
                building = str(coords_df.iloc[i]["Typ budynku"]).removesuffix("/blok")
                if building == building_type:
                    detector_id = coords_df.iloc[i]["Nr detektora"].replace(" ", "")
                    density_value = detector_df.loc[detector_id, "a"]
                    if hasattr(density_value, 'item'):
                        density_value = density_value.item()
                    building_densities.append(float(density_value))
            except:
                continue
        
        if building_densities:
            building_stats[building_type] = {
                'mean': np.mean(building_densities),
                'std': np.std(building_densities),
                'count': len(building_densities),
                'median': np.median(building_densities),
                'min': np.min(building_densities),
                'max': np.max(building_densities),
                'data': building_densities
            }
    
    if building_stats:
        # Wykres pudełkowy dla ttypow budynkow
        plt.figure(figsize=(12, 6))
        box_data = [data['data'] for data in building_stats.values()]
        box_labels = [f"{k}\n(n={v['count']})" for k, v in building_stats.items()]
        
        plt.boxplot(box_data, tick_labels=box_labels)
        plt.title('Porównanie średniorocznego stężenia radonu wg typu budynku')
        plt.ylabel('a [Bq/m³]')
        plt.grid(True, alpha=0.3)
        boxplot_buildings = plot_to_base64()
        
        stats_html += f"""
        <div class="stat-section">
            <h3>Statystyki wg typu budynku</h3>
            <div class="grid-container">
        """
        
        for building_type, stats in building_stats.items():
            stats_html += f"""
                <div class="stat-card">
                    <h4>{building_type.capitalize()}</h4>
                    <p><b>Średnia:</b> {stats['mean']:.2f} ± {stats['std']:.2f}</p>
                    <p><b>Mediana:</b> {stats['median']:.2f}</p>
                    <p><b>Liczba:</b> {stats['count']}</p>
                    <p><b>Zakres:</b> {stats['min']:.2f}-{stats['max']:.2f}</p>
                </div>
            """
        
        stats_html += f"""
            </div>
            <img src="data:image/png;base64,{boxplot_buildings}" style="width:100%; max-width:700px; margin-top:20px;">
        </div>
        """
    
    # Statystyki per wiek budynku
    age_stats = {}
    age_categories_list = ["<1900", "1900-1920", "1920-1940", "1940-1960", "1960-1980", "1980-2000", "2000-2020", "2020-2040"]
    
    for age_cat in age_categories_list:
        age_densities = []
        for i in range(len(coords_df)):
            try:
                #okreslenie katergroii wieku budynku 
                rok_budowy = coords_df.iloc[i]["Rok Budowy"]
                age = "?"
                
                if pd.isna(rok_budowy) or rok_budowy == "?":
                    continue
                else:
                    rok_str = str(rok_budowy)
                    if rok_str.startswith("? "):
                        rok_str = rok_str[2:]
                    
                    try:
                        rok_int = int(rok_str)
                        if rok_int < 1900:
                            calculated_age = "<1900"
                        else:
                            for val in range(1900, 2040, 20):
                                if val <= rok_int < val + 20:
                                    calculated_age = f"{val}-{val+20}"
                                    break
                            else:
                                calculated_age = "2020-2040"
                    except:
                        continue
                
                if calculated_age == age_cat:
                    detector_id = coords_df.iloc[i]["Nr detektora"].replace(" ", "")
                    density_value = detector_df.loc[detector_id, "a"]
                    if hasattr(density_value, 'item'):
                        density_value = density_value.item()
                    age_densities.append(float(density_value))
            except:
                continue
        
        if age_densities:
            age_stats[age_cat] = {
                'mean': np.mean(age_densities),
                'std': np.std(age_densities),
                'count': len(age_densities),
                'median': np.median(age_densities),
                'data': age_densities
            }
    
    if age_stats:
        # Wykres slupkowy dla wieku
        plt.figure(figsize=(12, 6))
        age_labels = list(age_stats.keys())
        age_means = [stats['mean'] for stats in age_stats.values()]
        age_stds = [stats['std'] for stats in age_stats.values()]
        
        bars = plt.bar(range(len(age_means)), age_means, yerr=age_stds, 
                      capsize=5, alpha=0.7, color='lightcoral')
        plt.xticks(range(len(age_means)), age_labels, rotation=45)
        plt.title('Średnioroczne stężenie radonu wg wieku budynku')
        plt.ylabel('Średnioroczne stężenie radonu [Bq/m³]')
        
        
        for bar, mean, count in zip(bars, age_means, [stats['count'] for stats in age_stats.values()]):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{mean:.1f}\nn={count}', ha='center', va='bottom', fontsize=9)
        
        plt.grid(True, alpha=0.3)
        age_chart = plot_to_base64()
        
        stats_html += f"""
        <div class="stat-section">
            <h3>Statystyki wg wieku budynku</h3>
            <img src="data:image/png;base64,{age_chart}" style="width:100%; max-width:800px;">
        </div>
        """
    
    # Statystyki per materiały budowlane
    material_stats = {}
    material_categories_list = ["cegła", "beton", "pustak", "drewno", "kamień", "styropian", "wylewka", "wielka płyta"]
    
    for material in material_categories_list:
        material_densities = []
        for i in range(len(coords_df)):
            try:
                if categories_df.iloc[i][material]:
                    detector_id = coords_df.iloc[i]["Nr detektora"].replace(" ", "")
                    density_value = detector_df.loc[detector_id, "a"]
                    if hasattr(density_value, 'item'):
                        density_value = density_value.item()
                    material_densities.append(float(density_value))
            except:
                continue
        
        if material_densities:
            material_stats[material] = {
                'mean': np.mean(material_densities),
                'std': np.std(material_densities),
                'count': len(material_densities),
                'median': np.median(material_densities)
            }
    
    if material_stats:
        stats_html += f"""
        <div class="stat-section">
            <h3>Statystyki wg materiałów budowlanych</h3>
            <div class="grid-container">
        """
        
        for material, stats in material_stats.items():
            stats_html += f"""
                <div class="stat-card">
                    <b>{material.capitalize()}</b><br>
                    Średnia: {stats['mean']:.2f} ± {stats['std']:.2f}<br>
                    Mediana: {stats['median']:.2f}<br>
                    n={stats['count']}
                </div>
            """
        
        stats_html += "</div></div>"
    
    # Podsumowanie jakies tego 
    if densities:
        stats_html += f"""
        <div class="stat-section" style="background: #e8f4f8;">
            <h3> Podsumowanie</h3>
            <p><b>Całkowita liczba detektorów:</b> {len(coords_df)}</p>
            <p><b>Detektory z danymi pomiarowymi:</b> {len(densities)} ({len(densities)/len(coords_df)*100:.1f}%)</p>
            <p><b>Detektory bez danych:</b> {len(coords_df) - len(densities)}</p>
            <p><b>Ogólny poziom radonu:</b> {'Niski' if np.mean(densities) < np.median(densities) else 'Średni/Wysoki'}</p>
        </div>
        """
    
    return stats_html

m = folium.Map([50, 20], tiles="OpenStreetMap")

main_excel = pd.ExcelFile("DETEKTORY DANE.xlsx")

coords_df = pd.read_excel(main_excel, "Sheet1")
coords_df = coords_df.dropna(subset=["Latitude", "Longitude"])
detector_df = pd.read_excel("wyniki.xlsx").set_index("Nr detektora")
# detector_df = pd.read_excel("wyniki.xlsx").set_index("Detector ID")
categories_df = pd.read_excel(main_excel, "Info_Bool").fillna(0)

age_categories = ["<1900", "1900-1920", "1920-1940", "1940-1960", "1960-1980", "1980-2000", "2000-2020", "2020-2040"]
building_categories = ["blok", "kamienica", "szeregowy", "wolnostojący"]
material_categories = ["cegła", "beton", "pustak", "drewno", "kamień", "styropian", "wylewka", "wielka płyta"]
connections_categories = ["woda", "gaz", "kanalizacja", "wentylacja", "CO", "klimatyzacja"]

categories = [*age_categories, *building_categories, *material_categories, *connections_categories]

colors = ["green", "lightgreen", "orange", "red", "black"]

# density_bins = [detector_df["Track density"].quantile(0.2 * i) for i in range(5)]
density_bins = [detector_df["Stężenie radonu"].quantile(0.2 * i) for i in range(5)]

cmp.StepColormap(
    colors,
    index=[0] + density_bins[1:],
    vmin=0,
    # vmax=detector_df["Track density"].max()/2.5,
    vmax=detector_df["Stężenie radonu"].max()/2.5,
    # caption="Wartość gęstości śladu [ślad / mm^2]"
    caption="Wartość stężenia radonu [Bq/m³]"
).add_to(m)

stats_html = generate_statistics(coords_df, detector_df, categories_df)


button_html = f'''
<div style="position: fixed; top: 50%; right: 10px; transform: translateY(-50%); z-index: 1000;">
    <button onclick="document.getElementById('statsModal').style.display='block'" style="
        background: #9b59b6; color: white; border: none; padding: 15px 10px; 
        border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3); writing-mode: vertical-rl;
        text-orientation: mixed; height: 150px; letter-spacing: 2px;
    ">
        STATYSTYKI
    </button>
</div>

<div id="statsModal" style="
    display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
    background: rgba(0,0,0,0.5); z-index: 2000; overflow: auto;
">
    <div style="
        background: white; margin: 20px auto; padding: 20px; width: 95%; 
        max-width: 1200px; border-radius: 10px; max-height: 95vh; overflow-y: auto;
    ">
        <div style="text-align: right; margin-bottom: 15px; position: sticky; top: 0; background: white; padding: 10px 0;">
            <button onclick="document.getElementById('statsModal').style.display='none'" style="
                background: #e74c3c; color: white; border: none; padding: 8px 15px; 
                border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold;
            ">✕ Zamknij</button>
        </div>
        {stats_html}
    </div>
</div>
'''

m.get_root().html.add_child(Element(button_html))

TagFilterButton(categories).add_to(m)

for i in range(len(coords_df)):
    # try: 
    #     density_value = detector_df.loc[coords_df.iloc[i]["Nr detektora"].replace(" ", ""), "Track density"]
    #     # to leci na float w przyadku gydby to bylo series, wazna zmiana imo bo mi sie wypierdalalo xdd
    #     if isinstance(density_value, pd.Series):
    #         density_value = density_value.iloc[0]
    #     density = float(density_value)
    #     color = colors[int(np.digitize(density, density_bins)) - 1]
    # except Exception as e:
    #     density = "?"
    #     color = "blue"

    print(list(detector_df.index))
    # print(detector_df.loc[coords_df.iloc[i]["Nr detektora"].strip(), "Stężenie radonu"])

    try: 
        if (coords_df.iloc[i]["Nr detektora"].strip() == "HA4116"):
            continue
        density = detector_df.loc[coords_df.iloc[i]["Nr detektora"].strip(), "Stężenie radonu"]
    except:
        density = "?"

    try: 
        if (coords_df.iloc[i]["Nr detektora"].strip() == "HA4116"):
            yearly = "?"
            continue
        yearly = detector_df.loc[coords_df.iloc[i]["Nr detektora"].strip(), "a"]
    except:
        yearly = "?"

    if isinstance(density, pd.Series):
        density = density.iloc[0]

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
    rok_budowy = coords_df.iloc[i]["Rok Budowy"]
    
    if pd.isna(rok_budowy) or rok_budowy == "?":
        age = "?"
    else:
        #konw na stringa
        rok_str = str(rok_budowy)
        if rok_str.startswith("? "):
            rok_str = rok_str[2:]
        
        #konw na liczbe
        try:
            rok_int = int(rok_str)
            if rok_int < 1900:
                age = "<1900"
            else:
                for val in range(1900, 2040, 20):
                    if val <= rok_int < val + 20:
                        age = f"{val}-{val+20}"
                        break
                else:
                    age = "2020-2040"
        except (ValueError, TypeError):
            age = "?"

    html=f"""
        <h1>{coords_df.iloc[i]["Nr detektora"]}</h1>
        <h4>Dane:</h4>
        <p>
            Stężenie radonu: {density} [Bq/m3]<br/>
            Średnioroczne stężenie: {yearly} [Bq/m3]<br/> 
            Data startu: {coords_df.iloc[i]["Start data"]}<br/>
            Data końca: {coords_df.iloc[i]["Koniec data"]}<br/>
            Czas ekspozycji: {coords_df.iloc[i]["Czas ekspozycji (dni)"]} dni<br/>
            Rok budowy: {coords_df.iloc[i]["Rok Budowy"]}<br/>
            Typ budynku: {building}<br/>
            Materiały budowlane: {", ".join(materials)}<br/>
            Przyłącza: {", ".join(connections)}<br/>
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