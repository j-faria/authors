from collections import Counter
import os
from typing import List, Literal, Tuple, Union
from yaml import safe_load as load, safe_dump as dump
# import pyperclip

from .utils import (
    name_to_initials,
    name_to_initials_last,
    name_to_last,
    name_to_first_last,
    strip_accents,
    tex_deescape,
    humanize_yaml,
    closest_author,
)

from .journals.AandA import AandA
from .journals.MNRAS import MNRAS


def _duplicates(lst):
    if len(lst) != len(set(lst)):
        return True, set([x for x in lst if lst.count(x) > 1])
    return False, None


class Names:
    def __init__(self, names: List[str], nicknames: List[str] = [],
                 warnings: bool = False):
        """ Holds a list of names and implements the `in` operator 
        
        Args:
            names (List[str]):
                List of names
            nicknames (List[str], optional):
                List of nicknames.
            warnings (bool, optional):
                Whether to print warnings for duplicate names.
        """
        self.names = [name.casefold() for name in names]  # case-insensitive names
        self.names_norm = [strip_accents(name) for name in self.names]
        self.nicknames = nicknames
        self._warnings = warnings
        if warnings and (dup := _duplicates(names))[0]:
            print(f"WARNING: duplicate names\n{dup[1]}")
        if warnings and (dup := _duplicates(self.last_names))[0]:
            print(f"WARNING: duplicate last names\n{dup[1]}")

    @property
    def last_names(self):
        return [name_to_last(name) for name in self.names]

    @property
    def last_names_norm(self):
        return [name_to_last(strip_accents(name)) for name in self.names]

    @property
    def first_last_names(self):
        return [name_to_first_last(strip_accents(name)) for name in self.names]

    def __len__(self):
        return len(self.names)

    def __contains__(self, name: str):
        name = name.casefold()
        if name in self.names or name in self.last_names:
            return True
        if name in self.nicknames:
            return True
        if (strip_accents(name) in self.names_norm or strip_accents(name) in self.last_names_norm):
            return True
        if name_to_last(name) in self.last_names:
            i = self.last_names.index(name_to_last(name))
            if name_to_initials_last(name) == name_to_initials_last(self.names[i]):
                return True
        if name_to_last(strip_accents(name)) in self.last_names_norm:
            i = self.last_names_norm.index(name_to_last(strip_accents(name)))
            if name_to_initials(name) == name_to_initials(self.names[i]):
                return True
        if name_to_first_last(name) in self.first_last_names:
            return True
        if name_to_first_last(strip_accents(name)) in self.first_last_names:
            return True

        return False


def get_all_known_authors(return_filename=False) -> Union[dict, Tuple[dict, str]]:
    """
    Load the dictionary of all known authors

    Args:
        return_filename (bool):
            Whether to return the path to the yaml file

    Returns:
        known_authors (dict):
            Dictionary with information about the known authors
        file (str):
            Only returned if `return_filename` is True. Path to the yaml file
    """
    here = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(here, "data", "all_known_authors.yml")
    if return_filename:
        return load(open(file, encoding="utf-8")), file
    else:
        return load(open(file, encoding="utf-8"))


def write_all_known_authors(data: dict, confirm: bool = True):
    """Write all the known authors to the yaml file

    Args:
        data (dict):
            Dictionary with information about the known authors
        confirm (bool):
            Whether to ask for confirmation before overwriting the YAML file

    Raises:
        ValueError:
            If `data` is empty
    
    !!! Warning
        This function overwrites the local YAML file that contains the author
        database. Use with caution!
    """
    if len(data) == 0:
        raise ValueError("data is empty")

    _, filename = get_all_known_authors(return_filename=True)

    if confirm:
        print(f"Overwrite {filename}? [y/N]", end=" ")
        if input().lower() != "y":
            print("Not overwriting")
            return

    with open(filename, "w", encoding="utf-8") as stream:
        dump(data, stream, allow_unicode=True, width=500, line_break=True)
    humanize_yaml(filename)


def get_all_affiliations():
    """Get a list of all known affiliations"""
    all_known_authors = get_all_known_authors()
    affiliations = []
    for a in all_known_authors.values():
        for aff in a["affiliations"]:
            if isinstance(aff, dict):
                affiliations.append(list(aff.keys())[0])
            else:
                affiliations.append(aff)
    return affiliations


