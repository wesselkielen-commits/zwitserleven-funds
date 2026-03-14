import os
import sqlite3
import pandas as pd
import requests
from io import StringIO

DB_PATH = "data/pension.db"
URL = "https://www.zwitserleven.nl/over-zwitserleven/verantwoord-beleggen/fondsen/"

print("=== START SCRIPT ===")
print("Working directory:", os.getcwd())
print("DB path:", DB_PATH)
print("DB exists before run:", os.path.exists(DB_PATH))

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(URL, headers=headers, timeout=30)
print("HTTP status:", response.status_code)
response.raise_for_status()

tables = pd.read_html(StringIO(response.text))
print("Aantal tabellen gevonden:", len(tables))

df = tables[0]
print("Kolommen gevonden:", list(df.columns))
print("Aantal rijen gevonden:", len(df))

# Alleen nodige kolommen
df = df[["Fonds", "Datum", "Koers"]]

# Koers opschonen
df["Koers"] = (
    df["Koers"]
    .astype(str)
    .str.replace("€", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)

# Datum opschonen
df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True)
new_date = df["Datum"].iloc[0].strftime("%Y-%m-%d")
print("Scrape datum:", new_date)

# Database openen
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Tabel aanmaken als die nog niet bestaat
cur.execute("""
CREATE TABLE IF NOT EXISTS prices (
    date TEXT,
    fund TEXT,
    price REAL,
    PRIMARY KEY (date, fund)
)
""")

# Laatste datum checken
cur.execute("SELECT MAX(date) FROM prices")
result = cur.fetchone()[0]
print("Laatste datum in DB:", result)

if result == new_date:
    print("Datum bestaat al, niks doen")
else:
    print("Nieuwe datum, data toevoegen")
    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT OR IGNORE INTO prices (date, fund, price)
            VALUES (?, ?, ?)
            """,
            (new_date, row["Fonds"], float(row["Koers"]))
        )
    conn.commit()
    print("Toegevoegd:", len(df), "regels")

conn.close()
print("=== EINDE SCRIPT ===")
