"""azkm CLI entry point."""

from azkm.flight_checks import prereqs
import firehelper
import sys
from azkm.commands import *  # noqa

def main():
    """azkm CLI.
    """
    if len(sys.argv) == 1:
        prereqs.confirm_cmd()
    else:
        prereqs.check_cmd()

    start_cli()

def start_cli():
    firehelper.start_fire_cli('azkm')

if __name__ == '__main__':
    main()