def get_all_affiliations_with_label():
    """Get a dictionary of all known affiliations that have a label"""
    all_known_authors = get_all_known_authors()
    aff_label = {}
    for a in all_known_authors.values():
        for aff in a["affiliations"]:
            if isinstance(aff, dict):
                key = list(aff.keys())[0]
                aff_label[key] = aff[key]["label"]
    return aff_label


def register_author(
    full_name: str,
    affiliations: List[str],
    labels: List[str] = None,
    email: str = None,
    orcid: str = None,
    acknowledgements: str = None,
    nickname: str = None,
    spelling: str = None,
):
    """Register a new author

    Args:
        full_name (str):
            Full name of the author
        affiliations (List[str]):
            List of affiliations
        labels (List[str], optional):
            Labels to use for each affiliation. Should have the same length as `affiliations`.
        email (str, optional):
            Email address.
        orcid (str, optional):
            ORCID id.
        acknowledgements (str, optional):
            Author's acknowledgements.
        nickname (str, optional):
            Nickname of the author.
        spelling (str, optional):
            Exact spelling of the author's name.
    """
    full_name = tex_deescape(str(full_name))
    all_known_authors = get_all_known_authors()
    label_aff = {v: k for k, v in get_all_affiliations_with_label().items()}

    if full_name in all_known_authors:
        print(f'author "{full_name}" is already known')
        return

    all_known_authors[full_name] = {"email": email, "orcid": orcid, "affiliations": []}

    if email is None:
        all_known_authors[full_name].pop("email")

    if orcid is None:
        all_known_authors[full_name].pop("orcid")

    if labels is None:
        labels = len(affiliations) * [None]

    for aff, label in zip(affiliations, labels):
        aff = tex_deescape(str(aff))
        if aff in label_aff:  # provided label instead of affiliation
            aff_label = {label_aff[aff]: {"label": aff}}
            all_known_authors[full_name]["affiliations"].append(aff_label)
        elif label is None:
            all_known_authors[full_name]["affiliations"].append(aff)
        else:
            aff_label = {aff: {"label": label}}
            all_known_authors[full_name]["affiliations"].append(aff_label)

    if acknowledgements is not None:
        all_known_authors[full_name]["acknowledgements"] = acknowledgements

    if nickname is not None:
        all_known_authors[full_name]["nickname"] = nickname

    if spelling is not None:
        all_known_authors[full_name]["spelling"] = spelling

    write_all_known_authors(all_known_authors, confirm=False)


def update_author_name(old_name: str, new_name: str, allow_closest: bool = False):
    """Update the name of one author

    Args:
        old_name (str):
            The old name, which should exist in the list of known authors
        new_name (str):
            The new name of the author
        allow_closest (bool, optional):
            If True and `old_name` is not found, try to find the closest match
            in the list of known authors
    """
    all_known_authors = get_all_known_authors()
    if allow_closest and old_name not in all_known_authors:
        closest = closest_author(old_name, list(all_known_authors.keys()))[0]
        print(f"author '{old_name}' not found, using closest match '{closest}'")
        old_name = closest
    if old_name in all_known_authors:
        new_name = tex_deescape(str(new_name))
        all_known_authors[new_name] = all_known_authors.pop(old_name)
        write_all_known_authors(all_known_authors, confirm=False)
        print("updated name for", old_name)
    else:
        print(f'author "{old_name}" not found')


def update_author_email(name: str, email: str, allow_closest: bool = False):
    """Update the email of an author

    Args:
        name (str):
            The name of the author
        email (str):
            The new email address
        allow_closest (bool, optional):
            If True and `name` is not found, try to find the closest match
            in the list of known authors
    """
    all_known_authors = get_all_known_authors()
    if allow_closest and name not in all_known_authors:
        closest = closest_author(name, list(all_known_authors.keys()))[0]
        print(f"author '{name}' not found, using closest match '{closest}'")
        name = closest
    if name in all_known_authors:
        all_known_authors[name]["email"] = str(email)
        write_all_known_authors(all_known_authors, confirm=False)
        print("updated email for", name)
    else:
        print(f'author "{name}" not found')


