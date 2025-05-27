from flask import Flask, request, jsonify
import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os
from mlb_crawler import crawler, Team_data

load_dotenv()

app = Flask(__name__)

# 建立 Azure SQL 連線
def get_connection():
    return pyodbc.connect(
        f"DRIVER={os.getenv('DB_DRIVER')};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_UID')};"
        f"PWD={os.getenv('DB_PWD')}"
    )

@app.route("/crawl", methods=["POST"])
def crawl_route():
    year = request.args.get("year", default="2024")
    try:
        Team_data(year)
        df = crawler(year)
        df.insert(0, 'year', year)  # 加入 year 欄位

        conn = get_connection()
        cursor = conn.cursor()

        # 重新建立完整欄位表格
        columns = df.columns.tolist()
        col_defs = ",\n".join([
            f"[{col}] NVARCHAR(MAX)" if df[col].dtype == 'object' else f"[{col}] FLOAT"
            for col in columns
        ])

        cursor.execute(f"""
            IF OBJECT_ID('players_full', 'U') IS NOT NULL DROP TABLE players_full;
            CREATE TABLE players_full (
                {col_defs}
            )
        """)
        conn.commit()

        # 寫入全部資料
        insert_query = f"INSERT INTO players_full ({', '.join([f'[{col}]' for col in columns])}) VALUES ({', '.join(['?' for _ in columns])})"
        for _, row in df.iterrows():
            values = [str(row[col]) if pd.isna(row[col]) else row[col] for col in columns]
            cursor.execute(insert_query, values)

        conn.commit()
        conn.close()

        return jsonify({"message": f"成功寫入 {len(df)} 筆資料至 players_full"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/players_full", methods=["GET"])
def get_all_full():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players_full")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
