# Prerequisite
To run the pipeline you will need:
- Python 3.10.7
- Pyenv to manage python versions & virtual environment
- Terraform ([installation guide](https://developer.hashicorp.com/terraform/downloads?product_intent=terraform))
- An AWS account with full CRUD permissions for the following AWS services:
    - S3
    - Redshift
    - EC2
    - VPC
    - EBS Volumes (To access the Million Song Dataset)
- Download the AWS account secret keys, store securely and 


# Development environment
- Run `make prepare-dev`
- Credentials
    - 


# Production environment
Run `make prepare-prod`