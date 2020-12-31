"""azkm CLI entry point."""

from .commands import *  # noqa
from .flight_checks import prereqs
import firehelper
import sys

def main():
    """azkm CLI.
    """
    if len(sys.argv) == 1:
        prereqs.confirm_cmd()
    else:
        prereqs.check_cmd()
        
    firehelper.start_fire_cli('azkm')


if __name__ == '__main__':
    main()
