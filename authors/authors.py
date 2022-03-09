""" Authors of your next scientific article """

import os
import textwrap
from yaml import load, FullLoader
import sqlite3
# import pyperclip


from .database import (_load_connection, DBFILE, check_database)
from .utils import (name_to_initials, name_to_initials_last, tex_escape, tex_deescape)
from .latex_pdf_utils import preview_AandA


def register_author(author_name, institute_address, acknow=None, conn=None,
                    db=DBFILE):
    check_database(db)
    conn, created_connection = _load_connection(conn, db)

    author_name = author_name.replace("'", "''")
    institute_address = institute_address.replace("'", "''")

    try:
        result = conn.execute('SELECT * FROM institutes '
                              f"WHERE institute_address='{institute_address}'")
        if len(result.fetchall()) == 0:
            conn.executescript("INSERT INTO institutes "
                               "(institute_address) "
                               f"VALUES('{institute_address}');")
    except Exception as e:
        raise e

    try:
        result = conn.execute('SELECT * FROM authors '
                              f"WHERE author_name='{author_name}'")
        if len(result.fetchall()) == 0:
            if acknow is None:
                conn.executescript("INSERT INTO authors "
                                   "(author_name) "
                                   f"VALUES('{author_name}');")
            else:
                conn.executescript("INSERT INTO authors "
                                   "(author_name, acknow) "
                                   f"VALUES('{author_name}', '{acknow}');")
    except Exception as e:
        raise e

    try:
        conn.executescript("INSERT OR IGNORE INTO authors_institutes "
                           "(author_name, institute_address) "
                           f"VALUES('{author_name}', '{institute_address}');")
    except Exception as e:
        print(e)
        print(author_name, institute_address)

    conn.commit()

    if created_connection:
        conn.close()


# def register_authors(author_names, institute_addresses, conn=None, db=DBFILE):
#     check_database(db)
#     conn, created_connection = _load_connection(conn, db)
#     for author, institute in zip(author_names, institute_addresses):
#         conn.executescript("INSERT OR IGNORE INTO author_institutes "
#                            "(author_name, institute_address) "
#                            f"VALUES('{author}', '{institute}');")
#     conn.commit()
#     print('Records created successfully!')
#     if created_connection:
#         conn.close()


def query_author(author_name, conn=None, db=DBFILE):
    """ Query the database for an author name

    Returns two lists:
        (id1, author_name, institute_address) for all matching authors
        (id2, author_name, akcnow) for all matching authors

    """
    conn, created_connection = _load_connection(conn, db)
    author_name = author_name.replace("'", "''")
    cursor = conn.execute("SELECT * FROM authors_institutes "
                          f"WHERE author_name LIKE '%{author_name}'")
    result1 = list(cursor)

    cursor = conn.execute("SELECT * FROM authors "
                          f"WHERE author_name LIKE '%{author_name}'")
    result2 = list(cursor)

    if created_connection:
        conn.close()

    return result1, result2


