import firehelper
from azkm.utils import tf

def destroy_km(km_id: str):
    tf.destroy(km_id)

destroy_cmd = {
    'destroy': destroy_km
}

firehelper.CommandRegistry.register(destroy_cmd)