import sqlite3
import pandas as pd
from datetime import datetime

# Database file paths
ROOM_428_DB_FILE = "ROOM_428.db"
EUTHANIZED_DB_FILE = "EUTHANIZED.db"
ROOM_203B_DB_FILE = "ROOM_203B.db"
NR1_DB_FILE = "NR1.db"
BREEDERS_DB_FILE = "BREEDERS.db"
TABLE_NAME = "mouse_list"  # Keep the same table name for consistency

# Column names (ensures consistency across functions)
COLUMN_NAMES = [
    "ID_TATOO_NT", "CAGE_NUM", "MOUSELINE", "GENOTYPE", "GENDER",
    "DOB", "AVAILABLE", "HEALTH", "USER_NAME", "MANIPULATIONS",
    "EXPERIMENT_1", "EXPERIMENT_2", "EXPERIMENT_3", "EXPERIMENT_4", "EXPERIMENT_5",
    "STATUS", "COMMENTS"
]

# ----------------- DATABASE INITIALIZATION -----------------
def initialize_database(db_file):
    """Creates the main database table if it does not exist."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_TATOO_NT TEXT,
            CAGE_NUM INTEGER,
            MOUSELINE TEXT,
            GENOTYPE TEXT,
            GENDER TEXT,
            DOB TEXT,
            AVAILABLE TEXT,
            HEALTH TEXT,
            USER_NAME TEXT,
            MANIPULATIONS TEXT,
            EXPERIMENT_1 TEXT,
            EXPERIMENT_2 TEXT,
            EXPERIMENT_3 TEXT,
            EXPERIMENT_4 TEXT,
            EXPERIMENT_5 TEXT,
            STATUS TEXT,
            COMMENTS TEXT DEFAULT ''
        )
    """)

    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = [column[1] for column in cursor.fetchall()]

    conn.commit()
    conn.close()
    print(f"✅ Table `mouse_list` ensured in {db_file}")

