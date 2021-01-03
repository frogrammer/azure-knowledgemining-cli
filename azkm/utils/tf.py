from typing import NamedTuple
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, Token
from azkm.providers.azurerm import AzurermProvider, ResourceGroup, StorageAccount, CognitiveAccount, SearchService, KubernetesCluster

import azkm.utils.osutil as osutil
import os

def _name_resource(km_id: str, prefix: str):
    illegal_char = ['_', '-', ' ']
    name = '{0}{1}'.format(prefix, km_id)
    for c in illegal_char:
        name = name.replace(c, '')
    return name


class KmStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

    def generate_baseline(self, km_id: str, region: str, tags: dict):
        
        AzurermProvider(self, "Azurerm",
            features=[{}]
            )

        km_rg = ResourceGroup(self, _name_resource(km_id, 'rg'),
            name=_name_resource(km_id, 'rg'), 
            location = region,
            tags = tags
            )

        km_storage = StorageAccount(self, _name_resource(km_id, 'storage'),
            name=_name_resource(km_id, 'storage'),
            depends_on=[km_rg],
            resource_group_name=Token().as_string(km_rg.name),
            location=km_rg.location, 
            account_tier='Standard',
            account_replication_type='GRS',
            tags=tags)

        km_text = CognitiveAccount(self, _name_resource(km_id, 'text'), 
            name=_name_resource(km_id, 'text'),
            depends_on=[km_rg],
            resource_group_name=Token().as_string(km_rg.name),
            location=km_rg.location, 
            sku_name='S0',
            kind = 'TextAnalytics'
            )

        km_img = CognitiveAccount(self, _name_resource(km_id, 'img'), 
            name=_name_resource(km_id, 'img'),
            depends_on=[km_rg],
            resource_group_name=Token().as_string(km_rg.name),
            location=km_rg.location, 
            sku_name='S1',
            kind = 'ComputerVision'
            )

        km_search = SearchService(self, _name_resource(km_id, 'search'), 
            name=_name_resource(km_id, 'search'),
            depends_on=[km_rg],
            resource_group_name=Token().as_string(km_rg.name),
            location=km_rg.location, 
            sku='standard'
            )

        TerraformOutput(self, 'rg_id', value=km_rg.id)
        TerraformOutput(self, 'storage_id', value=km_storage.id)
        TerraformOutput(self, 'storage_conn', value=km_storage.primary_connection_string)
        TerraformOutput(self, 'text_endpoint', value=km_text.endpoint)
        TerraformOutput(self, 'text_key', value=km_text.primary_access_key)
        TerraformOutput(self, 'img_endpoint', value=km_img.endpoint)
        TerraformOutput(self, 'img_key', value=km_img.primary_access_key)
        TerraformOutput(self, 'km_id', value=km_search.id)
        TerraformOutput(self, 'km_key', value=km_search.primary_key)


def __get_out_dir(km_id: str):
    return os.path.join(osutil.ROOT_DIR, '{0}.out'.format(km_id))
 
def synth_km(km_id: str, region: str):
    app = App(outdir=__get_out_dir(km_id))
    km_stack = KmStack(app, km_id)
    km_stack.generate_baseline(km_id, region, {'km_id': km_id})
    app.synth()
    return app.outdir


def init(out_dir: str):
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'init', '--upgrade'])


def apply(out_dir: str):
    osutil.chdir(out_dir)
    osutil.run_subprocess(['terraform', 'apply'])


def destroy(km_id: str):
    out_dir = '{0}.out'.format(km_id)
    osutil.run_subprocess(['terraform', 'destroy'])