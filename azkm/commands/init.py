import firehelper
from azkm.utils import tf

def init_km(km_id: str, region:str):
    tf.synth_km(km_id, region)
    tf.init(km_id)
    tf.apply(km_id)

init_cmd = {
    'init': init_km
}

firehelper.CommandRegistry.register(init_cmd)