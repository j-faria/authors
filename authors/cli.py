from argparse import ArgumentParser
from .authors import update_author_email


def cli_update_author_email():
    doc = update_author_email.__doc__.split('\n')[0]
    parser = ArgumentParser(description=doc)
    parser.add_argument('author', type=str)
    parser.add_argument('email', type=str)
    args = parser.parse_args()
    update_author_email(args.author, args.email)

