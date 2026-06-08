import sqlite3
import pandas as pd
import os

# ── Database setup ──────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "climate_history.db")

def init_db():
    """Create the database table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS climate_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            location TEXT,
            temperature REAL,
            co2_level REAL,
            rainfall REAL
        )
    """)
    conn.commit()
    conn.close()
    print("Database ready!")

def store_data(date, location, temperature, co2_level, rainfall):
    """Store one climate record"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO climate_records (date, location, temperature, co2_level, rainfall)
        VALUES (?, ?, ?, ?, ?)
    """, (date, location, temperature, co2_level, rainfall))
    conn.commit()
    conn.close()
    print(f"Stored: {date} | {location} | {temperature}°C")

def analyze_data():
    """Analyze and return historical data summary"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM climate_records", conn)
    conn.close()

    if df.empty:
        return {"message": "No data yet"}

    summary = {
        "total_records": len(df),
        "avg_temperature": round(df["temperature"].mean(), 2),
        "max_temperature": df["temperature"].max(),
        "min_temperature": df["temperature"].min(),
        "avg_co2": round(df["co2_level"].mean(), 2),
    }
    return summary

# ── Add sample data for testing ─────────────────
if __name__ == "__main__":
    init_db()
    store_data("2024-01-01", "Delhi", 22.5, 415.2, 5.0)
    store_data("2024-06-01", "Delhi", 38.0, 418.1, 0.5)
    store_data("2023-01-01", "Delhi", 19.0, 412.0, 8.0)
    print(analyze_data())