def update_author_orcid(name: str, orcid: str, allow_closest: bool = False):
    """Update the ORCID of an author

    Args:
        name (str):
            The name of the author
        orcid (str):
            The new ORCID
        allow_closest (bool, optional):
            If True and `name` is not found, try to find the closest match
            in the list of known authors
    """
    all_known_authors = get_all_known_authors()
    if allow_closest and name not in all_known_authors:
        closest = closest_author(name, list(all_known_authors.keys()))[0]
        print(f"author '{name}' not found, using closest match '{closest}'")
        name = closest
    if name in all_known_authors:
        all_known_authors[name]["orcid"] = str(orcid)
        write_all_known_authors(all_known_authors, confirm=False)
        print("updated ORCID for", name)
    else:
        print(f'author "{name}" not found')


def update_author_affiliations(
    name: str, affiliations: List[str], strategy: Literal["merge", "replace"] = "merge"
):
    """Update the affiliations of an author

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
        if strategy == "merge":
            existing = all_known_authors[name]["affiliations"]
            new = affiliations + existing
            all_known_authors[name]["affiliations"] = new
        elif strategy == "replace":
            all_known_authors[name]["affiliations"] = affiliations

        write_all_known_authors(all_known_authors, confirm=False)
        print("updated affiliations for", name)
    else:
        print(f'author "{name}" not found')


def update_author_acknowledgements(name: str, acknowledgements: str):
    """Update the acknowledgements of an author

    Args:
        name (str): The name of the author
        acknowledgements (str): The new acknowledgements
    """
    all_known_authors = get_all_known_authors()
    if name in all_known_authors:
        all_known_authors[name]["acknowledgements"] = str(acknowledgements)
        write_all_known_authors(all_known_authors, confirm=False)
        print("updated acknowledgements for", name)
    else:
        print(f'author "{name}" not found')


def update_author_nickname(name: str, nickname: str):
    """Update the nickname of an author

    Args:
        name (str): The name of the author
        nickname (str): The new nickname
    """
    all_known_authors = get_all_known_authors()
    if name in all_known_authors:
        all_known_authors[name]["nickname"] = str(nickname)
        write_all_known_authors(all_known_authors, confirm=False)
        print("updated nickname for", name)
    else:
        print(f'author "{name}" not found')


def update_author_spelling(name: str, spelling: str):
    """Update the spelling of an author's name

    Args:
        name (str): The name of the author
        spelling (str): The new spelling
    """
    all_known_authors = get_all_known_authors()
    if name in all_known_authors:
        all_known_authors[name]["spelling"] = str(spelling)
        write_all_known_authors(all_known_authors, confirm=False)
        print("updated spelling for", name)
    else:
        print(f'author "{name}" not found')


def delete_author(name: str):
    """Remove an author from the known author list

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
    """Change an affiliation

    Args:
        old (str): old affiliation, which will be replaced
        new (str): new affiliation
    """
    all_known_authors = get_all_known_authors()
    for k, v in all_known_authors.items():
        affs = v["affiliations"]
        for i, aff in enumerate(affs):
            if old in aff:
                print(k, aff, type(aff))
                if isinstance(aff, str):
                    v["affiliations"][i] = new
                elif isinstance(aff, dict):
                    v["affiliations"][i][new] = aff[old]
                    v["affiliations"][i].pop(old)
    write_all_known_authors(all_known_authors)


def set_affiliation_label(affiliation: str, label: str):
    """Set the label for a given affiliation

    Args:
        affiliation (str): the affiliation to set the label for
        label (str): the label
    """
    all_known_authors = get_all_known_authors()
    for k, v in all_known_authors.items():
        if affiliation in v["affiliations"]:
            aff = []
            for a in v["affiliations"]:
                if a == affiliation:
                    aff.append({affiliation: {"label": str(label)}})
                else:
                    aff.append(a)
            all_known_authors[k]["affiliations"] = aff

    write_all_known_authors(all_known_authors)


