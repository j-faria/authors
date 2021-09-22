""" authors """

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the version from authors/version.py
version = {}
with open("authors/version.py") as fp:
    exec(fp.read(), version)
    __version__ = version['__version__']

setup(
    name='authors',
    version=__version__,
    description=' Authors of your next scientific article',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/j-faria/authors',
    author='João Faria',
    author_email='joao.faria@astro.up.pt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),
    zip_safe=False,
    install_requires=['pyperclip'],
)
