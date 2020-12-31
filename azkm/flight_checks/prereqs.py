import shutil
from tabulate import tabulate

prereq_cmd = [
    'terraform',
    'kubectl'
]

def check_cmd():
    prereq_paths = []
    for cmd in prereq_cmd:
        cmd_path = shutil.which(cmd)
        assert cmd_path is not None, 'Please install {0}'.format(cmd)
        prereq_paths = prereq_paths + [(cmd, cmd_path)]
    return prereq_paths

def confirm_cmd():
    prereqs = check_cmd()
    print('Pre-requisites:')
    print(tabulate(prereqs, headers=['cmd', 'path']))
    print('\r\n')