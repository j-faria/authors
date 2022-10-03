import pytest
from authors.authors import get_all_known_authors


def test_known_authors():
    aka = get_all_known_authors()
    assert len(aka) >= 1, 'should know at least one author'


def test_Faria():
    aka = get_all_known_authors()
    assert 'João P. Faria' in aka, 'this author should be known...'
