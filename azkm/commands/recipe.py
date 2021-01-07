from firehelper import CommandRegistry
from azkm.commands import init, deploy, dataset

def deploy_imagenet(km_id: str, region:str):
    init.deploy_km(km_id, region)
    deploy.deploy_pipeline("imagenet", km_id)
    dataset.deploy_imagenet(km_id, num_images=10)
    deploy.deploy_application("imagenet", km_id)
    
recipes = {
    'recipe': {
        'imagenet': deploy_imagenet
    }
}

CommandRegistry.register(recipes)