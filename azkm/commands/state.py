import firehelper
from azkm.utils import tf
from tabulate import tabulate

def read(km_id: str):
    print(tabulate(tf.get_state(km_id)['outputs']))

state_cmd = {
    'state': {
        'read': read
    }
}

firehelper.CommandRegistry.register(state_cmd)