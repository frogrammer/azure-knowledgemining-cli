# azure-knowledgemining-cli
azkm is a cli tool to deploy azure knowledge mining solutions with cognitive skills and applicable datasets.

 # commands
```bash
azkm [cmd] [sub-cmd] [parameters]

```
|cmd|sub-cmd|parameters|description|
|---|---|---|---|
|init||km_id: environment name</br>region: environment region||
|destroy||km_id: environment name||
|state|read|km_id: environment name||
|state|list|||

# installation
To use on azure cloud shell:
```bash
curl https://raw.githubusercontent.com/frogrammer/azure-knowledgemining-cli/main/cloudshell-install.sh | bash
```
## pre-requisites
 - kubectl 
 - terraform
 - nodejs > 0.1.15 or a nodejs virtual environment
 - cdktf [OPTIONAL to generate azurerm provider CDK]
 - az cli