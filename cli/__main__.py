"""azkm CLI entry point."""

from .commands import *  # noqa
from .flight_checks import prereqs
import firehelper

def main():
    """azkm CLI.
    """
    prereqs.check_cmd()
    firehelper.start_fire_cli('azkm')


if __name__ == '__main__':
    main()
