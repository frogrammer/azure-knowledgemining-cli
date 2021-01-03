import firehelper
from azkm.utils import tf

def init_km(km_id: str, region:str):
    out_dir = tf.synth_km(km_id, region)
    tf.init(out_dir)
    tf.apply(out_dir)

init_cmd = {
    'init': init_km
}

firehelper.CommandRegistry.register(init_cmd)