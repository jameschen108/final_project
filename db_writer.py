from dotenv import load_dotenv
import os
import pandas as pd
import pyodbc
from mlb_crawler import crawler

load_dotenv()

def write_all_years_to_azure_sql(years):
    conn = pyodbc.connect(
        f"DRIVER={os.getenv('DB_DRIVER')};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_UID')};"
        f"PWD={os.getenv('DB_PWD')}"
    )
    cursor = conn.cursor()

    all_data = []
    for year in years:
        df = crawler(year)
        if "year" not in df.columns:
            df.insert(0, "year", year)
        else:
            df["year"] = year

        all_data.append(df)

    full_df = pd.concat(all_data, ignore_index=True)

    columns = full_df.columns.tolist()
    col_defs = ",\n".join([
        f"[{col}] NVARCHAR(MAX)" if full_df[col].dtype == 'object' else f"[{col}] FLOAT"
        for col in columns
    ])

    cursor.execute(f"""
        IF OBJECT_ID('players_full', 'U') IS NOT NULL DROP TABLE players_full;
        CREATE TABLE players_full (
            {col_defs}
        )
    """)
    conn.commit()

    insert_query = f"INSERT INTO players_full ({', '.join([f'[{col}]' for col in columns])}) VALUES ({', '.join(['?' for _ in columns])})"
    for _, row in full_df.iterrows():
        values = [str(row[col]) if pd.isna(row[col]) else row[col] for col in columns]
        cursor.execute(insert_query, values)

    conn.commit()
    conn.close()
    print(f"✅ 成功將 {len(full_df)} 筆資料寫入 players_full")

if __name__ == "__main__":
    write_all_years_to_azure_sql(["2025", "2024", "2023", "2022"])
