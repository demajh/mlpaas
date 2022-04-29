# System modules
import os
import sys
import yaml
import json
import time
import boto3
import hashlib
import zipfile
import tempfile
import sagemaker
import numpy as np
import pandas as pd
from time import gmtime, strftime

def get_redshift_credentials(user, cluster_identifier, region):

    session = boto3.Session()
    client = boto3.client('redshift',
                          region_name=region)
    response = client.get_cluster_credentials(DbUser=user,
                                              ClusterIdentifier=cluster_identifier)
    return response, session

def update_profiles_config(local_profile_path):

    with open(local_profile_path, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    user = data["magnify_transforms"]["outputs"]["dev"]["user"]
    cluster_identifier = data["magnify_transforms"]["outputs"]["dev"]["host"].split('.')[0]
    region = data["magnify_transforms"]["outputs"]["dev"]["host"].split('.')[2]
    creds, session = get_redshift_credentials(user, cluster_identifier, region)    
    data["magnify_transforms"]["outputs"]["dev"]["user"] = creds["DbUser"]
    data["magnify_transforms"]["outputs"]["dev"]["password"] = creds["DbPassword"]
        
    with open(local_profile_path, "w") as stream:
        yaml.dump(data, stream, default_flow_style=False)

    return
        
def load_config(config_path):

    if "s3" in config_path:
        config = download_config_s3(config_path)
    elif os.path.exists(config_path):
        config = json.load(open(config_path, "r"))
    else:
        raise Exception("Config path type not recognized.")
    return config

def download_config_s3(s3_path):

    bucket = s3_path.split("/")[2]
    key = "/".join(s3_path.split("/")[3:])
    s3 = boto3.resource('s3')
    content_object = s3.Object(bucket, key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    return json_content

def load_dbt_project(project_path):

    if "s3" in project_path:
        download_project_s3(project_path)
        
    elif os.path.exists(project_path):
        return
    
    else:
        raise Exception("project_path type not recognized.")
    
    return

def download_project_s3(s3_path):

    bucket = s3_path.split("/")[2]
    key = "/".join(s3_path.split("/")[3:])
    s3 = boto3.resource('s3')
    content_object = s3.Object(bucket, key)    
    basename = key.split('/')[-1]
    assert(basename.split('.')[-1]=="zip")
    local_dir = tempfile.mkdtemp()
    local_path = os.path.join(local_dir, basename)
    local_path_unzipped = os.path.join(local_dir, '.'.join(basename.split('.')[:-1]))
    
    s3_client = boto3.client('s3')
    # Download the file from S3
    s3_client.download_file(bucket, key, local_path)
    with zipfile.ZipFile(local_path, 'r') as zip_ref:
        zip_ref.extractall(local_path_unzipped)

    return local_path_unzipped

def run_pipeline_local(s3_path):

    project_path = download_project_s3(s3_path)
    update_profiles_config(os.path.join(project_path, "transforms/magnify_transforms/profiles.yml"))
    assert(len(os.listdir("{}/transforms/magnify_transforms".format(project_path)))>0)
    print("{}/transforms/magnify_transforms".format(project_path))
    print(os.listdir("{}/transforms/magnify_transforms".format(project_path)))
    os.system("cd {}/transforms/magnify_transforms;dbt debug --config-dir".format(project_path))
#    os.listdir("/root/.dbt")
#    os.system("cat /root/.dbt/profiles.yml")
    os.system("cd {}/transforms/magnify_transforms;dbt run".format(project_path))
    
    return

def handler(config, context):

    """                                                                                                     
    This is the driver function for the broker step.                                                        
    """

    print("Config")
    print(config)
    if config["pipeline_request_type"]=="run_pipeline":
        response_run_pipeline = run_pipeline_local(config["dbt_project_s3_location"])
        rerun_pipeline_status_message = json.dumps({"status": "SUCCEEDED", "response": response_run_pipeline})

    else:
        rerun_pipeline_status_message = json.dumps({"status": "FAILED", "response": response_run_pipeline})

    config["rerun_pipeline_status_message"] = rerun_pipeline_status_message

    return config

if __name__ == "__main__":

#    config_path = "s3://magnify-data-pipeline/configs/config.json"
    config_path = os.environ["CONFIG_PATH"]
    config = load_config(config_path)
    config["pipeline_request_type"] = "run_pipeline"

    pipeline_response = handler(config, {})
    print(pipeline_response)        
