import pandas as pd

from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

df = pd.read_excel("DETEKTORY DANE.xlsx")

for i in range(16,30):
    df.drop(f"Unnamed: {i}", axis=1, inplace=True)

for col in df:
    df.loc[:, col] = df[col].replace("?", 0)

df = df.fillna(0)

cols_to_sort_by = list(df.columns)

for unused_col in ["Imię i nazwisko", "Adres", "Longitude", "Latitude", "Nr detektora", "Start data", "Start godzina", "Koniec data", "Koniec godzina", "Uwagi", "Czas ekspozycji (dni)", "Rok Budowy"]:
    cols_to_sort_by.remove(unused_col)

DATA_DIR = BASE_DIR / "data_csv"
DATA_DIR.mkdir(exist_ok=True)

for col in cols_to_sort_by:
    column_dir = DATA_DIR / col
    column_dir.mkdir(exist_ok=True)

    unique_values = df[col].unique()

    for val in unique_values:
        split_df = df.loc[df[col] == str(val).rstrip()]
        file = column_dir / (str(val).removesuffix("/blok").rstrip().removesuffix("?").removeprefix("?") + ".csv")
        split_df.to_csv(file.absolute(), index=False)

exposure_time = "Czas ekspozycji (dni)"
exposure_time_dir = DATA_DIR / exposure_time
exposure_time_dir.mkdir(exist_ok=True)

for val in range(0,100,20):
    split_df = df.loc[(df[exposure_time] >= val) & (df[exposure_time] < val + 20)]
    file = exposure_time_dir / f"{val}-{val+20}.csv"
    split_df.to_csv(file.absolute(), index=False)

construction_year = "Rok Budowy"
construction_year_dir = DATA_DIR / construction_year
construction_year_dir.mkdir(exist_ok=True)

filtered_df = df.copy()
filtered_df.loc[:, construction_year] = [str(val).removeprefix("? ") for val in df[construction_year]]

for val in range(1900,2040,20):
    split_df = filtered_df.loc[(filtered_df[construction_year].astype(int) >= val) & (filtered_df[construction_year].astype(int) < val + 20)]
    file = construction_year_dir / f"{val}-{val+20}.csv"
    split_df.to_csv(file.absolute(), index=False)

split_df = filtered_df.loc[filtered_df[construction_year].astype(int) < 1900]
file = construction_year_dir / "<1900.csv"
split_df.to_csv(file.absolute(), index=False)