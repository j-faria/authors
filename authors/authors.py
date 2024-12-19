""" Authors of your next scientific article """

from collections import Counter
import os
from typing import List, Literal, Tuple, Union
from yaml import safe_load as load, safe_dump as dump

from .utils import (name_to_initials_last, name_to_last, tex_escape,
                    tex_deescape, humanize_yaml)
from .latex_pdf_utils import preview_AandA, preview_MNRAS


def get_all_known_authors(
        return_filename=False) -> Union[dict, Tuple[dict, str]]:
    """
    Load the dictionary of all known authors

    Args:
        return_filename (bool): Whether to return the path to the yaml file
    Returns:
        known_authors (dict):
            Dictionary with information about the known authors
        file (str):
            Only returned if `return_filename` is True. Path to the yaml file
    """
    here = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(here, 'data', 'all_known_authors.yml')
    if return_filename:
        return load(open(file, encoding='utf-8')), file
    else:
        return load(open(file, encoding='utf-8'))


def write_all_known_authors(data):
    # with open('all_known_authors_new.yml', 'w') as stream:
    _, filename = get_all_known_authors(return_filename=True)
    with open(filename, 'w', encoding='utf-8') as stream:
        dump(data, stream, allow_unicode=True, width=500, line_break=True)
    humanize_yaml(filename)


def get_all_affiliations():
    all_known_authors = get_all_known_authors()
    affiliations = []
    for a in all_known_authors.values():
        for aff in a['affiliations']:
            if isinstance(aff, dict):
                affiliations.append(list(aff.keys())[0])
            else:
                affiliations.append(aff)
    return affiliations


def register_author(full_name: str, affiliations: List[str], email: str = None,
                    orcid: str = None, labels: List[str] = None):
    """Register a new author

    Args:
        full_name (str): Full name of the author
        affiliations (List[str]): List of affiliations
        email (str, optional): Email address. Defaults to None.
        orcid (str, optional): ORCID id. Defaults to None.
        labels (List[str], optional):
            Labels to use for each affiliation. Should have the same length as
            `affiliations`. Defaults to None.
    """
    full_name = tex_deescape(str(full_name))
    all_known_authors, filename = get_all_known_authors(return_filename=True)

    if full_name in all_known_authors:
        print(f'author "{full_name}" is already known')
        return

    all_known_authors[full_name] = {
        'email': email,
        'orcid': orcid,
        'affiliations': []
    }

    if email is None:
        all_known_authors[full_name].pop('email')

    if orcid is None:
        all_known_authors[full_name].pop('orcid')

    if labels is None:
        labels = len(affiliations) * [None]

    for aff, label in zip(affiliations, labels):
        aff = tex_deescape(str(aff))
        if label is None:
            all_known_authors[full_name]['affiliations'].append(aff)
        else:
            aff_label = {aff: {'label': label}}
            all_known_authors[full_name]['affiliations'].append(aff_label)

    write_all_known_authors(all_known_authors)


def update_author_name(old_name: str, new_name: str):
    """ Update the name of one author

    Args:
        old_name (str):
            The old name, which should exist in the list of known authors
        new_name (str):
            The new name of the author
    """
    all_known_authors = get_all_known_authors()
    if old_name in all_known_authors:
        new_name = tex_deescape(str(new_name))
        all_known_authors[new_name] = all_known_authors.pop(old_name)
    write_all_known_authors(all_known_authors)


def update_author_email(name: str, email: str):
    """ Update the email of an author

    Args:
        name (str): The name of the author
        email (str): The new email address
    """
    all_known_authors = get_all_known_authors()
    if name in all_known_authors:
        all_known_authors[name]['email'] = str(email)
    write_all_known_authors(all_known_authors)


def update_author_orcid(name: str, orcid: str):
    """ Update the ORCID of an author

    Args:
        name (str): The name of the author
        orcid (str): The new ORCID
    """
    all_known_authors = get_all_known_authors()
    if name in all_known_authors:
        all_known_authors[name]['orcid'] = str(orcid)
    write_all_known_authors(all_known_authors)


