import shutil

prereq_cmd = [
    'terraform',
    'kubectl'
]

def check_cmd():
    for cmd in prereq_cmd:
        assert shutil.which(cmd) is not None, 'Please install {0}'.format(cmd)