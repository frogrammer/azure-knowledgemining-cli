import json
import os
import random

import azkm.utils.osutil as osutil
from azkm.providers.azurerm import (AzurermProvider, CognitiveAccount,
                                    KubernetesCluster, ResourceGroup,
                                    SearchService, StorageAccount)
from cdktf import App, TerraformOutput, TerraformStack, Token, TerraformVariable
from constructs import Construct

AZKM_DIR = os.path.join(os.path.expanduser ('~'), '.azkm')

def __get_out_dir(km_id: str):
    out_dir = os.path.join(AZKM_DIR, '{0}.out'.format(km_id))
    if not os.path.isdir(AZKM_DIR):
        os.mkdir(AZKM_DIR)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    return out_dir

def _clean_name(name: str):
    illegal_char = ['_', '-', ' ']
    for c in illegal_char:
        name = name.replace(c, '')
    return name

def _get_vars(km_id: str):
    out_dir = __get_out_dir(km_id)
    vars_file = os.path.join(out_dir, 'cdk.tf.json')
    if not os.path.isfile(vars_file):
        return {
            'env_id': km_id,
            'res_suffix': str(random.randint(0, 999999))
        }
    else:
        with open(vars_file, 'r') as f:
            vars = json.loads(f.read())['variable']
            env_id = [vars[k] for k in vars.keys() if 'envid' in k][0]
            env_id = [vars[k] for k in vars.keys() if 'envid' in k][0]
            return {
                'env_id': [vars[k]['default'] for k in vars.keys() if 'envid' in k][0],
                'env_suffix': [vars[k]['default'] for k in vars.keys() if 'suffix' in k][0]
            }


class KmStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

    def generate_baseline(self, km_id: str, region: str, tags: dict):
        vars = _get_vars(km_id)
        env_id = TerraformVariable(self, 'env_id', type='string', default=_clean_name(vars['env_id']))
        res_suf = TerraformVariable(self, 'env_suffix', type='string', default=_clean_name(vars['env_suffix']))

        def _name_resource(res: str):
            return '{0}{1}{2}'.format(env_id.string_value, res, res_suf.string_value)


        AzurermProvider(self, "Azurerm",
            features=[{}]
            )

        km_rg = ResourceGroup(self, _name_resource('rg'),
            name=_name_resource('rg'), 
            location = region,
            tags = tags
            )

        km_storage = StorageAccount(self, _name_resource('storage'),
            name=_name_resource('storage'),
            depends_on=[km_rg],
            resource_group_name=km_rg.name,
            location=km_rg.location, 
            account_tier='Standard',
            account_replication_type='GRS',
            tags=tags)

        km_text = CognitiveAccount(self, _name_resource('text'), 
            name=_name_resource('text'),
            depends_on=[km_rg],
            resource_group_name=km_rg.name,
            location=km_rg.location, 
            sku_name='S0',
            kind = 'TextAnalytics'
            )

        km_img = CognitiveAccount(self, _name_resource('img'), 
            name=_name_resource('img'),
            depends_on=[km_rg],
            resource_group_name=km_rg.name,
            location=km_rg.location, 
            sku_name='S1',
            kind = 'ComputerVision'
            )

        km_search = SearchService(self, _name_resource('search'), 
            name=_name_resource('search'),
            depends_on=[km_rg],
            resource_group_name=km_rg.name,
            location=km_rg.location, 
            sku='standard'
            )

        km_aks = KubernetesCluster(self, _name_resource('aks'), 
            name=_name_resource('aks'),
            depends_on=[km_rg],
            resource_group_name=km_rg.name,
            location=km_rg.location, 
            default_node_pool=[{
                'name': 'default',
                'nodeCount': 1,
                'vmSize': 'Standard_D4s_v3',
            }],
            dns_prefix='azkm',
            identity=[{
                'type': 'SystemAssigned'
            }]
            )

        TerraformOutput(self, 'rg_id', value=km_rg.id)
        TerraformOutput(self, 'storage_id', value=km_storage.id)
        TerraformOutput(self, 'storage_conn', value=km_storage.primary_connection_string)
        TerraformOutput(self, 'text_endpoint', value=km_text.endpoint)
        TerraformOutput(self, 'text_key', value=km_text.primary_access_key)
        TerraformOutput(self, 'img_endpoint', value=km_img.endpoint)
        TerraformOutput(self, 'img_key', value=km_img.primary_access_key)
        TerraformOutput(self, 'search_name', value=km_search.name)
        TerraformOutput(self, 'search_key', value=km_search.primary_key)
        TerraformOutput(self, 'aks_name', value=km_aks.name)



def synth_km(km_id: str, region: str):
    app = App(outdir=__get_out_dir(km_id))
    km_stack = KmStack(app, km_id)
    km_stack.generate_baseline(km_id, region, {'km_id': km_id})
    app.synth()
    return app.outdir


def init(km_id: str):
    out_dir = __get_out_dir(km_id)
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'init', '--upgrade'])


def apply(km_id: str):
    out_dir = __get_out_dir(km_id)
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'apply'])


def destroy(km_id: str):
    out_dir = __get_out_dir(km_id)
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'destroy'])

def get_state(km_id: str):
    out_dir = __get_out_dir(km_id)
    with open(os.path.join(out_dir,'terraform.tfstate'), 'r') as f:
        tfstate = json.loads(f.read())
        return tfstate

def get_envs():
    return [d.replace('.out', '') for d in os.listdir(AZKM_DIR)]