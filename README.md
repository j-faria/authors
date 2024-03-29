<div align="center">

![](authors/crowd.png)

</div>

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
  J. P. Faria \inst{\ref{ia-porto}, \ref{ia-fcup}} 
}
\institute{
  Instituto de Astrofísica e Ciências do Espaço Universidade do Porto, CAUP, Rua das Estrelas, 4150-762 Porto, Portugal \label{ia-porto} \and
  Departamento de Física e Astronomia, Faculdade de Ciências, Universidade do Porto, Rua Campo Alegre, 4169-007 Porto, Portugal \label{ia-fcup}
}
```

### Add yourself

Feel free to open [an issue](https://github.com/j-faria/authors/issues) or a [pull request](https://github.com/j-faria/authors/pulls) to add yourself to the (**public!**) [list](https://github.com/j-faria/authors/blob/main/authors/data/all_known_authors.yml) of known authors.
