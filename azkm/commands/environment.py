import firehelper
from azkm.utils import tf
from azkm.utils import text
from tabulate import tabulate

def read(km_id: str):
    state = text.flatten_dict(tf.get_state(km_id))
    state_tabular = [['resource', 'value']]
    for k in state:
        state_tabular = state_tabular + [[k, state[k]]]
    print(tabulate(state_tabular, headers='firstrow'))

def list_env():
    print(tabulate([[env] for env in tf.get_envs()]))

env_cmd = {
    'environment': {
        'show': read,
        'list': list_env
    }
}

firehelper.CommandRegistry.register(env_cmd)