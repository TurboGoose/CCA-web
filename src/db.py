import sqlite3

from consts import DATABASE_FILE


def create_tables():
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS datasets(name TEXT primary key);")
    cur.execute("""CREATE TABLE IF NOT EXISTS labels (
        dataset_name TEXT REFERENCES datasets(name),
        name TEXT NOT NULL,
        PRIMARY KEY (dataset_name, name)
    );
    """)

    con.commit()
    con.close()


def add_dataset_to_db(dataset: str):
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"INSERT INTO datasets (name) VALUES ('{dataset}');")
    con.commit()
    con.close()


def add_label_for_dataset(label: str, dataset: str):
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"INSERT INTO labels (name, dataset_name) VALUES ('{label}', '{dataset}');")
    con.commit()
    con.close()


def get_datasets():
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"SELECT name FROM datasets;")
    result = [ds[0] for ds in cur.fetchall()]
    con.commit()
    con.close()
    return result


def get_labels_for_dataset(dataset: str):
    con = sqlite3.connect(DATABASE_FILE)
    cur = con.cursor()
    cur.execute(f"SELECT name FROM labels WHERE dataset_name='{dataset}';")
    result = [label[0] for label in cur.fetchall()]
    con.commit()
    con.close()
    return result
