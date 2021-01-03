import firehelper
from azkm.utils import tf
from tabulate import tabulate

def read(km_id: str):
    print(tabulate(tf.get_state(km_id)['outputs']))

def list_env():
    print(tabulate([[env] for env in tf.get_envs()]))

state_cmd = {
    'state': {
        'read': read,
        'list': list_env
    }
}

firehelper.CommandRegistry.register(state_cmd)