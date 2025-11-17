## Install dependencies

1. Create a Python virtual enviroment (optional):

```bash
python -m venv .venv
```

2. Install requirements:

```bash
pip install -r requirements.txt
```

## How to use the scripts

Download the Excel spreadsheet and put it in the same repository as the scripts. The file is expected to be named "DETEKTORY DANE.xlsx" (default name after a download).

Then, you can run the first script that will split and sort the data into numerous CSV files:

```bash
python sort_data_csv.py
```

The files will be saved inside different directories in `data_csv/`. Each directory will hold separate CSV files for every unique value seen in the given column.

You can then turn the CSV files into Excel spreadsheets with the next script:

```bash
python csv_to_excel.py
```

The output will be saved into `data_excel/`. Each directory inside `data_csv/` will result in a single file with numerous sheets.