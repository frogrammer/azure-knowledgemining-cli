import requests
from azkm.utils.stdout import stdout_print

API_VERSION = '2020-06-30'

def create_resource(component_name: str, resource_name: str, search_attr: dict, resource_attr: dict):
    stdout_print('provisioning {0} {1} in search {2}.'.format(component_name, resource_name, search_attr['name']))
    headers = {
        'Content-Type': 'application/json',
        'api-key': search_attr['primary_key']
    }
    # pluralise
    last_char = component_name[-1]
    if last_char is not 's':
        if last_char is 'x':
            component_name = component_name + 'e'
        component_name = component_name + 's'

    resource_attr['name'] = resource_name
    res_endpoint = 'https://{0}.search.windows.net/{1}?api-version={2}'.format(search_attr['name'], component_name, API_VERSION)
    check_res = requests.get('{0}&$select=name'.format(res_endpoint), headers=headers)
    check_res.raise_for_status()
    if 'value' in check_res.json() and any(v['name'] == resource_name for v in check_res.json()['value']):
        stdout_print('resource {0} with name {1} already exists in search {2}.'.format(component_name, resource_name, search_attr['name']))
        # raise Exception('{0} already exists for {1} in search appliance {2}'.format(component_name, resource_name, search_attr['name']))
    else:
        requests.post(res_endpoint, headers=headers, json=resource_attr).raise_for_status()
        stdout_print('created resource {0} with name {1} in search {2}.'.format(component_name, resource_name, search_attr['name']))
        
    
def create_datasource(resource_name: str, search_attr: dict, resource_attr: dict):
    return create_resource('datasources', resource_name, search_attr, resource_attr)

def create_index(resource_name: str, search_attr: dict, resource_attr: dict):
    return create_resource('indexes', resource_name, search_attr, resource_attr)

def create_indexer(resource_name: str, search_attr: dict, resource_attr: dict):
    return create_resource('indexers', resource_name, search_attr, resource_attr)

def create_skillset(resource_name: str, search_attr: dict, resource_attr: dict):
    return create_resource('skillsets', resource_name, search_attr, resource_attr)
