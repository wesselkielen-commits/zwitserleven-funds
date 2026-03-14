import pandas as pd
import sqlite3

DB_PATH = "data/pension.db"

URL = "https://www.zwitserleven.nl/over-zwitserleven/verantwoord-beleggen/fondsen/"


# -------------------
# SCRAPE WEBSITE
# -------------------

tables = pd.read_html(URL)

df = tables[0]

df = df[["Fonds", "Datum", "Koers"]]

df["Koers"] = (
    df["Koers"]
    .str.replace("€", "")
    .str.replace(",", ".")
    .str.strip()
    .astype(float)
)

df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True)

print("Scrape datum:", df["Datum"].iloc[0])


# -------------------
# CONNECT DATABASE
# -------------------

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()


# -------------------
# CHECK LAATSTE DATUM
# -------------------

cur.execute("SELECT MAX(date) FROM prices")

result = cur.fetchone()[0]

print("Laatste datum in DB:", result)


new_date = df["Datum"].iloc[0].strftime("%Y-%m-%d")


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
    print("Toegevoegd")


conn.close()
