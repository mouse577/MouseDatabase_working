# Mouse Database Manager

A desktop tool for organizing mouse colony and experiment records. The project uses a PyQt5 interface and separate SQLite databases for room inventories, breeders, NR1 animals, and euthanized animals. It provides a searchable table, record editing, CSV export, and a way to move records between inventories.

## What it tracks

Each `mouse_list` record can include an animal ID, cage number, mouse line, genotype, sex, date of birth, availability, health, assigned user, manipulations, up to five experiment fields, status, and comments. The interface calculates age in days from dates of birth formatted as `YYYY-MM-DD`.

The database selector offers `ROOM_428`, `ROOM_203B`, `BREEDERS`, `NR1`, and `EUTHANIZED`. The Search button filters the selected database by an **exact mouse-line match**. The **Copy Row** action copies a selected record into another database and then deletes it from the source; it is a move, despite its label. An ID suffix is generated when a copied or newly added ID already exists in the destination.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Application entry point and GUI launcher. |
| `gui.py` | PyQt5 table, search, form, and record actions. |
| `database_manager.py` | SQLite schema and data operations; CSV import/export and age updates. |
| `add_age_column.py` | Adds `AGE_IN_DAYS` to existing databases that lack it. |
| `250424_DB_backup/` | A dated snapshot of five SQLite database files; these are not automatically loaded by the application. |

## Setup and launch

Use Python 3 with a desktop display. Install the two external Python packages:

```bash
python -m pip install pandas PyQt5
```

Run commands from the repository root so relative database and CSV paths resolve there. Launch the application:

```bash
python main.py
```

To import room 428 records, place `PPL_Scholl_428_MouseList.csv` in the repository root. The CSV is optional, and its column names should match the `mouse_list` fields. The archived `.db` files in `250424_DB_backup/` are separate from the working databases.

## Using the interface

1. Select an inventory with the database selector.
2. Use **Search** for an exact `MOUSELINE` value, or **Refresh Data** to show all records.
3. Select a row to populate the form, edit fields, and choose **Update Row**; use **Add Record** for a new animal.
4. Use **Export to CSV** to save the selected inventory's records.
5. Use **Copy Row** to move an animal to another inventory. Check the destination after the move, especially when the animal ID already exists there.

