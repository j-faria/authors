from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..authors import Authors

from ..latex_pdf_utils import preview_MNRAS
from ..utils import tex_escape


class MNRAS:
    def MNRAS(
        self: Authors,
        show: bool = True,
        preview: bool = False,
        line_breaks: int = 6,
        alphabetical: bool = False,
        alphabetical_after: int = 1,
        alphabetical_groups: List[int] | None = None,
        force_initials: bool = True,
        save_to_file: str | None = None,
        # copy_to_clipboard: bool = False,
    ) -> str:
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
