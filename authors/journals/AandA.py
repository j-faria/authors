from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..authors import Authors

from ..latex_pdf_utils import preview_AandA
from ..utils import tex_escape


class AandA:
    def AandA(
        self: Authors,
        show: bool = True,
        add_orcids: bool = True,
        preview: bool = False,
        alphabetical: bool = False,
        alphabetical_after: int = 1,
        alphabetical_groups: List[int] | None = None,
        add_email: bool = True,
        force_initials: bool = True,
        save_to_file: str | None = None,
        # copy_to_clipboard: bool = False,
    ) -> str:
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
            add_email (bool, optional):
                Add email address for first author (if available)
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

        email = ""

        for i, author in enumerate(author_list):
            if known_authors[i]:
                name, data = self.query_author(author)

                name = self._get_name(name, data, force_initials)

                institutes = data["affiliations"]

                if add_email and i == 0:
                    email = data.get("email", "")

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

            if add_email and i == 0 and email != "":
                text += rf"\\ \email{{{email}}} "

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
