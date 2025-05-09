# Documentation

The idea behind the `authors` package is to keep a _very_ simple database of authors'
names, affiliations, and other metadata. The database is stored in a
_human-readable_ YAML file, which makes it easy to edit and maintain. There is a
**public** version of this database, which can be found
[here](https://github.com/j-faria/authors/blob/main/authors/data/all_known_authors.yml),
but you can also create and use your own local version of the database.

### Interacting with the public database

To edit the public database, we use issues[^1] on the [GitHub
repository](https://github.com/j-faria/authors/issues){:target="_blank"}. You can [create a new
issue](https://github.com/j-faria/authors/issues/new/choose){:target="_blank"} and choose from the
available templates:

![alt text](image.png)

### Using the package

To use the package in your code you just create an instance of the
`Authors` class and call the method corresponding to the journal you are working
with. For example:

```python
from authors import Authors

Authors('Faria').AandA()
```

will output (and also return):

```
\author{
  J.~P.~Faria \inst{\ref{geneva}} \orcidlink{0000-0002-6728-244X}
}

\institute{
  Observatoire Astronomique de l'Université de Genève, Chemin Pegasi 51b, 1290 Versoix, Switzerland \label{geneva}
}
```

which you can copy and paste directly into your A&A LaTeX document.

!!! note

    If there were more authors in the example above, the institutes would be 
    correctly sorted and labeled, and it is also possible to sort (some of) 
    the authors alphabetically.


Currently, there are methods available for two different journals, A&A and
MNRAS, but it is easy to add support for other journals. The methods are
documented in the [API reference](api.md).


To interact with the local database of authors (which is a simple YAML file in
your computer), you can use some of the following functions

```python
import authors

authors.register_author(...)
authors.update_author_affiliations(...)
authors.update_author_name(...)
authors.update_author_orcid(...)
```

The changes you make will be written back to the YAML file and will be available
next time you use the package. In any case, we encourage you to submit changes
to the public database (see above), which would make them available to everyone.

#### Command line interface

You can also use the command line interface to interact with the database. The
following commands will be available when you install the package

```sh
$ authors-update-author-name
$ authors-update-author-email
$ authors-update-author-orcid
$ authors-delete-author
$ authors
```

For example, the last command can be used as follows:

```sh
$ authors list.txt -j aanda
# some output...
```


### Names can be complicated

Representing people's names, across cultures and languages, can be a challenge.
The `authors` package tries to make things simple, but there is certainly room
for improvement. The default behaviour is to convert names into initials and
last names, but even this simple task can get complicated. 

To make sure that a name is correctly represented, you can use `[` and `]`
characters to enclose parts of the name that should not be modified. 

For example, let's say the author is [Federico García
Lorca](https://wikipedia.org/wiki/Federico_Garc%c3%ada_Lorca), a well-known
Spanish poet. Registering this name and using the
[`AandA`][authors.Authors.AandA]  method would result in the default behaviour
of separating the last name and initials:

```python
authors.register_author('Federico García Lorca', ['Some institute'])

authors.Authors('Federico García Lorca').AandA()
# \author{
#   F.~G.~Lorca \inst{\ref{ inst1 }}
# }
# 
# \institute{
#   Some institute \label{ inst1 }
# }
```

But it's quite common for Spanish authors to write both family names, so we
could use `[` and `]` to change the default behaviour:

```python
authors.update_author_name('Federico García Lorca', 'Federico [García Lorca]')

authors.Authors('Federico García Lorca').AandA()
# \author{
#   F.~García~Lorca \inst{\ref{ inst1 }}
# }
# 
# \institute{
#   Some institute \label{ inst1 }
# }
```

As a last resort, you can set an author's _spelling_ directly:

```python
authors.update_author_spelling('Federico García Lorca', 'Fe. García Lorca')

authors.Authors('Federico García Lorca').AandA()
# \author{
#   Fe.~García~Lorca \inst{\ref{ inst1 }}
# }
# 
# \institute{
#   Some institute \label{ inst1 }
# }
```

### Adding a new journal

It's very easy to add support for a new journal, by simply adding a new method
to the [`Authors`][authors.Authors] class. For example, to add support for JOSS,
we could do the following:

```python
from authors import Authors

def JOSS(self: Authors): # (1)
    ...
```

1.  This function will be added as a method to [`Authors`][authors.Authors],
    hence the `self` first argument.

and then simply inject the method into the [`Authors`][authors.Authors] class:

```python
Authors.JOSS = JOSS
```

which could then be used as follows:

```python
Authors('Your Name').JOSS()
# some output...
```

Feel free to [open an issue](https://github.com/j-faria/authors/issues) if you
want to add support for a new journal.



---
[^1]: Unfortunately, this does mean you would need to create a GitHub account.