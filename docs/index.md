<div align="center">
<img src="https://raw.githubusercontent.com/j-faria/authors/master/authors/crowd.png" alt="crowd of authors" width="400"></img>
</div>

This package provides simple ways to register and manage authors of scientific
papers together with their affiliations, unique identifiers, and other metadata.

The package can be installed with the following command
<!-- (![PyPI - Version](https://img.shields.io/pypi/v/authors?style=flat&label=PyPI&link=https%3A%2F%2Fpypi.org%2Fproject%2Fauthors%2F)) -->

```sh
pip install authors
```

and used as follows:

```python
from authors import Authors

Authors('list.txt').AandA()
```

where `list.txt` is a file with the names of the authors, one per line.