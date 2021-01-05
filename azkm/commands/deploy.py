"""CLI commands: fulmar deploy pipeline [ida]."""
import json
import os
import requests
from urllib.parse import urljoin

from azkm.utils import tf
from azkm.utils import cogsearch
from azkm.utils import text
from firehelper import CommandRegistry

PIPELINE_URL = 'https://raw.githubusercontent.com/frogrammer/azkm-pipelines/master/pipelines.json'

PIPELINE_COMPONENTS = ['datasource', 'skillset', 'index', 'indexer']  # installation order

def _load_pipeline(url: str, pipeline_name: str, resource_attr: dict):
    p_res = requests.get(url)
    p_res.raise_for_status()
    p_components = p_res.json()
    if not pipeline_name in p_components or not all([p in p_components[pipeline_name] for p in PIPELINE_COMPONENTS]):
        raise Exception('Invalid pipeline json.')
    
    pipeline = {}
    for p in PIPELINE_COMPONENTS:
        comp_url = p_components[pipeline_name][p]
        if comp_url.startswith('.'):  # relative url
            comp_url = urljoin(url, comp_url)
        comp_res = requests.get(comp_url)
        comp_res.raise_for_status()
        res_txt = text.replace_tokens(comp_res.text, resource_attr)
        pipeline[p] = {}
        try:
            pipeline[p] = json.loads(res_txt)
        except:
            pipeline[p] = json.loads(res_txt[1:])

    return pipeline



def deploy_pipeline(pipeline: str, km_id: str, pipeline_url = PIPELINE_URL):
    """Deploy pipeline.

    Args:
        km_id (str): azkm instance name
    """
    try:
        env_state = tf.get_state(km_id)
    except:
        raise Exception('Error finding search appliance or cognitive services for environment {0}'.format(km_id))    

    pipeline_resources = _load_pipeline(pipeline_url, pipeline, env_state)
    
    for p in PIPELINE_COMPONENTS:
        cogsearch.create_resource(p, pipeline, env_state['azurerm_search_service'], pipeline_resources[p])
        
    print('\r\nDeployed imagenet pipeline to environment {0}.'.format(km_id))


pipeline_commands = {
    "deploy": {
        "pipeline": deploy_pipeline
    }
}

CommandRegistry.register(pipeline_commands)
