"""azkm CLI entry point."""

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
    
    prereqs.get_providers()
    start_cli()

def start_cli():
    from .commands import init, destroy  # noqa
    firehelper.start_fire_cli('azkm')

if __name__ == '__main__':
    main()