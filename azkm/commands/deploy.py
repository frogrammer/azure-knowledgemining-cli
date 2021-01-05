"""CLI commands: fulmar deploy pipeline [ida]."""
import json

import requests
from azkm.utils import az
from firehelper import CommandRegistry

# Refactoring / DRY required

def deploy_imagenet(instance: str, region: str):
    """Deploy imagenet pipeline.

    Args:
        instance (str): Fulmar instance name
        region (str): Fulmar instance region
    """
    _, fulmar_store_conn = deploy_adls(instance, region)
    _, fulmar_search_keys = deploy_cogsearch(instance, region)
    _, fulmar_cogsvcs_keys = az.create_cognitiveservices()
    az.create_storage_container('imagenet')
    headers = {
        'Content-Type': 'application/json',
        'api-key': fulmar_search_keys['primaryKey']
    }
    endpoint = f'https://fulmar{instance}.search.windows.net/'
    api_version = '?api-version=2020-06-30'
    endpoint_datasources = f'{endpoint}datasources{api_version}'
    endpoint_indexers = f'{endpoint}indexers{api_version}'
    endpoint_indexes = f'{endpoint}indexes{api_version}'
    endpoint_skillsets = f'{endpoint}skillsets{api_version}'

    # get resources
    res_ds = requests.get(f'{endpoint_datasources}&$select=name', headers=headers)
    res_ds.raise_for_status()
    res_indexes = requests.get(f'{endpoint_indexes}&$select=name', headers=headers)
    res_indexes.raise_for_status()
    res_indexers = requests.get(f'{endpoint_indexers}&$select=name', headers=headers)
    res_indexers.raise_for_status()
    res_skillsets = requests.get(f'{endpoint_skillsets}&$select=name', headers=headers)
    res_skillsets.raise_for_status()

    # create ida datasource
    if not any(v['name'] == 'imagenet' for v in res_ds.json()['value']):
        print('datasource\tprovisioning')
        datasource = {}
        with open('./cli/configuration/imagenet/datasource.json', 'r') as idx_f:
            conn_str = fulmar_store_conn['connectionString']
            container = 'imagenet'
            ds_txt = idx_f.read()  # invalid first char
            ds_txt = ds_txt.replace('{{env_storage_connection_string}}', conn_str).replace('{{env_storage_container}}', container)
            datasource = json.loads(ds_txt)
        datasource['name'] = 'imagenet'
        res_ds = requests.post(endpoint_datasources, headers=headers, json=datasource)
        res_ds.raise_for_status()
        print('datasource\tcomplete')

    # create ida skillset
    if not any(v['name'] == 'imagenet' for v in res_skillsets.json()['value']):
        print('skillset\tprovisioning')
        skillset = {}
        with open('./cli/configuration/imagenet/skills.json', 'r') as sk_f:
            sk_txt = sk_f.read()[1:]  # invalid first char
            sk_txt = sk_txt.replace('{{cog_services_key}}', fulmar_cogsvcs_keys['key1'])
            skillset = json.loads(sk_txt)
        skillset['name'] = 'imagenet'
        res_s = requests.post(endpoint_skillsets, headers=headers, json=skillset)
        res_s.raise_for_status()
        print('skillset\tcomplete')

    # create ida index
    if not any(v['name'] == 'imagenet' for v in res_indexes.json()['value']):
        print('index\t\tprovisioning')
        index = {}
        with open('./cli/configuration/imagenet/index.json', 'r') as idx_f:
            idx_txt = idx_f.read()[1:]  # invalid first char
            index = json.loads(idx_txt)
        index['name'] = 'imagenet'
        res_idx = requests.post(endpoint_indexes, headers=headers, json=index)
        res_idx.raise_for_status()
        print('index\t\tcomplete')

    # create ida indexer
    if not any(v['name'] == 'imagenet' for v in res_indexers.json()['value']):
        print('indexer\t\tprovisioning')
        indexer = {}
        with open('./cli/configuration/imagenet/indexer.json', 'r') as idxr_f:
            idxr_txt = idxr_f.read()[1:].replace('{{datasource_name}}', 'imagenet').replace('{{index_name}}', 'imagenet').replace('{{skillset_name}}', 'imagenet')  # invalid first char
            indexer = json.loads(idxr_txt)
        indexer['name'] = 'imagenet'
        res_idxr = requests.post(endpoint_indexers, headers=headers, json=indexer)
        res_idxr.raise_for_status()
        print('indexer\t\tcomplete')


pipeline_commands = {
    "deploy": {
        "imagenet": deploy_imagenet
    }
}

CommandRegistry.register(pipeline_commands)