def query_institute(institute_address, associated_authors=False, conn=None, 
                    db=DBFILE):
    conn, created_connection = _load_connection(conn, db)
    institute_address = institute_address.replace("'", "''")
    #
    cursor = conn.execute(
        "SELECT * FROM institutes "
        f"WHERE institute_address LIKE '%{institute_address}%'")
    result1 = list(cursor)
    #
    cursor = conn.execute(
        "SELECT * FROM authors_institutes "
        f"WHERE institute_address LIKE '%{institute_address}%'")
    result2 = list(cursor)

    if created_connection:
        conn.close()

    return result1, result2


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

        check_database(db)
        self.conn = conn
        if conn is None:
            self.conn = sqlite3.connect(db)

        self.warn_unknown_authors()

    def warn_unknown_authors(self):
        self.known = []
        for author in self.all_authors:
            q = query_author(author, conn=self.conn)[0]
            if len(q) == 0:
                print(f'Cannot find "{author}" in list of known authors!')
                self.known.append(False)
            else:
                self.known.append(True)

    def _get_author_list(self, alphabetical=False, alphabetical_after=1,
                         alphabetical_groups=None):
        if alphabetical:
            # argsort
            def argsort(seq):
                return sorted(range(len(seq)), key=seq.__getitem__)

            if alphabetical_groups is None:
                # authors which are not in alphabetical order
                author_list = self.all_authors[:alphabetical_after]
                known_authors = self.known[:alphabetical_after]

                # authors which are in alphabetical order, sorted
                sauthors = argsort(self.last_names[alphabetical_after:])
                for i in sauthors:
                    author_list.append(
                        self.all_authors[alphabetical_after:][i])
                    known_authors.append(self.known[alphabetical_after:][i])

            # sort alphabetically in groups (alphabetical_after is ignored)
            else:
                alphabetical_groups.append(len(self.all_authors))
                alphabetical_after = alphabetical_groups[0]
                # authors which are not in alphabetical order
                author_list = self.all_authors[:alphabetical_after]
                known_authors = self.known[:alphabetical_after]

                # authors which are in alphabetical order, sorted
                for g1, g2 in zip(alphabetical_groups,
                                  alphabetical_groups[1:]):
                    sauthors = argsort(self.last_names[g1:g2])
                    for i in sauthors:
                        author_list.append(self.all_authors[g1:][i])
                        known_authors.append(self.known[g1:][i])

        else:
            author_list = self.all_authors
            known_authors = self.known

        return author_list, known_authors

    def AandA(self, alphabetical=False, alphabetical_after=1,
              alphabetical_groups=None, force_initials=True, preview=False):
        """ Provide the \author and \institute LaTeX tags for A&A

        Arguments
        ---------
        alphabetical: bool
            Whether to sort author names alphabetically
        alphabetical_after: int, default 1
            Sort author names alphabetically *after* this author. By default,
            sort after the first author.
        alphabetical_groups: list, optional
            If provided, sort author names alphabetically in groups. Examples:
              [5, 10] authors 1, 2, 3, 4, 5 use order as given
                      authors 6, 7, 8, 9, 10 sorted alphabetically
                      authors 11, ... sorted alphabetically
              [3] authors 1, 2, 3 use order as given
                  authors 4, ... sorted alphabetically
                  (this would be equivalent to using alphabetical_after=3)
        force_initials: bool, default True
            If True, force the author names to be F. M. Last
        """
        author_list, known_authors = self._get_author_list(
            alphabetical, alphabetical_after, alphabetical_groups)

        institutes_in_list = []
        labels = []

        text = ''

        # print the authors first
        print(r'\author{')
        text += r'\author{' + '\n'

        for i, author in enumerate(author_list):
            if known_authors[i]:
                queryAI, queryA = query_author(author, conn=self.conn)
                name = queryA[0][1]
                institutes = [q[2] for q in queryAI]

                if force_initials:
                    name = name_to_initials_last(name)

                # don't line-break people's names, it's not polite
                name = name.replace(' ', '~')
                numbers = []

                print(f'  {name}', end=' ')
                text += f'  {name} '

                print(r'\inst{', end='')
                text += r'\inst{'

                for j, institute in enumerate(institutes):
                    inst = query_institute(institute, conn=self.conn)[0]
                    label = inst[0][2]

                    if institute not in institutes_in_list:
                        institutes_in_list.append(institute)
                        labels.append(label)
                    numbers.append(institutes_in_list.index(institute) + 1)

                    end = ', ' if j < (len(institutes) - 1) else ''
                    if label is None:
                        print(f'\\ref{{ inst{numbers[-1]} }}', end=end)
                        text += f'\\ref{{ inst{numbers[-1]} }}{end}'
                    else:
                        print(f'\\ref{{{label}}}', end=end)
                        text += f'\\ref{{{label}}}{end}'
                
                thanks = queryA[0][3]
                if thanks is not None:
                    print(rf', \thanks{{ {thanks} }}', end='')
                    text += rf', \thanks{{ {thanks} }}'

                print(r'}', end=' ')
                text += r'} '

            else:
                print(f'  {author}', end=' ')
                print(r'\inst{unknown}', end=' ')
                text += f'  {author} '
                text += r'\inst{unknown} '

            if i < (len(self.all_authors) - 1):
                print(r'\and')
                text += r'\and' + '\n'

        print(r'}')
        text += r'}' + '\n\n'

        # then print the institutes
        print(r'\institute{')
        text += r'\institute{' + '\n'

        for i, (institute, label) in enumerate(zip(institutes_in_list, labels)):
            escaped_institute = tex_escape(institute)
            print(f'  {institute}', end=' ')
            text += f'  {escaped_institute} '

            if label is None:
                print(rf'\label{{ inst{i+1} }}', end=' ')
                text += rf'\label{{ inst{i+1} }} '
            else:
                print(rf'\label{{{label}}}', end=' ')
                text += rf'\label{{{label}}} '

            if institute == institutes_in_list[-1]:
                print()
                text += '\n'
            else:
                print(r'\and')
                text += r'\and' '\n'

        print(r'}')
        text += r'}' + '\n'

        if preview:
            preview_AandA(text)


    def acknowledgements(self, indent='  ', sanitize_initials=True, **kwargs):
        author_list, known_authors = self._get_author_list(**kwargs)

        print(r'\begin{acknowledgements}')
        for name in author_list:
            author = query_author(name, conn=self.conn)[1]
            if len(author) == 1:
                ack = author[0][2]
                if ack is None:
                    continue

                if sanitize_initials:
                    initials = name_to_initials(author[0][1])
                    initials = ''.join(initials)
                    # replace any I.N.I. ...
                    dotted = ''.join(i + '.' for i in initials)
                    # replace any I. N. I. ...
                    dotted_spaced = ''.join(i + '. ' for i in initials)
                    # replace any I.~N.~I. ...
                    dotted_spaced_tilde = ''.join(i + '.~' for i in initials)

                    ack = ack.replace(dotted, initials)
                    ack = ack.replace(dotted_spaced, initials)
                    ack = ack.replace(dotted_spaced_tilde, initials)

                ack = textwrap.wrap(ack, 80, initial_indent=indent,
                                    subsequent_indent=indent)
                print('\n'.join(ack))
                print()
        print(r'\end{acknowledgements}')
