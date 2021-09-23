""" Authors of your next scientific article """

import os
from yaml import load, FullLoader
import sqlite3
# import pyperclip

here = os.path.dirname(os.path.abspath(__file__))
DBFILE = os.path.join(here, 'authors_institutes.db')


def substr_in_list(sub, lst):
    for i, item in enumerate(lst):
        if sub in item:
            return True, i
    return False, None


def _load_connection(conn, db):
    creating_connection = conn is None
    if creating_connection:
        conn = sqlite3.connect(db)
    return conn, creating_connection


def register_author(author_name, institute_address, conn=None, db=DBFILE):
    conn, created_connection = _load_connection(conn, db)

    author_name = author_name.replace("'", "''")
    institute_address = institute_address.replace("'", "''")

    try:
        result = conn.execute('SELECT * FROM institutes '
                              f"WHERE institute_address='{institute_address}'")
        if len(result.fetchall()) == 0:
            conn.executescript("INSERT OR IGNORE INTO institutes "
                               "(institute_address) "
                               f"VALUES('{institute_address}');")
    except Exception as e:
        raise e

    try:
        result = conn.execute('SELECT * FROM author '
                              f"WHERE author_name='{author_name}'")
        if len(result.fetchall()) == 0:
            conn.executescript("INSERT OR IGNORE INTO author "
                               "(author_name) "
                               f"VALUES('{author_name}');")
    except Exception as e:
        raise e

    try:
        conn.executescript("INSERT OR IGNORE INTO author_institutes "
                           "(author_name, institute_address) "
                           f"VALUES('{author_name}', '{institute_address}');")
    except Exception as e:
        print(e)
        print(author_name, institute_address)

    conn.commit()
    print('Record created successfully!')

    if created_connection:
        conn.close()


def register_authors(author_names, institute_addresses, conn=None, db=DBFILE):
    conn, created_connection = _load_connection(conn, db)
    for author, institute in zip(author_names, institute_addresses):
        conn.executescript("INSERT OR IGNORE INTO author_institutes "
                           "(author_name, institute_address) "
                           f"VALUES('{author}', '{institute}');")
    conn.commit()
    print('Records created successfully!')
    if created_connection:
        conn.close()


def query_author(author_name, conn=None, db=DBFILE):
    conn, created_connection = _load_connection(conn, db)
    author_name = author_name.replace("'", "''")
    cursor = conn.execute("SELECT * FROM author_institutes "
                          f"WHERE author_name LIKE '%{author_name}%'")
    result = list(cursor)
    if created_connection:
        conn.close()
    return result


def query_institute(institute_address, conn=None, db=DBFILE):
    conn, created_connection = _load_connection(conn, db)
    institute_address = institute_address.replace("'", "''")
    cursor = conn.execute(
        "SELECT * FROM institutes "
        f"WHERE institute_address LIKE '%{institute_address}%'")
    result = list(cursor)
    if created_connection:
        conn.close()
    return result


def change_author(old_name, new_name=None, new_institute=None, conn=None,
                  db=DBFILE):
    if new_name is None and new_institute is None:  # nothing to do
        print('change_author: '
              'both new_name and new_institute are None, nothing to do')
        return

    conn, created_connection = _load_connection(conn, db)
    r = query_author(old_name, conn)
    if len(r) == 0:
        answer = input(f'Author "{old_name}" not found. Register? (Y/n) ')
        if answer.lower() != 'n':
            register_author(new_name, new_institute, conn)
    elif len(r) > 1:
        print(f'Found several authors that match "{old_name}": ')
        print([a[1] for a in r])
    else:
        r = r[0]
        print(f'Found author {r[1]}')
        print(f'at institute {r[2]}')
        if new_name is None:  # changing institute
            print(f'changing institute to {new_institute}')
            register_author(r[1], new_institute, conn)
        elif new_institute is None:  # changing name
            print(f'changing name to {new_name}')
            register_author(new_name, r[2], conn)
        else:  # changing both
            print(f'changing institute to {new_institute} \n'
                  f'and name to {new_name}')
            register_author(new_name, new_institute, conn)


class Authors:
    def __init__(self, load_from, conn=None, db=DBFILE):
        A = list(map(str.strip, open(load_from).readlines()))
        self.all_authors = [a for a in A if a != '']
        self.last_names = [a.split('.')[-1].strip() for a in A if a != '']
        self.first_author = self.all_authors[0]

        self.conn = conn
        if conn is None:
            self.conn = sqlite3.connect(db)

        self.warn_unknown_authors()

    def warn_unknown_authors(self):
        self.known = []
        for author in self.all_authors:
            q = query_author(author, conn=self.conn)
            if len(q) == 0:
                print(f'Cannot find "{author}" in list of known authors!')
                self.known.append(False)
            else:
                self.known.append(True)

    def AandA(self, alphabetical=False, alphabetical_after=1):

        if alphabetical:
            author_list = self.all_authors[:alphabetical_after]
            known_authors = self.known[:alphabetical_after]

            # argsort
            def argsort(seq):
                return sorted(range(len(seq)), key=seq.__getitem__)

            sauthors = argsort(self.last_names[alphabetical_after:])
            for i in sauthors:
                author_list.append(self.all_authors[alphabetical_after:][i])

            # author_list += sorted(self.all_authors[alphabetical_after:])
            for i in sauthors:
                known_authors.append(self.known[alphabetical_after:][i])

        else:
            author_list = self.all_authors
            known_authors = self.known


        institutes_in_list = []
        labels = []
        # print the authors first
        print(r'\author{')
        for i, author in enumerate(author_list):
            if known_authors[i]:
                query = query_author(author, conn=self.conn)
                name = query[0][1]
                institutes = [q[2] for q in query]

                # don't line-break people's names, it's not polite
                name = name.replace(' ', '~')

                print(f'  {name}', end=' ')
                numbers = []
                print(r'\inst{', end='')

                for j, institute in enumerate(institutes):
                    label = query_institute(institute, conn=self.conn)[0][2]

                    if institute not in institutes_in_list:
                        institutes_in_list.append(institute)
                        labels.append(label)
                    numbers.append(institutes_in_list.index(institute) + 1)

                    end = ', ' if j < (len(institutes) - 1) else ''
                    if label is None:
                        print(f'{numbers[-1]}', end=end)
                    else:
                        print(f'\\ref{{{label}}}', end=end)


                print(r'}', end=' ')

            else:
                print(f'  {author}', end=' ')
                print(r'\inst{unknown}', end=' ')

            if i < (len(self.all_authors) - 1):
                print(r'\and')

        print(r'}')

        # then print the institutes
        print(r'\institute{')
        for institute, label in zip(institutes_in_list, labels):
            print(f'  {institute}', end=' ')
            if label is not None:
                print(f'\label{{{label}}}', end=' ')
            if institute == institutes_in_list[-1]:
                print()
            else:
                print(r'\and')
        print(r'}')
