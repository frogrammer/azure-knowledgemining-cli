import subprocess
import os
import azkm

ROOT_DIR = '/'.join(azkm.__file__.split('/')[:-2])

def chdir(rel_dir: str = ''):    
    os.chdir(os.path.join(ROOT_DIR, rel_dir))

def run_subprocess(cmd: list):
    subprocess.run(cmd)