def _health_check(check_affiliations: bool = True):
    all_known_authors = get_all_known_authors()
    print(f"there are {len(all_known_authors)} known authors")
    print("checking for duplicate / similar author names...")
    names = list(all_known_authors.keys())
    if len(names) == len(set(names)):
        print(" no exact duplicates")

    names_initials_last = [name_to_initials_last(name) for name in names]
    if len(names_initials_last) == len(set(names_initials_last)):
        print(" no duplicates in initials, last name")
    else:
        print(" duplicates in initials, last name:")
        c = Counter(names_initials_last)
        for name, counts in c.items():
            if counts > 1:
                print("  ", name, "occurs", counts, "times")

    affiliations = list(set(get_all_affiliations()))
    affiliation_label = get_all_affiliations_with_label()
    print(f"there are {len(affiliations)} unique affiliations")

    print("setting affiliation labels...")
    for i, affiliation in enumerate(affiliations):
        print(f"progress {i + 1}/{len(affiliations)}", end="\r")
        if affiliation in affiliation_label:
            set_affiliation_label(affiliation, affiliation_label[affiliation])

    if not check_affiliations:
        return
    print("checking for duplicate / similar affiliations...")
    from .utils import lev_dist

    for i, affiliation1 in enumerate(affiliations):
        print(f"progress {i + 1}/{len(affiliations)}", end="\r")
        for j, affiliation2 in enumerate(affiliations[i + 1 :]):
            dist = lev_dist(affiliation1, affiliation2)
            prob = 1 - 2 * dist / (len(affiliation1) + len(affiliation2))
            if prob > 0.7:
                print(f"{dist=}, {prob=}")
                print(" " + affiliation1)
                print(" " + affiliation2)
                opt = input(" (1) keep first (2) keep second (3) keep both : ")
                if opt == "1":
                    change_affiliation(affiliation2, affiliation1)
                elif opt == "2":
                    change_affiliation(affiliation1, affiliation2)
                elif opt == "3":
                    pass


