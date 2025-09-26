from pyexcel.cookbook import merge_all_to_a_book

import glob
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
CSV_DIR = BASE_DIR / "data_csv"

EXCEL_DIR = BASE_DIR / "data_excel"
EXCEL_DIR.mkdir()

for directory in CSV_DIR.iterdir():
    merge_all_to_a_book(glob.glob(f"data_csv/{directory.name}/*.csv"), f"data_excel/{directory.name}.xlsx")