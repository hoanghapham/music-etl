
What you need to do to set up the pipeline:

- [Install packages](#install-packages)
  - [Install Python](#install-python)
  - [Install required packages:](#install-required-packages)
- [Set up infrastructure](#set-up-infrastructure)
  - [Obtain the AWS Secrets](#obtain-the-aws-secrets)
  - [Config `secrets.tfvars`](#config-secretstfvars)
  - [Run Terraform \& obtain the resource info](#run-terraform--obtain-the-resource-info)
  - [Obtain Spotify API Credentials](#obtain-spotify-api-credentials)


How to get data:
- [Access the full Million Song Dataset](#access-the-full-million-song-dataset)
- [Get a subset of MSD](#get-a-subset-of-msd)

## `config.cfg` explanation


## Install packages

### Install Python
You can use `pyenv` to install a different Python version from what you have in your machine. Assuming that you already have pyenv installed, run the following:

```bash
pyenv install 3.10.7
```

On PopOS, you may encounter this error: `python-build: line xxx: xxxx Segmentation fault`. If that's the case, run the following:

```bash
sudo apt install clang -y;
CC=clang pyenv install 3.10.7;
```
(Reference: https://github.com/pyenv/pyenv/issues/2239)

Then cd in to the project folder, run this to set the project's python version to Python 3.10.7

### Install required packages:

From the `music-etl` folder run the following to install required packages

```bash
pip3 install -r etl/requirements.txt;
pip3 install -e etl/ 
```
These two commands are combined into the `make setup-env` command.

## Set up infrastructure

We use [Terraform]((https://developer.hashicorp.com/terraform/downloads?product_intent=terraform)) to set up the infrastructure for this pipeline, including:
- S3 bucket
- Redshift cluster
- EC2 instance
- EBS Volume (containing the source MSD data)

First, you will need to obtain AWS secrets, only then you can run Terraform

### Obtain the AWS Secrets

Log into the AWS console,go to **Identity and Access Management (IAM)**, create a new user, and grant full CRUD permissions for the following AWS services:
    - S3
    - Redshift
    - EC2
    - VPC
    - EBS Volumes (To access the Million Song Dataset)

Create a secret keys for this user and store these securely. This will be used to fill in the config files later.

### Config `secrets.tfvars`

This will be used to pass credentials to terraform when running commands. A sample of the file is already included. The AWS secrets and Redshift password will go here.

This file need to be presented in the Terraform folder that you want to run (either `dev/` or `prod/`)

### Run Terraform & obtain the resources info


After configuring Terraform secrets, change into the Terrform folder you want to run and execute:

```bash
terraform init;
terraform apply -var-file secrets.tfvars -auto-approve;
```

After the command finished running, it will output the resource identifiers that you need to input to the `etl/flows/config.cfg` file, including:
- Redshift endpoint
- Bucket name
- IAM role ARN

In case you run the `prod/` folder, you will also 

### Obtain Spotify API Credentials
Simply go to https://developer.spotify.com/dashboard/applications, create an app, and obtain the client ID and client Secret.


## How to get data

### Access the full Million Song Dataset
The official guide to access the full dataset is [here](ht://millionsongdataset.com/pages/getting-dataset/). 
The terraform scripts in this repo will automatically give you access to the dataset via EC2. It will be mounted to `/mnt/snap` directory.


### Get a subset of MSD
The subset can be downloaded from [this link](http://labrosa.ee.columbia.edu/~dpwe/tmp/millionsongsubset.tar.gz). 
You can run the scrip at `etl/flows/download_msd_subset` to download & extract it. The output folder is configured in the `etl/flows/config.cfg` file. 
