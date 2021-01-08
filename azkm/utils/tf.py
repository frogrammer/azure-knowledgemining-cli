import json
import os
import random
import shutil

from azkm.utils import az
import azkm.utils.osutil as osutil
from azkm.providers.azurerm import (AzurermProvider, CognitiveAccount,
                                    KubernetesCluster, ResourceGroup,
                                    SearchService, StorageAccount, StorageContainer, StorageShare)
from cdktf import App, TerraformOutput, TerraformStack, TerraformVariable
from constructs import Construct

AZKM_DIR = os.path.join(os.path.expanduser ('~'), '.azkm')

def get_out_dir(km_id: str):
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

def _get_envvars(km_id: str):
    out_dir = get_out_dir(km_id)
    vars_file = os.path.join(out_dir, 'cdk.tf.json')
    if not os.path.isfile(vars_file):
        return {
            'env_id': km_id,
            'env_suffix': str(random.randint(0, 999999))
        }
    else:
        with open(vars_file, 'r') as f:
            vars = json.loads(f.read())['variable']
            
            def __get_var(var: str):
                candidates = [vars[k]['default'] for k in vars.keys() if var in k]
                if len(candidates):
                    return candidates[0]
                else:
                    return ''

            return {
                'env_id': __get_var('envid'),
                'env_suffix': __get_var('suffix'),
                'sp_app_id': __get_var('spappid'),
                'sp_obj_id': __get_var('spobjid'),
                'sp_secret': __get_var('spsecret')
            }

def _create_sp(km_id: str, suffix: str):
    assert az.logged_in(), 'please log into az cli with desired tenant, subscription and identity.'
    return az.create_sp('{0}{1}'.format(km_id, suffix))

class KmStack(TerraformStack):

    vars: dict = {}
    tfvars: dict = {}
    resources: dict = {}

    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

    def generate_vars(self, km_id: str, region: str):
        self.vars = _get_envvars(km_id)
        self.vars['env_id'] = km_id
        self.vars['env_region'] = region

        if 'sp_secret' not in self.vars:
            sp = _create_sp(self.vars['env_id'], self.vars['env_suffix'])
            self.vars['sp_app_id'] = sp['appId']
            self.vars['sp_obj_id'] = sp['objectId']
            self.vars['sp_secret'] = sp['password']

        self.tfvars['env_id'] = TerraformVariable(self, 'env_id', type='string', default=_clean_name(self.vars['env_id']))
        self.tfvars['env_region'] = TerraformVariable(self, 'env_region', type='string', default=self.vars['env_region'])
        self.tfvars['env_suffix'] = TerraformVariable(self, 'env_suffix', type='string', default=_clean_name(self.vars['env_suffix']))
        self.tfvars['sp_app_id'] = TerraformVariable(self, 'sp_app_id', type='string', default=self.vars['sp_app_id'])
        self.tfvars['sp_obj_id'] = TerraformVariable(self, 'sp_obj_id', type='string', default=self.vars['sp_obj_id'])
        self.tfvars['sp_secret'] = TerraformVariable(self, 'sp_secret', type='string', default=self.vars['sp_secret'])


    def generate_baseline(self, tags: dict):
    
        def _name_resource(res: str):
            return '{0}{1}{2}'.format(self.tfvars['env_id'].string_value, _clean_name(res), self.tfvars['env_suffix'].string_value)


        AzurermProvider(self, "Azurerm",
            features=[{}]
            )

        self.resources['rg'] = ResourceGroup(self, _name_resource('rg'),
            name=_name_resource('rg'), 
            location = self.vars['env_region'],
            tags = tags
            )

        self.resources['storage'] = StorageAccount(self, _name_resource('stor'),
            name=_name_resource('stor'),
            depends_on=[self.resources['rg']],
            resource_group_name=self.resources['rg'].name,
            location=self.resources['rg'].location, 
            account_tier='Standard',
            account_replication_type='GRS',
            tags=tags)

        self.resources['container_imagenet'] = StorageContainer(self, 'imagenet',
            name='imagenet',
            depends_on=[self.resources['storage']],
            storage_account_name  = self.resources['storage'].name,
            container_access_type = "private")

        self.resources['share_kmapp'] = StorageShare(self, 'kmapp',
            name='kmapp',
            depends_on=[self.resources['storage']],
            storage_account_name  = self.resources['storage'].name,
        )

        self.resources['cogsvcs'] = CognitiveAccount(self, _name_resource('cogsvcs'), 
            name=_name_resource('cogsvcs'),
            depends_on=[self.resources['rg']],
            resource_group_name=self.resources['rg'].name,
            location=self.resources['rg'].location, 
            sku_name='S0',
            kind = 'CognitiveServices'
            )

        self.resources['search'] = SearchService(self, _name_resource('search'), 
            name=_name_resource('search'),
            depends_on=[self.resources['rg']],
            resource_group_name=self.resources['rg'].name,
            location=self.resources['rg'].location, 
            sku='basic'
            )

        self.resources['aks'] = KubernetesCluster(self, _name_resource('aks'), 
            name=_name_resource('aks'),
            depends_on=[self.resources['rg']],
            resource_group_name=self.resources['rg'].name,
            location=self.resources['rg'].location, 
            default_node_pool=[{
                'name': 'default',
                'nodeCount': 1,
                'vmSize': 'Standard_D4s_v3',
            }],
            dns_prefix='azkm',
            service_principal=[{
                'clientId': self.vars['sp_app_id'],
                'clientSecret': self.vars['sp_secret']
            }],
            addon_profile=[{
                'httpApplicationRouting': [{
                    'enabled': True
                }],
                'kubeDashboard': [{
                    'enabled': True
                }]
            }]
        )

        return self.resources

    def generate_outputs(self):
        return [TerraformOutput(self, r, value=self.resources[r].id) for r in self.resources]

def synth_km(km_id: str, region: str):
    app = App(outdir=get_out_dir(km_id))
    km_stack = KmStack(app, km_id)
    km_stack.generate_vars(km_id, region)
    km_stack.generate_baseline({'azkmid': km_id})
    km_stack.generate_outputs()
    app.synth()
    return app.outdir

def init(km_id: str):
    out_dir = get_out_dir(km_id)
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'init', '--upgrade'])

def plan(km_id: str):
    out_dir = get_out_dir(km_id)
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'plan'])

def apply(km_id: str):
    out_dir = get_out_dir(km_id)
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'apply'])

def destroy(km_id: str):
    out_dir = get_out_dir(km_id)
    vars = _get_envvars(km_id)
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'destroy'])
    if 'sp_obj_id' in vars and vars['sp_obj_id']:
        az.delete_sp(vars['sp_obj_id'])
    shutil.rmtree(out_dir)

def refresh(km_id: str):
    out_dir = get_out_dir(km_id)
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'refresh'])

def get_state(km_id: str):
    refresh(km_id)
    out_dir = get_out_dir(km_id)
    out_state = {}
    with open(os.path.join(out_dir,'terraform.tfstate'), 'r') as f:
        tfstate = json.loads(f.read())
        for r in tfstate['resources']:
            __ = out_state[r['type']] if r['type'] in out_state else []
            out_state[r['type']] = __ + [i['attributes'] for i in r['instances']]
        return out_state

def get_envs():
    if os.path.isdir(AZKM_DIR):
        return [d.replace('.out', '') for d in os.listdir(AZKM_DIR)]
    else:
        return None
