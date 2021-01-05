"""CLI commands: fulmar deploy pipeline [ida]."""
import json
import os
import requests
from azkm.utils import tf
from azkm.utils import cogsearch
from firehelper import CommandRegistry

ROOT_PATH = '/'.join(os.path.dirname(os.path.realpath(__file__)).split('/')[:-1])
CFG_PATH = os.path.join(ROOT_PATH,'configuration')
IMAGENET_PATH = os.path.join(CFG_PATH, 'imagenet')

def deploy_imagenet(km_id: str,):
    """Deploy imagenet pipeline.

    Args:
        km_id (str): azkm instance name
    """
    try:
        env_state = tf.get_state(km_id)
        search_attr = [r for r in env_state['resources'] if r['type'] == 'azurerm_search_service'][0]['instances'][0]['attributes']
        cogsvcs_attr = [r for r in env_state['resources'] if r['type'] == 'azurerm_cognitive_account'][0]['instances'][0]['attributes']
        storage_attr = [r for r in env_state['resources'] if r['type'] == 'azurerm_storage_account'][0]['instances'][0]['attributes']
        storage_conn = storage_attr['primary_blob_connection_string']
    except:
        raise Exception('Error finding search appliance or cognitive services for environment {0}'.format(km_id))

    # datasource
    with open('{0}/datasource.json'.format(IMAGENET_PATH), 'r') as f:
        ds_txt = f.read()  # invalid first char
        ds_txt = ds_txt.replace('{{env_storage_connection_string}}', storage_conn).replace('{{env_storage_container}}', 'imagenet')
        datasource = json.loads(ds_txt)
        cogsearch.create_datasource('imagenet', search_attr, datasource)

    # skillset
    with open('{0}/skills.json'.format(IMAGENET_PATH), 'r') as f:
        sk_txt = f.read()[1:]  # invalid first char
        sk_txt = sk_txt.replace('{{cog_services_key}}', cogsvcs_attr['primary_access_key'])
        skillset = json.loads(sk_txt)
        cogsearch.create_skillset('imagenet', search_attr, skillset)
        
    # index
    with open('{0}/index.json'.format(IMAGENET_PATH), 'r') as f:
        idx_txt = f.read()[1:]  # invalid first char
        index = json.loads(idx_txt)
        cogsearch.create_index('imagenet', search_attr, index)

    # indexer
    with open('{0}/indexer.json'.format(IMAGENET_PATH), 'r') as f:
        idxr_txt = f.read()[1:].replace('{{datasource_name}}', 'imagenet').replace('{{index_name}}', 'imagenet').replace('{{skillset_name}}', 'imagenet')  # invalid first char
        indexer = json.loads(idxr_txt)
        cogsearch.create_indexer('imagenet', search_attr, indexer)
    
    print('\r\nDeployed imagenet pipeline to environment {0}.'.format(km_id))

pipeline_commands = {
    "deploy": {
        "imagenet": deploy_imagenet
    }
}

CommandRegistry.register(pipeline_commands)
