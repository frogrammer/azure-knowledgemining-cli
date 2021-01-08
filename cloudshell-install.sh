#!/bin/bash
pip install nodeenv
nodeenv azkm
pip install azkm
echo '' > ~/start_azkm.sh
echo 'source ~/azkm/bin/activate' >>  ~/start_azkm.sh
echo 'azkm' >>  ~/start_azkm.sh
echo 'run ~/start_azkm.sh to run azkm in nodejs virtualenv.'