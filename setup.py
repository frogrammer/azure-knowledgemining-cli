from setuptools import setup, find_packages
from os import path

# https://packaging.python.org/guides/making-a-pypi-friendly-readme/
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='azure-knowledgemining-cli',
    version=0.6,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/frogrammer/azure-knowledgemining-cli',
    author='Luke Vinton',
    author_email='luke0vinton@gmail.com',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=['fire', 'azure-cli==2.14.0', 'azure-mgmt-core==1.2.0', 'azure-storage-blob', 'fire-cli-helper', 'cdktf', 'tabulate'],
    tests_require=[],
    classifiers=[],
    test_suite='',
    entry_points={
        'console_scripts': [
            'azkm = azkm.__main__:main',
        ]
    },
    package_data={
        '': ['*.json', '*.tgz']
    },
    include_package_data=True
)
