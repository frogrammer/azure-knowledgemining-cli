"""CLI commands: fulmar deploy pipeline [ida]."""
import json
import os
import requests
from urllib.parse import urljoin

from azkm.utils import az
from azkm.utils import tf
from azkm.utils import cogsearch
from azkm.utils import text
from azkm.utils import osutil
from azkm.utils import zip
from firehelper import CommandRegistry

# TODO: rethink pipeline/application deployment config + pattern


PIPELINE_URL = 'https://raw.githubusercontent.com/frogrammer/azkm-pipelines/master/pipelines.json'
PIPELINE_COMPONENTS = ['datasource', 'skillset', 'index', 'indexer']  # installation order
APP_COMPONENTS = ['app_bin', 'app_template']
FILES_TO_TOKEN_REPLACE = ['.json', '.yaml']

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

def _load_application(url: str, pipeline_name: str, resource_attr: dict, km_id: str):
    p_res = requests.get(url)
    p_res.raise_for_status()
    p_components = p_res.json()
    if not pipeline_name in p_components or not all([p in p_components[pipeline_name] for p in APP_COMPONENTS]):
        raise Exception('Invalid pipeline json.')
    
    pipeline_app_root = os.path.join(tf.get_out_dir(km_id), pipeline_name)

    if not os.path.isdir(pipeline_app_root):
        os.mkdir(pipeline_app_root)

    app = {}
    for p in APP_COMPONENTS:
        comp_url = p_components[pipeline_name][p]
        if comp_url.startswith('.'):  # relative url
            comp_url = urljoin(url, comp_url)
        comp_res = requests.get(comp_url)
        comp_res.raise_for_status()
        if comp_url.endswith('.zip'):
            path = os.path.join(pipeline_app_root, comp_url.split('/')[-1].replace('.zip', ''))
            zip.extract_all(comp_res.content, path)
            for root, dirs, files in os.walk(path):
                for file in files:
                    if any([file.endswith(ext) for ext in FILES_TO_TOKEN_REPLACE]):
                        file_path = os.path.join(root, file)
                        file_txt = ''
                        with open(file_path, 'r') as f:
                            file_txt = text.replace_tokens(f.read(), resource_attr)
                        with open(file_path, 'w') as f:
                            f.write(file_txt)
            app[p] = path
        else: 
            file_name = os.path.join(pipeline_app_root, comp_url.split('/')[-1])
            res_txt = comp_res.text
            if any([file_name.endswith(ext) for ext in FILES_TO_TOKEN_REPLACE]):
                res_txt = text.replace_tokens(comp_res.text, resource_attr)
            with open(file_name, 'w') as f:
                f.write(res_txt)
            app[p] = file_name

    return app

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
        cogsearch.create_resource(p, pipeline, env_state['azurerm_search_service'][0], pipeline_resources[p])
        
    print('\r\nDeployed imagenet pipeline to environment {0}.'.format(km_id))


def deploy_application(pipeline: str, km_id: str, pipeline_url = PIPELINE_URL):
    """Deploy application.

    Args:
        km_id (str): azkm instance name
    """
    try:
        env_state = tf.get_state(km_id)
    except:
        raise Exception('Error finding search appliance or cognitive services for environment {0}'.format(km_id))    

    app_resources = _load_application(pipeline_url, pipeline, env_state, km_id)
    
    # copy azkm resources to file share
    az.run_command('storage', 'file', 'upload-batch', 
        '--account-name', env_state['azurerm_storage_account'][0]['name'], 
        '--account-key', env_state['azurerm_storage_account'][0]['primary_access_key'], 
        '-s', tf.get_out_dir(km_id), 
        '-d', 'kmapp')
    
    # kubectl deploy app_template
    if app_resources['app_template']:
        osutil.run_subprocess(['az', 'aks', 'get-credentials', 
        '-n', env_state['azurerm_kubernetes_cluster'][0]['name'], 
        '-g', env_state['azurerm_resource_group'][0]['name']
        ])
        osutil.run_subprocess(['kubectl', 'create', 'secret', 'generic', 'azure-secret', 
        '--from-literal=azurestorageaccountname={0}'.format(env_state['azurerm_storage_account'][0]['name']), 
        '--from-literal=azurestorageaccountkey={0}'.format(env_state['azurerm_storage_account'][0]['primary_access_key'])])
        osutil.run_subprocess(['kubectl', 'apply', '-f', app_resources['app_template']])


    print('\r\nDeployed imagenet app to environment {0}.'.format(km_id))

pipeline_commands = {
    "deploy": {
        "pipeline": deploy_pipeline,
        "app": deploy_application
    }
}

CommandRegistry.register(pipeline_commands)