def update_author_affiliations(name: str, affiliations: List[str],
                               strategy: Literal['merge', 'replace'] = 'merge'):
    """ Update the affiliations of an author

    Args:
        name (str): The name of the author
        affiliations (List[str]): List of new affiliations
        strategy (Literal['merge', 'replace']):
            Which strategy to use for the update. If 'merge', the new
            affiliations are added to the existing ones (keeping only unique).
            If 'replace', the existing affiliations are replaced.
    """
    if isinstance(affiliations, str):
        affiliations = [affiliations]

    all_known_authors = get_all_known_authors()
    if name in all_known_authors:
        if strategy == 'merge':
            existing = all_known_authors[name]['affiliations']
            new = affiliations + existing
            all_known_authors[name]['affiliations'] = new
        elif strategy == 'replace':
            all_known_authors[name]['affiliations'] = affiliations

    write_all_known_authors(all_known_authors)


def delete_author(name: str):
    """ Remove an author from the known author list

    Args:
        name (str): name of the author to remove
    """
    all_known_authors = get_all_known_authors()
    if name in all_known_authors:
        all_known_authors.pop(name)
        write_all_known_authors(all_known_authors)
        print(f'removed author "{name}"')
    else:
        print(f'author "{name}" not found')


def change_affiliation(old: str, new: str):
    """ Change an affiliation

    Args:
        old (str): old name of the affiliation, which will be replaced
        new (str): new name of the affiliation
    """
    from fileinput import FileInput
    _, filename = get_all_known_authors(return_filename=True)
    with FileInput(filename, inplace=True, backup='.bak') as f:
        for line in f:
            print(line.replace(old, new), end='')


def set_affiliation_label(affiliation: str, label: str):
    """ Set the label for a given affiliation

    Args:
        affiliation (str): the affiliation to set the label for
        label (str): the label
    """
    all_known_authors = get_all_known_authors()
    for k, v in all_known_authors.items():
        if affiliation in v['affiliations']:
            aff = []
            for a in v['affiliations']:
                if a == affiliation:
                    aff.append({affiliation: {'label': str(label)}})
                else:
                    aff.append(a)
            all_known_authors[k]['affiliations'] = aff

    write_all_known_authors(all_known_authors)


def _health_check():
    all_known_authors = get_all_known_authors()
    print(f'there are {len(all_known_authors)} known authors')
    print('checking for duplicate / similar author names...')
    names = list(all_known_authors.keys())
    if len(names) == len(set(names)):
        print(' no exact duplicates')

    names_initials_last = [name_to_initials_last(name) for name in names]
    if len(names_initials_last) == len(set(names_initials_last)):
        print(' no duplicates in initials, last name')
    else:
        print(' duplicates in initials, last name:')
        c = Counter(names_initials_last)
        for name, counts in c.items():
            if counts > 1:
                print('  ', name, 'occurs', counts, 'times')

    affiliations = list(set(get_all_affiliations()))
    print(f'there are {len(affiliations)} unique affiliations')

    from .utils import lev_dist
    for i, affiliation1 in enumerate(affiliations):
        for j, affiliation2 in enumerate(affiliations[i + 1:]):
            dist = lev_dist(affiliation1, affiliation2)
            prob = 1 - 2 * dist / (len(affiliation1) + len(affiliation2))
            if prob > 0.7:
                print(f'{dist=}, {prob=}')
                print(' ' + affiliation1)
                print(' ' + affiliation2)
                opt = input(' (1) keep first (2) keep second (3) keep both : ')
                if opt == '1':
                    change_affiliation(affiliation2, affiliation1)
                elif opt == '2':
                    change_affiliation(affiliation1, affiliation2)
                elif opt == '3':
                    pass


