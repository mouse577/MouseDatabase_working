import os
from database_manager import initialize_database, ROOM_428_DB_FILE, EUTHANIZED_DB_FILE, ROOM_203B_DB_FILE, BREEDERS_DB_FILE, NR1_DB_FILE, load_csv_to_dataframe, save_dataframe_to_sqlite, create_empty_database
from gui import run_gui

# Ensure the CSV file is in the correct location
CSV_FILE = "PPL_Scholl_428_MouseList.csv"
DB_FILE = "PPL_Scholl_428_MouseDatabase.db"  # Define database file

if __name__ == "__main__":
    # ✅ Initialize all databases on startup
    for db_file in [ROOM_428_DB_FILE, EUTHANIZED_DB_FILE, ROOM_203B_DB_FILE, BREEDERS_DB_FILE, NR1_DB_FILE]:
        print(f"🔍 Initializing database: {db_file}")
        initialize_database(db_file)

    # ✅ Ensure every database has the `mouse_list` table
    for db_file in [ROOM_428_DB_FILE, EUTHANIZED_DB_FILE, ROOM_203B_DB_FILE, BREEDERS_DB_FILE, NR1_DB_FILE]:
        initialize_database(db_file)  # ✅ Creates `mouse_list` if missing

    # ✅ Initialize ROOM_428 and import data from CSV
    initialize_database(ROOM_428_DB_FILE)

    if os.path.exists(CSV_FILE):
        try:
            df = load_csv_to_dataframe(CSV_FILE)
            save_dataframe_to_sqlite(df, ROOM_428_DB_FILE)  # ✅ Import only into ROOM_428
            print("✅ CSV data successfully loaded into ROOM_428 database.")
        except Exception as e:
            print(f"⚠️ Error loading CSV: {e}. Starting ROOM_428 with an empty database.")
    else:
        print(f"⚠️ CSV file not found: {CSV_FILE}. Starting ROOM_428 with an empty database.")

    # Start the GUI
    run_gui()


