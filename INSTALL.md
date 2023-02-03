# Prerequisite
To run the pipeline you will need:
- Python 3.10.7
- Pyenv to manage python versions & virtual environment
- Terraform ([installation guide](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform))

# Credentials
# Obtain Spotify API Credentials
Simply go to https://developer.spotify.com/dashboard/applications, create an app, and obtain the client ID and client Secret.

# Optain the AWS Secrets

Log into the AWS console,go to **Identity and Access Management (IAM)**, create a new user, grant the 

- An AWS account with full CRUD permissions for the following AWS services:
    - S3
    - Redshift
    - EC2
    - VPC
    - EBS Volumes (To access the Million Song Dataset)
- Download the AWS account secret keys, store securely. Enter it into the `config.cfg` file, and also use it in the .tfvars which will be used to authorize terraform actions


# Development environment
- Run `make prepare-dev`
- Credentials
    - 


# Production environment
Run `make prepare-prod`