class Authors(AandA, MNRAS):
    """Hold information about the authors of a paper"""

    def __init__(self, load_from: str, warn_unknown: bool = True) -> None:
        r"""
        Args:
            load_from (str):
                From where to load the author list. Can be a '\n'-separated
                string with the author names or the name of a file containing
                the list of authors.
            warn_unknown (bool):
                Whether to emit warninings for unknown authors

        Examples:
            >>> Authors('First Name\nSecond Name')
            >>> Authors('author_list.txt')

        """
        if not isinstance(load_from, str):
            raise TypeError("`load_from` must be a string")

        if load_from == "":
            raise ValueError("`load_from` should not be an empty string")

        if load_from == "all":
            load_from = "\n".join([n for n in get_all_known_authors().keys()])

        self.all_known_authors = get_all_known_authors()

        self.all_known_nicknames = list(
            set([v.get("nickname", "") for v in self.all_known_authors.values()])
        )

        self.names = Names(
            self.all_known_authors.keys(),
            nicknames=self.all_known_nicknames,
            warnings=False,
        )

        if os.path.exists(load_from):
            A = list(map(str.strip, open(load_from, encoding="utf-8").readlines()))
        else:
            assert isinstance(load_from, str)
            A = load_from.splitlines()

        self.all_authors = [a for a in A if a != ""]
        self.last_names = [name_to_last(a).lower() for a in A]
        self.first_author = self.all_authors[0]
        self.known = self._get_known_authors()

        if warn_unknown and not all(self.known):
            print("WARNING: some authors are unknown:", ", ".join(self.unknown_authors))

    def __repr__(self):
        return f"Authors({len(self.all_authors)} authors, {sum(self.known)} known)"

    @property
    def unknown_authors(self):
        return [a for a, known in zip(self.all_authors, self.known) if not known]

    def _get_known_authors(self) -> List:
        known = [author in self.names for author in self.all_authors]
        return known

        # known = []
        # for last_name in self.last_names:
        #     if last_name.casefold() in known_last_names:
        #         known.append(True)
        #     elif tex_deescape(last_name).casefold() in known_last_names:
        #         known.append(True)
        #     elif last_name.casefold() in known_last_names_norm:
        #         known.append(True)
        #     elif last_name.casefold() in known_nicknames:
        #         known.append(True)
        #     elif any(match := [last_name in known_last_name for known_last_name in known_last_names_norm]):
        #         if sum(match) > 1:
        #             raise ValueError(f"multiple matches for {last_name}")
        #         known.append(True)
        #     else:
        #         known.append(False)
        # return known

    def _get_author_list(
        self, alphabetical=False, alphabetical_after=1, alphabetical_groups=None
    ):
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
                    author_list.append(self.all_authors[alphabetical_after:][i])
                    known_authors.append(self.known[alphabetical_after:][i])

            # sort alphabetically in groups (alphabetical_after is ignored)
            else:
                alphabetical_groups.append(len(self.all_authors))
                alphabetical_after = alphabetical_groups[0]
                # authors which are not in alphabetical order
                author_list = self.all_authors[:alphabetical_after]
                known_authors = self.known[:alphabetical_after]

                # authors which are in alphabetical order, sorted
                for g1, g2 in zip(alphabetical_groups, alphabetical_groups[1:]):
                    sauthors = argsort(self.last_names[g1:g2])
                    for i in sauthors:
                        author_list.append(self.all_authors[g1:][i])
                        known_authors.append(self.known[g1:][i])

        else:
            author_list = self.all_authors
            known_authors = self.known

        return author_list, known_authors

    def query_author(self, author: str):
        if author in self.all_known_authors:
            return author, self.all_known_authors[author]

        last_name = name_to_last(author)
        for name, data in self.all_known_authors.items():
            _last = name_to_last(name)
            if last_name.casefold() == _last.casefold():
                return name, data
            if tex_deescape(last_name) == _last:
                return name, data
            if last_name.casefold() in data.get("nickname", "").casefold():
                return name, data
            if last_name.casefold() in strip_accents(_last).casefold():
                return name, data
        return ValueError("unreachable")

    def _get_name(self, name: str, data: dict, force_initials: bool = True):
        if "spelling" in data:
            name = data["spelling"]
        else:
            if force_initials:
                name = name_to_initials_last(name)
        # don't line-break people's names, it's not polite
        name = name.replace(" ", "~")
        return name

    def AandA(
        self,
        show=True,
        add_orcids: bool = True,
        preview: bool = False,
        alphabetical: bool = False,
        alphabetical_after: int = 1,
        alphabetical_groups: List[int] = None,
        force_initials: bool = True,
        save_to_file: str = None,
        copy_to_clipboard: bool = False,
    ):
        r"""Provide the \author and \institute LaTeX tags for A&A

        Args:
            show (bool, optional):
                Whether to print the \author and \institute tags (otherwise just
                return them in a string).
            add_orcids (bool, optional):
                Whether to add ORCID links for authors that have them. Note that
                this may require additional LaTeX, and may not be accepted by
                every journal.
            preview (bool, optional):
                Try to compile and preview a template LaTeX file.
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
            save_to_file (str, optional):
                File where to save the LaTeX tags
            copy_to_clipboard (bool, optional):
                Copy the LaTeX tags to the clipboard
        """
        author_list, known_authors = self._get_author_list(
            alphabetical, alphabetical_after, alphabetical_groups
        )

        institutes_in_list = []
        labels = {}

        text = ""

        # print the authors first
        text += r"\author{" + "\n"

        for i, author in enumerate(author_list):
            if known_authors[i]:
                name, data = self.query_author(author)

                name = self._get_name(name, data, force_initials)

                institutes = data["affiliations"]

                numbers = []

                text += f"  {name} "

                text += r"\inst{"

                for j, institute in enumerate(institutes):
                    label = None
                    if isinstance(institute, dict):
                        _institute = list(institute.keys())[0]
                        label = institute[_institute]["label"]
                        institute = _institute

                    if institute not in labels:
                        labels[institute] = label

                    if institute not in institutes_in_list:
                        institutes_in_list.append(institute)

                    numbers.append(institutes_in_list.index(institute) + 1)

                    end = ", " if j < (len(institutes) - 1) else ""
                    if labels[institute] is None:
                        text += f"\\ref{{ inst{numbers[-1]} }}{end}"
                    else:
                        text += f"\\ref{{{labels[institute]}}}{end}"

                text += r"} "

                if "orcid" in data and add_orcids:
                    text += f"\\orcidlink{{{data['orcid']}}} "

            else:
                text += f"  {author} "
                text += r"\inst{unknown} "

            if i < (len(self.all_authors) - 1):
                text += r"\and" + "\n"

        text += "\n" + "}" + "\n\n"

        # then print the institutes
        text += r"\institute{" + "\n"

        for i, institute in enumerate(institutes_in_list):
            escaped_institute = tex_escape(institute)
            label = labels[institute]
            text += f"  {escaped_institute} "

            if label is None:
                text += rf"\label{{ inst{i + 1} }} "
            else:
                text += rf"\label{{{label}}} "

            if institute == institutes_in_list[-1]:
                text += "\n"
            else:
                text += r"\and" "\n"

        text += r"}" + "\n"

        if show:
            print(text)

        if save_to_file is not None:
            with open(save_to_file, "w", encoding="utf-8") as f:
                print(text, file=f)

        if preview:
            longauth = len(institutes_in_list) > 20
            preview_AandA(text, longauth=longauth)

        # if copy_to_clipboard:
        #     pyperclip.copy(text)

        return text

    def MNRAS(
        self,
        show: bool = True,
        preview: bool = False,
        add_orcids: bool = True,
        line_breaks: int = 6,
        alphabetical: bool = False,
        alphabetical_after: int = 1,
        alphabetical_groups: List[int] = None,
        force_initials: bool = True,
        save_to_file: str = None,
        copy_to_clipboard: bool = False,
    ):
        r"""Provide the \author LaTeX tag for MNRAS

        Args:
            show (bool, optional):
                Whether to print the LaTeX tags (otherwise, just return them)
            preview (bool, optional):
                NO DOC
            add_orcids (bool, optional):
                NO DOC
            alphabetical (bool, optional):
                Whether to sort author names alphabetically. Default is False
            alphabetical_after (int, optional):
                Sort author names alphabetically *after* this author. By
                default, sort after the first author.
            alphabetical_groups (List[int], optional):
                If provided, sort author names alphabetically in groups.
                Examples:
                  [5, 10] authors 1, 2, 3, 4, 5 use order as given
                          authors 6, 7, 8, 9, 10 sorted alphabetically authors
                          11, ... sorted alphabetically
                  [3] authors 1, 2, 3 use order as given
                      authors 4, ... sorted alphabetically (this would be
                      equivalent to using alphabetical_after=3)
            force_initials (bool, optional):
                If True, force the author names to be F. M. Last
            save_to_file (str, optional):
                File where to save the LaTeX tags
            copy_to_clipboard (bool, optional):
                Copy the LaTeX tags to the clipboard
        """
        author_list, known_authors = self._get_author_list(
            alphabetical, alphabetical_after, alphabetical_groups
        )

        institutes_in_list = []
        labels = {}

        text = ""

        # print the authors first
        text += r"\author[]{" + "\n"

        for i, author in enumerate(author_list):
            if known_authors[i]:
                name, data = self.query_author(author)

                name = self._get_name(name, data, force_initials)

                institutes = data["affiliations"]

                numbers = []

                text += f"  {name} "

                text += r"$^{"

                for j, institute in enumerate(institutes):
                    label = None
                    if isinstance(institute, dict):
                        _institute = list(institute.keys())[0]
                        label = institute[_institute]["label"]
                        institute = _institute

                    if institute not in labels:
                        labels[institute] = label

                    if institute not in institutes_in_list:
                        institutes_in_list.append(institute)

                    numbers.append(institutes_in_list.index(institute) + 1)

                    end = r",\, " if j < (len(institutes) - 1) else ""
                    text += f"{numbers[-1]}{end}"

                text += r"}$"

                if i < (len(self.all_authors) - 1):
                    text += ", "

            if (i + 1) % line_breaks == 0:
                text += r"\newauthor\,\!"

            if i < (len(self.all_authors) - 1):
                text += "\n"

        text += "\n"

        # then print the institutes
        text += r"\\" + "\n"

        for i, institute in enumerate(institutes_in_list):
            escaped_institute = tex_escape(institute)
            label = labels[institute]
            text += f" $^{{{i + 1}}}$ {escaped_institute} "

            if institute == institutes_in_list[-1]:
                text += "\n"
            else:
                text += r"\\" + "\n"

        text += r"}" + "\n"

        if show:
            print(text)

        if save_to_file is not None:
            with open(save_to_file, "w") as f:
                print(text, file=f)

        if preview:
            preview_MNRAS(text)

        # if copy_to_clipboard:
        #     pyperclip.copy(text)

        return text
