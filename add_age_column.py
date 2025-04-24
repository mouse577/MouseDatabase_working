import sqlite3
import re
from pathlib import Path

# Database paths
DB_FILES = [
    "ROOM_428.db",
    "EUTHANIZED.db",
    "ROOM_203B.db",
    "BREEDERS.db",
    "NR1.db"
]

TABLE_NAME = "mouse_list"

def add_age_column_to_db(db_file):
    if not Path(db_file).exists():
        print(f"⚠️ Skipping {db_file}: File not found.")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Check if AGE_IN_DAYS already exists
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = [row[1] for row in cursor.fetchall()]
    if "AGE_IN_DAYS" in columns:
        print(f"✅ {db_file} already has AGE_IN_DAYS.")
    else:
        cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN AGE_IN_DAYS TEXT DEFAULT 'None'")
        print(f"🆕 Added AGE_IN_DAYS to {db_file}")

    # Fill with placeholders
    cursor.execute(f"SELECT ROWID, DOB FROM {TABLE_NAME}")
    rows = cursor.fetchall()

    for row_id, dob in rows:
        if dob and isinstance(dob, str) and re.match(r"\d{4}-\d{2}-\d{2}", dob):
            cursor.execute(f"UPDATE {TABLE_NAME} SET AGE_IN_DAYS = '1' WHERE ROWID = ?", (row_id,))
        else:
            cursor.execute(f"UPDATE {TABLE_NAME} SET AGE_IN_DAYS = 'None' WHERE ROWID = ?", (row_id,))

    conn.commit()
    conn.close()
    print(f"✅ AGE_IN_DAYS initialized for {db_file}")

def main():
    for db_file in DB_FILES:
        add_age_column_to_db(db_file)

if __name__ == "__main__":
    main()
