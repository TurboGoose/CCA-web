import sqlite3

from consts import DATABASE_FILE


def create_tables() -> None:
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS datasets(name TEXT PRIMARY KEY ON UPDATE CASCADE ON DELETE CASCADE);")
    cur.execute("""CREATE TABLE IF NOT EXISTS labels (
        dataset_name TEXT REFERENCES datasets(name),
        name TEXT NOT NULL,
        PRIMARY KEY (dataset_name, name)
    );
    """)

    con.commit()
    con.close()


def save_dataset(dataset: str) -> None:
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"INSERT INTO datasets (name) VALUES ('{dataset}');")
    con.commit()
    con.close()


def get_datasets() -> list[str]:
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"SELECT name FROM datasets;")
    result = [ds[0] for ds in cur.fetchall()]
    con.commit()
    con.close()
    return result


def rename_dataset(old_dataset_name: str, new_dataset_name: str):
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"UPDATE datasets SET name='{new_dataset_name}' WHERE name='{old_dataset_name}';")
    con.commit()
    con.close()


def delete_dataset(dataset: str) -> None:
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"DELETE FROM datasets WHERE name='{dataset}';")
    con.commit()
    con.close()


def save_label_for_dataset(label: str, dataset: str) -> None:
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"INSERT INTO labels (name, dataset_name) VALUES ('{label}', '{dataset}');")
    con.commit()
    con.close()


def get_labels_for_dataset(dataset: str) -> list[str]:
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"SELECT name FROM labels WHERE dataset_name='{dataset}';")
    result = [label[0] for label in cur.fetchall()]
    con.commit()
    con.close()
    return result


def rename_label_for_dataset(dataset: str, old_label_name: str, new_label_name: str) -> None:
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"UPDATE labels SET name='{new_label_name}' WHERE dataset_name='{dataset}' AND name='{old_label_name}';")
    con.commit()
    con.close()


def delete_label_for_dataset(label: str, dataset: str) -> None:
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"DELETE FROM labels WHERE dataset_name='{dataset}' AND name='{label}';")
    con.commit()
    con.close()
