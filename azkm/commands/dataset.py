"""CLI commands: fulmar deploy dataset [imagenet, cord19]."""
import io
import os
import random
import tarfile

import azure.core.exceptions
import requests
from azure.storage.blob import BlobClient
from clint.textui import progress
from firehelper import CommandRegistry

from azkm.utils import tf
from azkm.utils.stdout import stdout_print

CORD19_URL = 'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_2020-10-12.tar.gz'
OBL_URL = 'https://abbottabad-compound-material.s3.amazonaws.com/Everything.20171105.tgz'
ENRON_URL = 'https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tar.gz'


def deploy_imagenet(km_id: str, synset_id: str = None, num_images: int = 1000):
    """Deploy imagenet sample to a container.

    Args:
        km_id (str): azkm environment id
        synset_id (str, optional): imagenet synset id. Defaults to None.
        num_images (int, optional): number of images to download. Defaults to 1000.
    """
    try:
        env_state = tf.get_state(km_id)
        storage_conn = env_state['azurerm_storage_account'][0]['primary_blob_connection_string']
    except Exception as e:
        raise Exception('Error finding storage for environment {0}.'.format(km_id))
    img_count = 0
    while img_count < num_images:
        if not synset_id:
            # pick random synset
            syn_res = requests.get('http://www.image-net.org/api/text/imagenet.synset.obtain_synset_list')
            syn_res.raise_for_status()
            synset = syn_res.text.split('\n')
            synset_id = random.choice(synset)

        image_urls_res = requests.get(f'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid={synset_id}')
        image_urls_res.raise_for_status
        images_to_fetch = image_urls_res.text.split('\r\n')[:-1][:num_images - img_count]
        print(f'fetching {len(images_to_fetch)} images from synset {synset_id}')
        for img_url in images_to_fetch:
            with io.BytesIO() as b_io:
                try:
                    counter = f'{img_count}/{num_images}'
                    spaces = 16 - len(counter)
                    stdout_print(f'{img_count}/{num_images}{"".join([" " for i in range(spaces)])}{img_url[:50]}')
                    res = requests.get(img_url, timeout=10)
                    if res.headers['Content-Type'][:5] == 'image':
                        b_io.write(res.content)
                        b_io.seek(0)
                        blob_name = f'imagenet/{synset_id}/{img_url.split("/")[-1]}'
                        with BlobClient.from_connection_string(conn_str=storage_conn, container_name='imagenet', blob_name=blob_name) as blob:
                            try:
                                blob.upload_blob(b_io)
                            except azure.core.exceptions.ResourceExistsError:
                                pass
                        img_count = img_count + 1
                    else:
                        stdout_print(f'not image\t{img_url[:50]}')
                except Exception as e:
                    stdout_print(f'error\t\t{img_url[:50]}')
                    pass
        synset_id = None
    print(f'{num_images} images fetched.')


dataset_commands = {
    "dataset": {
        "imagenet": deploy_imagenet
    }
}

CommandRegistry.register(dataset_commands)
