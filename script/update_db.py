import pandas as pd
import sqlite3
import os
import requests

DB_PATH = "data/pension.db"
URL = "https://www.zwitserleven.nl/over-zwitserleven/verantwoord-beleggen/fondsen/"

print("Current working directory:", os.getcwd())
print("Database path:", DB_PATH)
print("Database exists before run:", os.path.exists(DB_PATH))
print("Start ophalen website...")

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=30)
response.raise_for_status()

print("Website status code:", response.status_code)

tables = pd.read_html(response.text)

print("Aantal tabellen gevonden:", len(tables))

df = tables[0]
print("Kolommen gevonden:", list(df.columns))
print("Aantal rijen gevonden:", len(df))

df = df[["Fonds", "Datum", "Koers"]]

df["Koers"] = (
    df["Koers"]
    .astype(str)
    .str.replace("€", "", regex=False)
    .str.replace(",", ".", regex=False)
    .str.strip()
    .astype(float)
)

df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True)

new_date = df["Datum"].iloc[0].strftime("%Y-%m-%d")
print("Scrape datum:", new_date)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS prices (
    date TEXT,
    fund TEXT,
    price REAL,
    PRIMARY KEY (date, fund)
)
""")

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
            (
                new_date,
                row["Fonds"],
                float(row["Koers"]),
            ),
        )
    conn.commit()
    print("Toegevoegd:", len(df), "regels")

conn.close()
print("Script klaar")
