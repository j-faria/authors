<div align="center">
  
![](authors/crowd.png)

 ## the [list](https://github.com/j-faria/authors/blob/main/authors/data/all_known_authors.yml) of known authors is **public!**

[![badge][rna]][rna-link]

| [![badge][uan]][uan-link] | [![badge][uae]][uae-link] | [![badge][uao]][uao-link] | 
|---------------------------------------|---|---|

[![badge][da]][da-link]

</div>

[rna]: https://img.shields.io/badge/Register-New%20Author-green?style=for-the-badge
[rna-link]: https://github.com/j-faria/authors/actions/workflows/register_new_author.yml


[uan]: https://img.shields.io/badge/Update-Author%20Name-orange?style=for-the-badge
[uan-link]: https://github.com/j-faria/authors/actions/workflows/update_author_name.yml

[uae]: https://img.shields.io/badge/Update-Author%20Email-orange?style=for-the-badge
[uae-link]: https://github.com/j-faria/authors/actions/workflows/update_author_email.yml

[uao]: https://img.shields.io/badge/Update-Author%20ORCID-orange?style=for-the-badge
[uao-link]: https://github.com/j-faria/authors/actions/workflows/update_author_orcid.yml

[da]: https://img.shields.io/badge/Delete-Author-red?style=for-the-badge
[da-link]: https://github.com/j-faria/authors/actions/workflows/delete_author.yml


### Installation

```
pip install authors
```


### Simple use

```python
>>> from authors import Authors
>>> Authors('list.txt').AandA()
```
```
\author{
  J.~P.~Faria \inst{\ref{geneva}} \orcidlink{0000-0002-6728-244X}
}

\institute{
  Observatoire Astronomique de l'Université de Genève, Chemin Pegasi 51b, 1290 Versoix, Switzerland \label{geneva}
}
```


