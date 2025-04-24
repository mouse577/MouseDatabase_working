import sys
import sqlite3
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, \
    QLineEdit, QLabel, QFileDialog, QHBoxLayout, QMessageBox, QComboBox, QInputDialog, QGridLayout
from database_manager import (
    fetch_data, filter_records, export_to_csv, insert_record, delete_record,
    update_record, copy_row_to_new_db, create_empty_database, update_age_in_days, TABLE_NAME,
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

        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(self.fill_update_fields)
        self.table.setSortingEnabled(True)  # ✅ ENABLE SORTING
        self.layout.addWidget(self.table)

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

        self.layout.addLayout(button_layout_2)  # ✅ Buttons at bottom

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
        update_age_in_days(self.current_db)
        self.load_data()

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
        if selected_index in db_map:
            self.current_db = db_map[selected_index]
        else:
            QMessageBox.warning(self, "Error", "Invalid database selection.")
            return
        update_age_in_days(self.current_db)
        self.load_data()  # ✅ Reload table with the newly selected database

    def load_data(self):
        """Loads data from the selected SQLite database into the table."""
        self.table.setSortingEnabled(False)
        print(f"🔍 GUI loading data from {self.current_db}")
        df = fetch_data(self.current_db)
        if df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
        else:
            self.populate_table(df)

        self.table.setSortingEnabled(True)
        return

        self.populate_table(df)

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

        # #  new code to auto delete row after copying
        # deleted = delete_record(source_db, record_id)
        # if deleted:
        #     QMessageBox.information(self, "Success", f"Row {record_id} moved from {source_db} to {destination_db}.")
        #     self.load_data()
        # else:
        #     QMessageBox.warning(self, "Warning", f"Row was copied but could not be deleted from {source_db}.")
        #
        # # QMessageBox.information(self, "Success", f"Row {record_id} copied from {source_db} to {destination_db}.")

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
        cursor.execute(f"SELECT INDEX_ID FROM {TABLE_NAME} WHERE ID_TATOO_NT = ?", (id_tatoo_nt,))
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

        success = update_record(self.current_db, index_id, *values)


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

            # ✅ Call delete_record() with ID_TATOO_NT
            success = delete_record(self.current_db, id_tatoo_nt)

            if success:
                self.load_data()  # Refresh UI after deletion
                QMessageBox.information(self, "Success", f"Record {id_tatoo_nt} deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Record not found or could not be deleted.")
        else:
            QMessageBox.warning(self, "Selection Error", "Please select a record to delete.")


def run_gui():
    create_empty_database()  # Ensure the new database is created before GUI starts
    app = QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_gui()








