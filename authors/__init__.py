# flake8: noqa
__all__ = ['Authors']

from importlib.metadata import version as _version, PackageNotFoundError

try:
    __version__ = _version("authors")
except PackageNotFoundError: # package is not installed
    pass


from .authors import Authors, _health_check
from .authors import (
    register_author, 
    delete_author,
    # 
    update_author_name, 
    update_author_affiliations,
    update_author_email,
    update_author_orcid,
    update_author_acknowledgements,
    update_author_nickname,
)

from . import utils