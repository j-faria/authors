# flake8: noqa
__all__ = ['Authors']

from importlib.metadata import version as _version, PackageNotFoundError

try:
    __version__ = _version("authors")
except PackageNotFoundError: # package is not installed
    pass


from .authors import Authors
from .authors import register_author, delete_author
from .authors import (update_author_name, update_author_affiliations,
                      update_author_email, change_affiliation,
                      set_affiliation_label)
