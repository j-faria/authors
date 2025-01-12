from argparse import ArgumentParser
from .authors import Authors
from .authors import delete_author, update_author_email, update_author_name, update_author_orcid


def cli_authors():
    parser = ArgumentParser()
    parser.add_argument('file', type=str)
    parser.add_argument('-j', '--jornal', type=str, 
                        default='aanda', choices=['aanda', 'mnras'])
    parser.add_argument('-p', '--preview', action='store_true')
    args = parser.parse_args()
    
    a = Authors(args.file)
    if args.jornal == 'aanda':
        a.AandA(preview=args.preview)
    elif args.jornal == 'mnras':
        a.MNRAS(preview=args.preview)

def cli_update_author_name():
    doc = update_author_name.__doc__.split('\n')[0]
    parser = ArgumentParser(description=doc)
    parser.add_argument('old_name', type=str)
    parser.add_argument('new_name', type=str)
    args = parser.parse_args()
    update_author_name(args.old_name, args.new_name)


def cli_update_author_email():
    doc = update_author_email.__doc__.split('\n')[0]
    parser = ArgumentParser(description=doc)
    parser.add_argument('author', type=str)
    parser.add_argument('email', type=str)
    args = parser.parse_args()
    update_author_email(args.author, args.email)


def cli_update_author_orcid():
    doc = update_author_orcid.__doc__.split('\n')[0]
    parser = ArgumentParser(description=doc)
    parser.add_argument('author', type=str)
    parser.add_argument('orcid', type=str)
    args = parser.parse_args()
    update_author_orcid(args.author, args.orcid)


def cli_delete_author():
    doc = delete_author.__doc__.split('\n')[0]
    parser = ArgumentParser(description=doc)
    parser.add_argument('author', type=str)
    args = parser.parse_args()
    delete_author(args.author)
