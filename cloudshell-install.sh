#!/bin/bash
pip install nodeenv
nodeenv azkm
pip install azkm
echo '' > ~/start_azkm.sh
echo 'source ~/azkm/bin/activate' >  ~/start_azkm.sh
echo 'azkm' >  ~/start_azkm.sh
source ~/start_azkm.sh