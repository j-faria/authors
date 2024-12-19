# flake8: noqa
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("authors")
except PackageNotFoundError:
    # package is not installed
    pass

from .authors import Authors, delete_author

from .authors import register_author, delete_author
from .authors import (update_author_name, update_author_affiliations,
                      update_author_email, change_affiliation,
                      set_affiliation_label)