class Authors:
    """ Hold information about the authors of a paper """
    def __init__(self, load_from: str) -> None:
        r"""
        Args:
            load_from (str):
                From where to load the author list. Can be a '\n'-separated
                string with the author names or the name of a file containing
                the list of authors.
        Examples:
            Authors('First Name\nSecond Name')
            Authors('author_list.txt')
        """
        if not isinstance(load_from, str):
            raise TypeError('`load_from` must be a string')
        
        if load_from == '':
            raise ValueError('`load_from` should not be an empty string')

        here = os.path.dirname(os.path.abspath(__file__))
        all_known_authors_file = os.path.join(here, 'data',
                                              'all_known_authors.yml')
        self.all_known_authors = load(open(all_known_authors_file, encoding='utf-8'))

        if os.path.exists(load_from):
            A = list(map(str.strip, open(load_from).readlines()))
        else:
            assert isinstance(load_from, str)
            A = load_from.splitlines()

        self.all_authors = [a for a in A if a != '']
        self.last_names = [name_to_last(a).lower() for a in A]
        self.first_author = self.all_authors[0]
        self.known = self._get_known_authors()

    def _get_known_authors(self) -> List:
        known_last_names = [
            name_to_last(a).lower() for a in self.all_known_authors.keys()
        ]
        known = []
        for last_name in self.last_names:
            if last_name.lower() in known_last_names:
                known.append(True)
            else:
                known.append(False)
        return known

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

    def query_author(self, author: str):
        last_name = name_to_last(author)
        for name, data in self.all_known_authors.items():
            if last_name in name_to_last(name):
                return name, data

    def AandA(self, alphabetical: bool = False, alphabetical_after: int = 1,
              alphabetical_groups: List[int] = None,
              force_initials: bool = True, add_orcids: bool = True,
              preview: bool = False, save_to_file: str = None):
        r""" Provide the \author and \institute LaTeX tags for A&A

        Args:
            alphabetical (bool, optional):
                Whether to sort author (last) names alphabetically.
            alphabetical_after (int, optional):
                Sort author names alphabetically *after* this author. By
                default, sort after the first author.
            alphabetical_groups (List[int], optional):
                If provided, sort author names alphabetically in groups.
                Examples:
                  [5, 10] authors 1, 2, 3, 4, 5 use order as given
                          authors 6, 7, 8, 9, 10 sorted alphabetically
                          authors 11, ... sorted alphabetically
                  [3] authors 1, 2, 3 use order as given
                      authors 4, ... sorted alphabetically
                      (this would be equivalent to using alphabetical_after=3)
            force_initials (bool, optional):
                If True, force the author names to be F. M. Last
            add_orcids (bool, optional):
                Whether to add ORCID links for authors that have them. Note that
                this may require additional LaTeX, and may not be accepted by
                every journal.
            preview (bool, optional):
                Try to compile and preview a template LaTeX file.
            save_to_file (str, optional):
                File where to save the LaTeX tags
        """
        author_list, known_authors = self._get_author_list(
            alphabetical, alphabetical_after, alphabetical_groups)

        institutes_in_list = []
        labels = {}

        text = ''

        # print the authors first
        text += r'\author{' + '\n'

        for i, author in enumerate(author_list):
            if known_authors[i]:
                name, data = self.query_author(author)
                institutes = data['affiliations']

                if force_initials:
                    name = name_to_initials_last(name)

                # don't line-break people's names, it's not polite
                name = name.replace(' ', '~')
                numbers = []

                text += f'  {name} '

                text += r'\inst{'

                for j, institute in enumerate(institutes):
                    label = None
                    if isinstance(institute, dict):
                        _institute = list(institute.keys())[0]
                        label = institute[_institute]['label']
                        institute = _institute

                    if institute not in labels:
                        labels[institute] = label

                    if institute not in institutes_in_list:
                        institutes_in_list.append(institute)

                    numbers.append(institutes_in_list.index(institute) + 1)

                    end = ', ' if j < (len(institutes) - 1) else ''
                    if labels[institute] is None:
                        text += f'\\ref{{ inst{numbers[-1]} }}{end}'
                    else:
                        text += f'\\ref{{{labels[institute]}}}{end}'

                # thanks = queryA[0][3]
                # if thanks is not None:
                #     text += rf', \thanks{{ {thanks} }}'

                text += r'} '

                if 'orcid' in data and add_orcids:
                    text += f"\\orcidlink{{{data['orcid']}}} "


            else:
                text += f'  {author} '
                text += r'\inst{unknown} '

            if i < (len(self.all_authors) - 1):
                text += r'\and' + '\n'

        text += '\n' + '}' + '\n\n'

        # then print the institutes
        text += r'\institute{' + '\n'

        for i, institute in enumerate(institutes_in_list):
            escaped_institute = tex_escape(institute)
            label = labels[institute]
            text += f'  {escaped_institute} '

            if label is None:
                text += rf'\label{{ inst{i+1} }} '
            else:
                text += rf'\label{{{label}}} '

            if institute == institutes_in_list[-1]:
                text += '\n'
            else:
                text += r'\and' '\n'

        text += r'}' + '\n'

        print(text)

        if save_to_file is not None:
            with open(save_to_file, 'w') as f:
                print(text, file=f)

        if preview:
            preview_AandA(text)


    def MNRAS(self, line_breaks: int = 6, alphabetical: bool = False,
              alphabetical_after: int = 1,
              alphabetical_groups: List[int] = None,
              force_initials: bool = True, add_orcids: bool = True,
              preview: bool = False, save_to_file: str = None):
        r""" Provide the \author LaTeX tag for MNRAS

        Args:
            alphabetical (bool, optional):
                Whether to sort author names alphabetically. Default is False
            alphabetical_after (int, optional):
                Sort author names alphabetically *after* this author. By
                default, sort after the first author.
            alphabetical_groups (List[int], optional):
                If provided, sort author names alphabetically in groups.
                Examples:
                  [5, 10] authors 1, 2, 3, 4, 5 use order as given
                          authors 6, 7, 8, 9, 10 sorted alphabetically
                          authors 11, ... sorted alphabetically
                  [3] authors 1, 2, 3 use order as given
                      authors 4, ... sorted alphabetically
                      (this would be equivalent to using alphabetical_after=3)
            force_initials (bool, optional):
                If True, force the author names to be F. M. Last
            add_orcids (bool, optional):
                Whether to add ORCID links for authors that have them. Note that
                this may require additional LaTeX, and may not be accepted by
                every journal. Default is True.
            preview (bool, optional):
                NO DOC
            save_to_file (str, optional):
                File where to save the LaTeX tags
        """
        author_list, known_authors = self._get_author_list(
            alphabetical, alphabetical_after, alphabetical_groups)


        institutes_in_list = []
        labels = {}

        text = ''

        # print the authors first
        text += r'\author[]{' + '\n'

        for i, author in enumerate(author_list):
            if known_authors[i]:
                name, data = self.query_author(author)
                institutes = data['affiliations']

                if force_initials:
                    name = name_to_initials_last(name)

                # don't line-break people's names, it's not polite
                name = name.replace(' ', '~')
                numbers = []

                text += f'  {name} '

                text += r'$^{'

                for j, institute in enumerate(institutes):
                    label = None
                    if isinstance(institute, dict):
                        _institute = list(institute.keys())[0]
                        label = institute[_institute]['label']
                        institute = _institute

                    if institute not in labels:
                        labels[institute] = label

                    if institute not in institutes_in_list:
                        institutes_in_list.append(institute)

                    numbers.append(institutes_in_list.index(institute) + 1)

                    end = r',\, ' if j < (len(institutes) - 1) else ''
                    text += f'{numbers[-1]}{end}'

                # thanks = queryA[0][3]
                # if thanks is not None:
                #     text += rf', \thanks{{ {thanks} }}'

                if 'orcid' in data and add_orcids:
                    text += rf", \, \\orcidlink{{{data['orcid']}}} "

                text += r'}$,  '

            # else:
            #     text += f'  {author} '
            #     text += r'\inst{unknown} '

            if (i + 1) % line_breaks == 0:
                text += r"\newauthor\,\!"

            if i < (len(self.all_authors) - 1):
                text += '\n'

        text += '\n'

        # then print the institutes
        text += r'\\' + '\n'

        for i, institute in enumerate(institutes_in_list):
            escaped_institute = tex_escape(institute)
            label = labels[institute]
            text += f' $^{{{i+1}}}$ {escaped_institute} '

            # if label is None:
            #     text += rf'\label{{ inst{i+1} }} '
            # else:
            #     text += rf'\label{{{label}}} '

            if institute == institutes_in_list[-1]:
                text += '\n'
            else:
                text += r'\\' + '\n'

        text += r'}' + '\n'

        print(text)

        if save_to_file is not None:
            with open(save_to_file, 'w') as f:
                print(text, file=f)
        # \author[K. T. Smith et al.]{
        # Keith T. Smith,$^{1}$\thanks{E-mail: mn@ras.org.uk (KTS)}
        # A. N. Other,$^{2}$
        # Third Author$^{2,3}$
        # and Fourth Author$^{3}$
        # \\
        # % List of institutions
        # $^{1}$Royal Astronomical Society, Burlington House, Piccadilly, London W1J 0BQ, UK\\
        # $^{2}$Department, Institution, Street Address, City Postal Code, Country\\
        # $^{3}$Another Department, Different Institution, Street Address, City Postal Code, Country
        # }

        if preview:
            preview_MNRAS(text)

