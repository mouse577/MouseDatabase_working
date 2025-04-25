import sys
import sqlite3
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, \
    QLineEdit, QLabel, QFileDialog, QHBoxLayout, QMessageBox, QComboBox, QInputDialog, QGridLayout
from database_manager import (
    fetch_data, filter_records, export_to_csv, insert_record, delete_record,
    update_record, copy_row_to_new_db, create_empty_database, update_age_in_days, get_all_tables, TABLE_NAME,
    ROOM_428_DB_FILE, EUTHANIZED_DB_FILE, ROOM_203B_DB_FILE, BREEDERS_DB_FILE, NR1_DB_FILE
)

# Database file paths
DB_FILE = "PPL_Scholl_428_MouseDatabase.db"
NEW_DB_FILE = "PPL_Scholl_428_Deceased_MouseDatabase.db"


class DatabaseApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mouse List Database Manager")
        self.setGeometry(100, 100, 900, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Database selection
        self.db_label = QLabel("Select Database:")
        self.layout.addWidget(self.db_label)

        self.db_selector = QComboBox()
        self.db_selector.addItems(["ROOM_428", "EUTHANIZED", "ROOM_203B", "BREEDERS", "NR1"])
        self.db_selector.currentIndexChanged.connect(self.switch_database)
        self.layout.addWidget(self.db_selector)
        print("🧩 1. Database selector created")

        # Table selector
        self.table_selector = QComboBox()
        self.table_selector.currentIndexChanged.connect(self.switch_table)
        self.layout.addWidget(QLabel("Select Table:"))
        self.layout.addWidget(self.table_selector)
        print("🧩 2. Table selector created")


        # Search Bar
        search_layout = QHBoxLayout()  # ✅ Make search layout horizontal to save space
        self.search_label = QLabel("Search:")
        search_layout.addWidget(self.search_label)

        self.search_input = QLineEdit()
        self.search_input.setFixedWidth(200)  # ✅ Reduce width of search bar
        search_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.setFixedHeight(25)  # ✅ Reduce button height
        self.search_button.clicked.connect(self.search_data)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)
        print("🧩 3. Search bar created")

        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.fill_update_fields)
        self.table.setSortingEnabled(True)  # ✅ ENABLE SORTING
        self.layout.addWidget(self.table)
        print("🧩 4. Table widget created")

        # Buttons Layout
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.setFixedHeight(25)  # ✅ Reduce button height
        self.refresh_button.clicked.connect(self.load_data)
        button_layout.addWidget(self.refresh_button)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.setFixedHeight(25)
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_button)

        self.copy_button = QPushButton("Copy Row")
        self.copy_button.setFixedHeight(25)
        self.copy_button.clicked.connect(self.copy_selected_row)
        button_layout.addWidget(self.copy_button)

        self.layout.addLayout(button_layout)
        print("🧩 5. First row of buttons created")

        # ✅ Compact Form Layout for Input Fields
        self.fields = {}
        form_layout = QGridLayout()  # ✅ Use a grid to fit more inputs in less space

        labels = ["ID_TATOO_NT", "CAGE_NUM", "MOUSELINE", "GENOTYPE", "GENDER", "DOB", "AVAILABLE", "HEALTH",
                  "USER_NAME", "MANIPULATIONS", "EXPERIMENT_1", "EXPERIMENT_2", "EXPERIMENT_3",
                  "EXPERIMENT_4", "EXPERIMENT_5", "STATUS", "COMMENTS"]

        row, col = 0, 0  # ✅ Track row/col for grid positioning
        for label in labels:
            field_label = QLabel(label)  # ✅ Create a label with full column name
            form_layout.addWidget(field_label, row * 2, col)  # ✅ Place label in the row above

            field_input = QLineEdit()
            field_input.setFixedWidth(200)  # ✅ Keep width at 200px
            field_input.setFixedHeight(20)

            field_input.setPlaceholderText(label)  # ✅ Full column name as placeholder
            field_input.setToolTip(label)  # ✅ Tooltip shows full name on hover

            self.fields[label] = field_input
            form_layout.addWidget(field_input, row * 2 + 1, col)  # ✅ Place input field below label

            col += 1
            if col > 4:  # ✅ Move to next column after 5 per row
                col = 0
                row += 1

        self.layout.addLayout(form_layout)  # ✅ Add compact input fields at bottom
        print("🧩 6. Form fields created")

        # ✅ Compact Button Layout
        button_layout_2 = QHBoxLayout()

        self.add_button = QPushButton("Add Record")
        self.add_button.setFixedHeight(25)
        self.add_button.clicked.connect(self.add_record)
        button_layout_2.addWidget(self.add_button)

        self.update_button = QPushButton("Update Row")
        self.update_button.setFixedHeight(25)
        self.update_button.clicked.connect(self.update_selected_row)
        button_layout_2.addWidget(self.update_button)

        self.delete_button = QPushButton("Delete Row")
        self.delete_button.setFixedHeight(25)
        self.delete_button.clicked.connect(self.delete_selected_record)
        button_layout_2.addWidget(self.delete_button)

        self.new_table_button = QPushButton("New Table")
        self.new_table_button.setFixedHeight(25)
        self.new_table_button.clicked.connect(self.create_new_table)
        button_layout_2.addWidget(self.new_table_button)

        self.copy_to_table_button = QPushButton("Copy Record to Table")
        self.copy_to_table_button.setFixedHeight(25)
        self.copy_to_table_button.clicked.connect(self.copy_to_selected_table)
        button_layout_2.addWidget(self.copy_to_table_button)
        print("🧩 7. Second row of buttons created")

        self.delete_table_button = QPushButton("Delete Table")
        self.delete_table_button.setFixedHeight(25)
        self.delete_table_button.clicked.connect(self.delete_selected_table)
        button_layout_2.addWidget(self.delete_table_button)
        print("🧩 7. Second row of buttons created")


        self.layout.addLayout(button_layout_2)  # ✅ Buttons at bottom
        self.layout.addWidget(QLabel("✅ Button section loaded"))


        # Load data on startup
        db_map = {
            0: ROOM_428_DB_FILE,
            1: EUTHANIZED_DB_FILE,
            2: ROOM_203B_DB_FILE,
            3: BREEDERS_DB_FILE,
            4: NR1_DB_FILE
        }

        selected_index = self.db_selector.currentIndex()
        self.current_db = db_map.get(selected_index, ROOM_428_DB_FILE)
        self.refresh_table_list()
        self.current_table = TABLE_NAME

        # ✅ Only update AGE_IN_DAYS if NOT EUTHANIZED
        if "EUTHANIZED" not in self.current_db.upper():
            all_tables = get_all_tables(self.current_db)
            for table in all_tables:
                try:
                    update_age_in_days(self.current_db, table_name=table)
                except Exception as e:
                    print(f"⚠️ Skipped AGE_IN_DAYS update for table '{table}': {e}")
        else:
            print("⏸️ Skipped AGE_IN_DAYS update for EUTHANIZED.db")

        self.load_data()
        print("🧩 8. Refresh table list + load data")

    
    def switch_database(self):
        """Switches between the available databases and reloads data."""
        db_map = {
            0: ROOM_428_DB_FILE,
            1: EUTHANIZED_DB_FILE,
            2: ROOM_203B_DB_FILE,
            3: BREEDERS_DB_FILE,
            4: NR1_DB_FILE
        }

        selected_index = self.db_selector.currentIndex()
        if selected_index not in db_map:
            QMessageBox.warning(self, "Error", "Invalid database selection.")
            return

        self.current_db = db_map[selected_index]
        self.refresh_table_list()
        self.current_table = self.table_selector.currentText()

        if not self.current_table:
            QMessageBox.warning(self, "No Table Selected", "Could not determine a valid table to load.")
            return

        print(f"🧪 Tables in DB: {get_all_tables(self.current_db)}")
        print(f"🧪 Current table dropdown: '{self.table_selector.currentText()}'")

        update_age_in_days(self.current_db, table_name=self.current_table)
        self.load_data()


    
    def load_data(self):
        self.table.setSortingEnabled(False)
        print(f"🔍 GUI loading data from {self.current_db}, table {self.current_table}")
        
        if not self.current_table:
            QMessageBox.warning(self, "Load Error", "No table selected.")
            return

        try:
            conn = sqlite3.connect(self.current_db)
            df = pd.read_sql_query(f"""
                SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS,
                    AVAILABLE, HEALTH, USER_NAME, MANIPULATIONS, EXPERIMENT_1, EXPERIMENT_2,
                    EXPERIMENT_3, EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS
                FROM {self.current_table}
            """, conn)
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Could not load table: {e}")
            return

        if df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
        else:
            self.populate_table(df)

        self.table.setSortingEnabled(True)



    def search_data(self):
        """Filters data based on search input in the selected database."""
        mouseline = self.search_input.text()
        df = filter_records(self.current_db, "MOUSELINE", mouseline)
        self.populate_table(df)

    def export_data(self):
        """Exports the table to a CSV file."""
        filename, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if filename:
            export_to_csv(self.current_db, filename)

    def populate_table(self, df):
        """Populates the table widget with DataFrame data (excluding INDEX_ID)."""
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])  # ✅ Exclude INDEX_ID
        self.table.setHorizontalHeaderLabels(df.columns)

        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))

                column_name = df.columns[col_idx]

                if column_name == "COMMENTS":
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                if column_name == "AGE_IN_DAYS":
                    item.setToolTip("Calculated automatically from DOB on GUI load")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Optional: make read-only in table

                self.table.setItem(row_idx, col_idx, item)

            # Optional column width control
            if "COMMENTS" in df.columns:
                self.table.setColumnWidth(df.columns.get_loc("COMMENTS"), 400)
            if "AGE_IN_DAYS" in df.columns:
                self.table.setColumnWidth(df.columns.get_loc("AGE_IN_DAYS"), 120)

    def copy_selected_row(self):
        """Copies the selected row to another database and updates the UI."""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a row to copy.")
            return

        record_id = self.table.item(selected, 0).text()

        # ✅ Prompt user to select the destination database
        dest_db, ok = QInputDialog.getItem(self, "Select Destination Database",
                                           "Choose the database to copy to:",
                                           ["ROOM_428", "EUTHANIZED", "ROOM_203B", "BREEDERS", "NR1"],
                                           0, False)

        if not ok:  # User canceled
            return

        # ✅ Database file mapping
        db_map = {
            "ROOM_428": ROOM_428_DB_FILE,
            "EUTHANIZED": EUTHANIZED_DB_FILE,
            "ROOM_203B": ROOM_203B_DB_FILE,
            "BREEDERS": BREEDERS_DB_FILE,
            "NR1": NR1_DB_FILE
        }

        destination_db = db_map.get(dest_db)
        if not destination_db:
            QMessageBox.warning(self, "Error", "Invalid database selection.")
            return

        # ✅ Use the currently selected database as the source
        source_db = self.current_db

        # # ✅ Call copy function with both source and destination
        # copy_row_to_new_db(source_db, destination_db, record_id)

        new_id = copy_row_to_new_db(source_db, destination_db, record_id)
        if new_id:
            deleted = delete_record(source_db, record_id)
            msg = f"✅ Row copied to {dest_db} as '{new_id}'."
            if deleted:
                msg += f"\nOriginal ID {record_id} deleted from source."
            else:
                msg += f" ⚠️ Could not delete original ID '{record_id}'."
            QMessageBox.information(self, "Copy Complete", msg)
            self.load_data()
        else:
            QMessageBox.warning(self, "Coopy Failed", f"Could not copy row '{record_id}' unknown error or duplicate.")



    def copy_to_selected_table(self):
        """Copies the selected row from main table to a user-selected table."""
        if self.current_table != TABLE_NAME:
            QMessageBox.warning(self, "Invalid Target", "You are already in the main table. Select a different table to copy to.")
            return

        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a row to copy.")
            return

        record_id = self.table.item(selected, 0).text()

        # ✅ Fetch available tables excluding main table
        tables = get_all_tables(self.current_db)
        user_tables = [t for t in tables if t != TABLE_NAME]

        if not user_tables:
            QMessageBox.warning(self, "No Tables", "No user-created tables found.")
            return

        dest_table, ok = QInputDialog.getItem(
            self,
            "Select Target Table",
            "Choose table to copy to:",
            user_tables,
            0,
            False
        )
        if not ok:
            return  # User cancelled

        try:
            conn = sqlite3.connect(self.current_db)
            cursor = conn.cursor()

            # ✅ Duplicate check in the destination table
            cursor.execute(f"SELECT 1 FROM {dest_table} WHERE ID_TATOO_NT = ?", (record_id,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Duplicate ID", f"ID '{record_id}' already exists in table '{dest_table}'. Copy aborted.")
                conn.close()
                return

            # ✅ Fetch the row from the main table
            cursor.execute(f"""
                SELECT ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS,
                    AVAILABLE, HEALTH, USER_NAME, MANIPULATIONS,
                    EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3,
                    EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS
                FROM {TABLE_NAME}
                WHERE ID_TATOO_NT = ?
            """, (record_id,))
            row = cursor.fetchone()

            if not row:
                QMessageBox.warning(self, "Not Found", f"Could not find record '{record_id}' in main table.")
                conn.close()
                return

            # ✅ Insert into user-selected table
            cursor.execute(f"""
                INSERT INTO {dest_table} (
                    ID_TATOO_NT, CAGE_NUM, MOUSELINE, GENOTYPE, GENDER, DOB, AGE_IN_DAYS,
                    AVAILABLE, HEALTH, USER_NAME, MANIPULATIONS,
                    EXPERIMENT_1, EXPERIMENT_2, EXPERIMENT_3,
                    EXPERIMENT_4, EXPERIMENT_5, STATUS, COMMENTS
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", f"Copied record '{record_id}' to table '{dest_table}'.")
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Copy Failed", f"❌ Error copying record: {e}")




    def fill_update_fields(self):
        """Fills input fields with selected row's data for editing (ignores AGE_IN_DAYS)."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return  # No row selected

        selected_row = selected_rows[0].row()

        # Get all column names from the table
        column_names = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]

        # Map each column to the appropriate input field, skipping AGE_IN_DAYS
        field_idx = 0
        for col_idx, column_name in enumerate(column_names):
            if column_name == "AGE_IN_DAYS":
                continue  # Skip auto-calculated field

            if field_idx >= len(self.fields):
                break  # More columns than fields

            item = self.table.item(selected_row, col_idx)
            if item:
                label = list(self.fields.keys())[field_idx]
                self.fields[label].setText(item.text())

            field_idx += 1

    def update_selected_row(self):
        """Updates the selected row with new values from the input fields."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a row to update.")
            return

        selected_row = selected_rows[0].row()

        # ✅ Fetch `INDEX_ID` from database using primary key fields (e.g., ID_TATOO_NT)
        id_tatoo_nt = self.table.item(selected_row, 0).text()
        conn = sqlite3.connect(self.current_db)
        cursor = conn.cursor()
        cursor.execute(f"SELECT INDEX_ID FROM {self.current_table} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
        index_id = cursor.fetchone()

        if not index_id:
            QMessageBox.warning(self, "Error", "Could not find the record in the database.")
            conn.close()
            return

        index_id = index_id[0]  # Extract INDEX_ID
        conn.close()

        values = [self.fields[label].text() if self.fields[label].text() else "" for label in [
            "CAGE_NUM", "MOUSELINE", "GENOTYPE", "GENDER", "DOB", "AVAILABLE", "HEALTH",
            "USER_NAME", "MANIPULATIONS", "EXPERIMENT_1", "EXPERIMENT_2", "EXPERIMENT_3",
            "EXPERIMENT_4", "EXPERIMENT_5", "STATUS", "COMMENTS"
        ]]
        print(f"🔍 DEBUG: Updating record {index_id} with values: {values} (Total: {len(values)})")

        success = update_record(self.current_db, index_id, *values, table_name=self.current_table)


        if success:
            self.load_data()
            QMessageBox.information(self, "Success", "Record updated successfully.")
        else:
            QMessageBox.warning(self, "Error", "Record update failed. Check if ID_TATOO_NT exists.")

    def add_record(self):
        """Adds a new record, updating ID if duplicate exists."""
        values = [self.fields[label].text().strip() for label in self.fields]

        # Ensure the correct number of arguments (17)
        while len(values) < 17:
            values.append("")

        new_id = insert_record(self.current_db, *values)

        self.load_data()

        if new_id:
            QMessageBox.information(
                self, "ID Adjusted",
                f"ID '{values[0]}' already exists.\nNew ID for this record is '{new_id}'."
            )
            self.fields["ID_TATOO_NT"].setText(new_id)
        else:
            QMessageBox.information(self, "Success", "New record added successfully.")


    def delete_selected_record(self):
        """Deletes the selected record using ID_TATOO_NT and refreshes the UI."""
        selected = self.table.currentRow()
        if selected >= 0:
            # ✅ Fetch ID_TATOO_NT directly from table (first column)
            id_tatoo_nt = self.table.item(selected, 0).text().strip()  # Ensure no trailing spaces

            # ✅ Call delete_record() with ID_TATOO_NT in current table
            success = delete_record(self.current_db, id_tatoo_nt)

            if success:
                # ✅ Prompt user if this is a secondary table and allow optional deletion from main table
                if self.current_table != TABLE_NAME:
                    apply_to_main, ok = QInputDialog.getItem(
                        self,
                        "Apply to Main?",
                        f"Delete matching ID in main table '{TABLE_NAME}' as well?",
                        ["Yes", "No"],
                        1,
                        False
                    )
                    if ok and apply_to_main == "Yes":
                        try:
                            # ✅ Attempt deletion from main table
                            conn = sqlite3.connect(self.current_db)
                            cursor = conn.cursor()
                            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
                            conn.commit()
                            conn.close()
                            print(f"✅ Also deleted {id_tatoo_nt} from main table")
                        except Exception as e:
                            print(f"⚠️ Failed to delete from main table: {e}")

                self.load_data()  # Refresh UI after deletion
                QMessageBox.information(self, "Success", f"Record {id_tatoo_nt} deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Record not found or could not be deleted.")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a record to delete.")


    def create_new_table(self):
        """Creates a new table in the current database with the same schema as mouse_list."""
        new_table_name, ok = QInputDialog.getText(self, "New Table", "Enter name for new table:")
        if not ok or not new_table_name.strip():
            return  # User canceled or entered blank

        new_table_name = new_table_name.strip()

        try:
            conn = sqlite3.connect(self.current_db)
            cursor = conn.cursor()

            # Create table using the same schema (excluding INDEX_ID auto-increment)
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

            QMessageBox.information(self, "Table Created", f"✅ New table '{new_table_name}' created in current database.")

            # Refresh dropdown and switch to it
            self.refresh_table_list()
            self.table_selector.setCurrentText(new_table_name)
            self.current_table = new_table_name
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Could not create table: {e}")



    def refresh_table_list(self):
        tables = get_all_tables(self.current_db)

        # ✅ Filter out internal SQLite tables
        tables = [t for t in tables if not t.startswith("sqlite_")]

        self.table_selector.clear()
        self.table_selector.addItems(tables)

        # ✅ Make sure to select something valid if mouse_list exists
        if TABLE_NAME in tables:
            self.table_selector.setCurrentText(TABLE_NAME)
        elif tables:
            self.table_selector.setCurrentText(tables[0])  # fallback
        else:
            self.table_selector.setCurrentText("")  # nothing to select

        self.current_table = self.table_selector.currentText()



   
    def switch_table(self):
        selected_table = self.table_selector.currentText().strip()
        if not selected_table:
            return  # ignore empty selection
        self.current_table = selected_table
        self.load_data()



    def update_age_for_table(self, table_name):
        """Updates AGE_IN_DAYS for a specific table based on DOB."""
        try:
            conn = sqlite3.connect(self.current_db)
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
                    print(f"⚠️ Skipped row {row_id} in {table_name} due to invalid DOB: {dob}")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Failed to update AGE_IN_DAYS for table {table_name}: {e}")


    def delete_selected_table(self):
        if self.current_table == TABLE_NAME:
            QMessageBox.warning(self, "Protected Table", "You cannot delete the main table.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the table '{self.current_table}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm != QMessageBox.Yes:
            return

        apply_to_main, ok = QInputDialog.getItem(
            self,
            "Apply Changes to Main?",
            f"Do you want to update records in the main table ('{TABLE_NAME}') based on this table?",
            ["Yes", "No"],
            1,
            False
        )

        try:
            conn = sqlite3.connect(self.current_db)
            cursor = conn.cursor()

            # Optional update logic
            if ok and apply_to_main == "Yes":
                # For each record in current table, update mouse_list
                cursor.execute(f"SELECT * FROM {self.current_table}")
                rows = cursor.fetchall()
                columns = [col[1] for col in cursor.execute(f"PRAGMA table_info({self.current_table})")]

                for row in rows:
                    data = dict(zip(columns, row))
                    # Skip INDEX_ID
                    if "INDEX_ID" in data:
                        del data["INDEX_ID"]

                    set_clause = ", ".join([f"{col}=?" for col in data if col != "ID_TATOO_NT"])
                    values = [data[col] for col in data if col != "ID_TATOO_NT"]
                    values.append(data["ID_TATOO_NT"])  # For WHERE clause

                    cursor.execute(
                        f"""UPDATE {TABLE_NAME}
                            SET {set_clause}
                            WHERE ID_TATOO_NT = ?""",
                        values
                    )

            # Now delete the table
            cursor.execute(f"DROP TABLE IF EXISTS {self.current_table}")
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", f"Table '{self.current_table}' deleted successfully.")
            self.refresh_table_list()
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Delete Failed", f"❌ Could not delete table: {e}")




def run_gui():
    create_empty_database()  # Ensure the new database is created before GUI starts
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_gui()
