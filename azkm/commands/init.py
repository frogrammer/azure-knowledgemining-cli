import firehelper
from azkm.utils import tf

def plan_km(km_id: str, region:str):
    tf.synth_km(km_id, region)
    tf.init(km_id)
    tf.plan(km_id)

def deploy_km(km_id: str, region:str):
    tf.synth_km(km_id, region)
    tf.init(km_id)
    tf.apply(km_id)

init_cmd = {
    'init': deploy_km
}

firehelper.CommandRegistry.register(init_cmd)