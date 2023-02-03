# Music ETL

## Goal
With this project, I aim to combine the real Million Song Dataset with data coming from Spotify API. With this pipeline, new researchers that are already familiar with the old Million Song Dataset to get new information for all the songs in Spotify, like new audio features, song popularity, artist popularity...


## Architecture

### Components
- Data sources
    - [Million Song Dataset](http://millionsongdataset.com/): We will use the actual MSD dataset in its original data format (HDF5). The full dataset (280 GB) can be accessed via AWS marketplace, and for development purpose we will use their subset (1.8 GB)
    - [Spotify API](https://developer.spotify.com/documentation/web-api/)
- Data storage:
    - Amazon S3: for JSON data staging
    - Amazon Redshift: for final analytics table storage. In reality, this is also the place where end-users query the final data tables for analytics purposes, so a database that can handle large query workload is necessary
- Orchestrator: [Prefect](https://www.prefect.io/). This is a new workflow orchestrator that are simpler to deploy and use than Airflow. It is also easier to use thanks to the syntax being closer to Python's syntax.
- Processing
    - Amazon EC2: For production, we need to access the MSD dataset on Amazon Workspace, and EC2 is needed to do that. 
    - Personal computer: for development purpose, it is sufficient to run everything in a personal machine.
- Terraform: for easy infrastructure set up.

![](./images/dev.png)

### ETL flow
- At the moment, the flow is configured to run for one time only. 
- In case we want to regularly update the songs & artists list, instead of using the Million Song Dataset, we can figure out a way to get updated songs & artists list on Spotify.
- Overview of the workflow:

    ![](./images/flow.png)
    

## Installation
Please refer to the [Set Up Guide](./SETUP.md).

## Data Model & Dictionary
Please refer to the [Data Dictionary](./DATA_DICTIONARY.md) file.

# Additional questions

## What if the data was increased by 100x?

Currently the pipeline is built purely on Python, and use the SequentialTaskRunner of Prefect. For larger data volume, we may need to build some parts of the ETL in Spark (for example, the staging & analytics transformation steps), or switch to the ConcurrentTaskRunner of Prefect, and run the flow in a stronger EC2 instance.

## What if the pipeline need to be run daily at 7am?

We will need to create a Prefect deployment that is scheduled to run daily at 7am, and have to modify the tasks to run incremental updates (instead of dropping all tables and create from scratch)

## If the database needed to be accessed by 100+ people?

In this case, we will need to pay extra attention to the query pattern of the users and create tables with correct distribution types to optimize the query performance, especially for JOIN operations. 


# Shortcuts to run the pipeline

## Local development (with MSD subset)

Assume that you have set up all resources via Terraform and filled in `config.cfg` file:

    ```bash
    make setup-env
    make download-msd-subset
    make extract-msd-data
    make run-etl-dev
    ```

## Production (on EC2)

If you run the terraform scripts in the `terraform/prod` folder, you can connect to the EC2 instance via the AWS console and access the Million Song Dataset at `/mnt/snap/`. When logged in, do the following:

- Clone this repo 
- Update the `config.cfg` file. Make sure to set `MSD_INPUT_DIR = /mnt/snap/data`
- Run commands:
    
    ```bash
    make setup-env
    make download-msd-subset
    make extract-msd-data
    make run-etl-prod
    ```
