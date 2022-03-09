import os
import sqlite3

here = os.path.dirname(os.path.abspath(__file__))
DBFILE = os.path.join(here, 'authors_institutes.db')


def _load_connection(conn, db):
    creating_connection = conn is None
    if creating_connection:
        conn = sqlite3.connect(db)
    return conn, creating_connection


def get_tables(db, conn=None):
    conn, created_connection = _load_connection(conn, db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [record[0] for record in cursor.fetchall()[1:]]
    if created_connection:
        conn.close()
    return tables


def get_columns(db, table, conn=None):
    conn, created_connection = _load_connection(conn, db)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    columns = [record[0] for record in cursor.description]
    if created_connection:
        conn.close()
    return columns


def create_database(db):
    conn, created_connection = _load_connection(None, db)

    sql1 = """
    CREATE TABLE IF NOT EXISTS authors (
        author_id INTEGER PRIMARY KEY,
        author_name TEXT UNIQUE NOT NULL,
        acknow TEXT
    );"""

    sql2 = """
    CREATE TABLE IF NOT EXISTS institutes (
        institute_id INTEGER PRIMARY KEY,
        institute_address TEXT UNIQUE NOT NULL,
        label TEXT
    );
    """

    sql3 = """
    CREATE TABLE IF NOT EXISTS authors_institutes (
        id INTEGER PRIMARY KEY,
        author_name INTEGER REFERENCES authors(author_name),
        institute_address INTEGER REFERENCES institutes(institute_address),
        UNIQUE(author_name, institute_address)
    );
    """

    for sql in (sql1, sql2, sql3):
        try:
            conn.execute(sql)
        except Exception as e:
            raise e

    if created_connection:
        conn.close()


def has_required_tables(db):
    tables = get_tables(db)
    has_tables = (
        'author' in tables,
        'institutes' in tables,
        'author_institutes' in tables,
    )
    return all(has_tables)


def check_database(db):
    if not has_required_tables(db):
        create_database(db)


def find_similar_institutes(db, threshold=0.7, interactive_replace=False):
    from collections import defaultdict
    from difflib import SequenceMatcher
    from .authors import query_institute

    conn, created_connection = _load_connection(None, db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM institutes")
    institutes = [row[1] for row in cursor.fetchall()]

    def similar(a, b):
        return SequenceMatcher(None, a, b).ratio()

    similarities = defaultdict(list)
    for i, institute in enumerate(institutes):
        others = institutes[i + 1:]
        # others = [x for j, x in enumerate(institutes) if j != i]
        for other in others:
            if similar(institute, other) > threshold:
                similarities[institute].append(other)

    if created_connection:
        conn.close()

    if interactive_replace:
        for k, sim in similarities.items():
            print(f'1 - {k}')
            for i, s in enumerate(sim, start=2):
                print(f'{i} - {s}')
            print('  ', 'a) replace 1 with 2')
            print('  ', 'b) replace 2 with 1')
            print('  ', 'c) ignore')
            option = input('   your option: ')
            if option == 'a':
                print(f'replacing\n  {k}\nwith\n  {s}')
            elif option == 'b':
                print(f'replacing\n  {s}\nwith\n  {k}')
            else:
                print('ignoring')

            print()
    else:
        for k, sim in similarities.items():
            print(k)
            print('seems similar to')
            for s in sim:
                print('  ', s)
            print()

    return similarities
