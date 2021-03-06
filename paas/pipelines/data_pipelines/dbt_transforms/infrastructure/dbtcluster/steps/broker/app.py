# System modules
import os
import sys
import json
import time
import boto3
import hashlib
import sagemaker
import numpy as np
import pandas as pd
from time import gmtime, strftime

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

def download_json_s3(bucket, key):

    s3 = boto3.resource('s3')
    content_object = s3.Object(bucket, key)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    
    return json_content

def dump_config_s3(bucket, key, config):

    s3 = boto3.resource('s3')
    s3 = s3.Object(bucket, key)
    s3.put(Body=(bytes(json.dumps(template).encode('UTF-8'))))

    return

def create_task(cluster_inst_name, task_name, role_arn, image_name, region):

    print("Creating log group")
    logs_client = boto3.client('logs', region_name=region)
    try:
        logs_response = logs_client.create_log_group(logGroupName='/aws/ecs/{}'.format(cluster_inst_name))
        print(logs_response)
    except:
        print("Logs already exist")

    current_time = time.gmtime()
    print("Creating task definition")
    ecs_client = boto3.client('ecs')
    task_inst_name = task_name + "-task-" + time.strftime("%Y-%m-%d-%H-%M-%S", current_time)
    taskdef_response = ecs_client.register_task_definition(
        family = task_inst_name,
        containerDefinitions=[
            {
                'name': task_inst_name,
                'image': image_name,
                'logConfiguration': {'logDriver': 'awslogs',
                                     'options': {'awslogs-region': region,
                                                 'awslogs-group': '/aws/ecs/{}'.format(cluster_inst_name)}
                },
            }
        ],
        memory='4096',
        cpu='2048',
        taskRoleArn=role_arn
    )
    
    print(taskdef_response)
    print("Running task.")
    service_response = ecs_client.run_task(cluster=cluster_inst_name, taskDefinition=task_inst_name)
    service_response["tasks"][0]["createdAt"] = service_response["tasks"][0]["createdAt"].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
#    print(service_response)
#    print(service_response["tasks"])
#    print(service_response["tasks"][0])
#    print(service_response["tasks"][0]["createdAt"])
    
    return service_response    

def create_execute_task(config):

    cluster_name = config["cluster_name"]
    task_name = config["task_name"]
    image_name = config["image_name"]
    role_arn = config["role_arn"]
    region = config["region"]

    # Function creates service instance, it executes after creation by default
    response = create_task(cluster_name, task_name, role_arn, image_name, region)
    
    return response

def handle_run_pipeline_request(config):

    """                                                                                                  
    This is the driver function for the broker step in the case of a new data pipeline request.
    """
    # Create and execute a cluster task for running a dbt pipeline
    response = create_execute_task(config)
    
    return response

def handler(event, context):

    """                                                                                                     
    This is the driver function for the broker step.
    """

    print("Event")
    print(event)
    config_path = event["config_path"]
    config = load_config(config_path)
    all_response = []
    if config["pipeline_request_type"]=="run_pipeline":
        response_run_pipeline = handle_run_pipeline_request(config)
        rerun_pipeline_status_message = json.dumps({"status": "SUCCEEDED", "response": response_run_pipeline})
        
    else:
        rerun_pipeline_status_message = json.dumps({"status": "FAILED", "response": response_run_pipeline})
        
    config["rerun_pipeline_status_message"] = rerun_pipeline_status_message

    return config

if __name__ == "__main__":

    config_path = "s3://magnify-data-pipeline/configs/config.json"
    config = load_config(config_path)
    config["pipeline_request_type"] = "run_pipeline"

    pipeline_response = handler(config, {})
    print(pipeline_response)