def create_empty_database():
    """Creates all databases as empty if they do not exist (except ROOM_428 which is imported from CSV)."""
    for db_file in [EUTHANIZED_DB_FILE, ROOM_203B_DB_FILE, BREEDERS_DB_FILE, NR1_DB_FILE]:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_TATOO_NT TEXT,
                CAGE_NUM INTEGER,
                MOUSELINE TEXT,
                GENOTYPE TEXT,
                GENDER TEXT,
                DOB TEXT,
                AVAILABLE TEXT,
                HEALTH TEXT,
                USER_NAME TEXT,
                MANIPULATIONS TEXT,
                EXPERIMENT_1 TEXT,
                EXPERIMENT_2 TEXT,
                EXPERIMENT_3 TEXT,
                EXPERIMENT_4 TEXT,
                EXPERIMENT_5 TEXT,
                STATUS TEXT,
                COMMENTS TEXT DEFAULT ''
            )
        """)
        conn.commit()
        conn.close()




def load_csv_to_dataframe(csv_file):
    """Loads a CSV file into a pandas DataFrame."""
    return pd.read_csv(csv_file)

def save_dataframe_to_sqlite(df, db_file, table_name="mouse_list"):
    """Saves a DataFrame to an SQLite database."""
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()


# ----------------- DATA MANAGEMENT FUNCTIONS -----------------
def fetch_data(db_file):
    """Fetches all data from the specified SQLite database, excluding INDEX_ID."""
    print(f"🔍 Fetching data from {db_file}")
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS, AVAILABLE, HEALTH, USER_NAME, MANIPULATIONS, EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3, EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS FROM {TABLE_NAME}", conn)
    conn.close()
    return df

def filter_records(db_file, column, value):
    """Filters records based on a column value in the specified database."""
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS, AVAILABLE, HEALTH, USER_NAME, MANIPULATIONS, EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3, EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS FROM {TABLE_NAME} WHERE {column} = ?", conn, params=(value,))
    conn.close()
    return df

def export_to_csv(db_file, csv_filename):
    """Exports the table to a CSV file from the specified database, excluding INDEX_ID."""
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f"SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS, AVAILABLE, HEALTH, USER_NAME, MANIPULATIONS, EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3, EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS FROM {TABLE_NAME}", conn)
    df.to_csv(csv_filename, index=False)
    conn.close()

# ----------------- RECORD OPERATIONS -----------------
def insert_record(db_file, id_tatoo_nt, cage_num, mouseline, genotype, gender, dob, available, health, user_name,
                  manipulations, experiment_1, experiment_2, experiment_3, experiment_4, experiment_5, status, comments):
    """Inserts a new record, modifying ID_TATOO_NT if it already exists."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    base_id = id_tatoo_nt
    cursor.execute(f"SELECT ID_TATOO_NT FROM {TABLE_NAME} WHERE ID_TATOO_NT LIKE ?", (f"{base_id}%",))
    existing_ids = {row[0] for row in cursor.fetchall()}
    print(f"🧪 Existing IDs for base {base_id}: {existing_ids}")  # <- DEBUG LINE

    if base_id in existing_ids:
        def generate_suffix(n):
            result = ""
            while n > 0:
                n, rem = divmod(n - 1, 26)
                result = chr(97 + rem) + result
            return result

        i = 1
        while True:
            candidate = f"{base_id}{generate_suffix(i)}"
            if candidate not in existing_ids:
                id_tatoo_nt = candidate
                break
            i += 1

    cursor.execute(f"""
        INSERT INTO {TABLE_NAME} (
            ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB,
            AVAILABLE, HEALTH, USER_NAME, MANIPULATIONS,
            EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3, EXPERIMENT_4, EXPERIMENT_5,
            STATUS, COMMENTS
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_tatoo_nt, cage_num, mouseline, genotype, gender, dob, available, health, user_name,
          manipulations, experiment_1, experiment_2, experiment_3, experiment_4, experiment_5,
          status, comments))

    conn.commit()
    conn.close()

    if id_tatoo_nt != base_id:
        print(f"✅ ID changed from {base_id} to {id_tatoo_nt}")
        return id_tatoo_nt
    else:
        return None




def update_record(db_file, index_id, cage_num, mouseline, genotype, gender, dob, available, health, user_name, manipulations, experiment_1, experiment_2, experiment_3, experiment_4, experiment_5, status, comments, table_name="mouse_list"):
    """Updates an existing record using ID_TATOO_NT as the unique identifier, including COMMENTS."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # ✅ Use the `index_id` that was already passed as an argument
    if not index_id:
        return False  # If index_id is missing, fail early

    cursor.execute(f"""
        UPDATE {table_name}
        SET CAGE_NUM = ?, MOUSELINE = ?, GENOTYPE = ?, GENDER = ?, DOB = ?, AVAILABLE = ?, HEALTH = ?, USER_NAME = ?, MANIPULATIONS = ?, EXPERIMENT_1 = ?, EXPERIMENT_2 = ?,EXPERIMENT_3 = ?, EXPERIMENT_4 = ?, EXPERIMENT_5 = ?, STATUS = ?, COMMENTS = ?
        WHERE INDEX_ID = ?
    """, (cage_num, mouseline, genotype, gender, dob, available, health, user_name, manipulations, experiment_1, experiment_2, experiment_3, experiment_4, experiment_5, status, comments, index_id))

    conn.commit()
    conn.close()
    return True


def delete_record(db_file, id_tatoo_nt):
    """Deletes a record from the database using ID_TATOO_NT as the unique identifier."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # ✅ Ensure ID_TATOO_NT exists before trying to delete
    cursor.execute(f"SELECT 1 FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
    if cursor.fetchone() is None:
        conn.close()
        return False  # No record found, return failure

    # ✅ Delete the record
    cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
    conn.commit()
    conn.close()

    return True  # ✅ Successfully deleted



# ----------------- ROW COPY FUNCTION -----------------
def copy_row_to_new_db(source_db, destination_db, id_tatoo_nt):
    """Copies a specific row from one database to another using ID_TATOO_NT, keeping column names explicitly listed."""
    conn_old = sqlite3.connect(source_db)
    conn_new = sqlite3.connect(destination_db)

    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()

    # ✅ Select the specific row explicitly listing all columns
    cursor_old.execute(f"""
        SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS, AVAILABLE, HEALTH, 
               USER_NAME, MANIPULATIONS, EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3, 
               EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS 
        FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?
    """, (id_tatoo_nt,))

    row = cursor_old.fetchone()

    if row:
        base_id = row[0]
        # ✅ Explicitly listing column names in the INSERT statement
        # cursor_new.execute(f"""
        #     INSERT INTO {TABLE_NAME} (
        #         ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS, AVAILABLE, HEALTH,
        #         USER_NAME, MANIPULATIONS, EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3,
        #         EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS
        #     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        # """, row)

        cursor_new.execute(f"SELECT ID_TATOO_NT FROM {TABLE_NAME} WHERE ID_TATOO_NT LIKE ?", (f"{base_id}%",))
        existing_ids = {ri[0] for ri in cursor_new.fetchall()}
        new_id = base_id
        if base_id in existing_ids:
            def generate_suffix(n):
                result = ""
                while n > 0:
                    n, rem = divmod(n - 1, 26)
                    result = chr(97 + rem) + result
                return result

            i = 1
            while True:
                candidate = f"{base_id}{generate_suffix(i)}"
                if candidate not in existing_ids:
                    new_id = candidate
                    break
                i += 1

        row = (new_id,) + row[1:]

        # ✅ Explicitly listing column names in the INSERT statement
        cursor_new.execute(f"""
            INSERT INTO {TABLE_NAME} (
                ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS, AVAILABLE, HEALTH, 
                USER_NAME, MANIPULATIONS, EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3, 
                EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)


        conn_new.commit()
        print(f"✅ Successfully copied row {id_tatoo_nt} from {source_db} to {destination_db}")

        conn_old.close()
        conn_new.close()
        return row[0] # ✅ Return new ID for confirmation

    conn_old.close()
    conn_new.close()
    return None


def add_age_column_to_all_dbs():
    """Adds AGE_IN_DAYS column to each database if it doesn't exist and initializes it."""
    db_files = [ROOM_428_DB_FILE, EUTHANIZED_DB_FILE, ROOM_203B_DB_FILE, BREEDERS_DB_FILE, NR1_DB_FILE]

    for db_file in db_files:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        existing_columns = [row[1] for row in cursor.fetchall()]
        if "AGE_IN_DAYS" not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN AGE_IN_DAYS TEXT DEFAULT 'None'")
            print(f"✅ Added AGE_IN_DAYS to {db_file}")

        # Update placeholder values
        cursor.execute(f"SELECT ROWID, DOB FROM {TABLE_NAME}")
        rows = cursor.fetchall()

        for row_id, dob in rows:
            if dob and isinstance(dob, str) and re.match(r"\d{4}-\d{2}-\d{2}", dob):
                cursor.execute(f"UPDATE {TABLE_NAME} SET AGE_IN_DAYS = '1' WHERE ROWID = ?", (row_id,))
            else:
                cursor.execute(f"UPDATE {TABLE_NAME} SET AGE_IN_DAYS = 'None' WHERE ROWID = ?", (row_id,))

        conn.commit()
        conn.close()


def update_age_in_days(db_file, table_name="mouse_list"):
    """Updates AGE_IN_DAYS for all rows based on DOB and current date in the specified table."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(f"SELECT ROWID, DOB FROM {table_name}")
    rows = cursor.fetchall()

    for row_id, dob in rows:
        try:
            if dob and dob.lower() != "none":
                dob_date = datetime.strptime(dob, "%Y-%m-%d")
                age_days = (datetime.now() - dob_date).days
                cursor.execute(f"UPDATE {table_name} SET AGE_IN_DAYS = ? WHERE ROWID = ?", (str(age_days), row_id))
            else:
                cursor.execute(f"UPDATE {table_name} SET AGE_IN_DAYS = 'None' WHERE ROWID = ?", (row_id,))
        except Exception as e:
            print(f"⚠️ Skipped row {row_id} in table {table_name} due to invalid DOB: {dob}")

    conn.commit()
    conn.close()



def get_all_tables(db_file):
    """Returns a list of table names in the given database."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]
    conn.close()
    return tables

def create_new_table(db_file, new_table_name):
    """Creates a new table in the selected database with the same schema as mouse_list."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {new_table_name} (
            INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_TATOO_NT TEXT,
            CAGE_NUM INTEGER,
            MOUSELINE TEXT,
            GENOTYPE TEXT,
            GENDER TEXT,
            DOB TEXT,
            AGE_IN_DAYS TEXT,
            AVAILABLE TEXT,
            HEALTH TEXT,
            USER_NAME TEXT,
            MANIPULATIONS TEXT,
            EXPERIMENT_1 TEXT,
            EXPERIMENT_2 TEXT,
            EXPERIMENT_3 TEXT,
            EXPERIMENT_4 TEXT,
            EXPERIMENT_5 TEXT,
            STATUS TEXT,
            COMMENTS TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()












