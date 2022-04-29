import os
import sys
import time
import json
import boto3

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

def trigger_data_pipeline(config):

    client = boto3.client('lambda')
    accept_type = "application/json"
    content_type = "application/json"    
    payload = json.dumps(config)
    start_time = time.time()
    response = client.invoke(FunctionName="ml_data_pipeline_broker",
                             InvocationType="Event",
                             Payload=payload)
    time.sleep(15)
    print("--- %s seconds ---" % (time.time() - start_time))

    return

if __name__=="__main__":

    config_path = "s3://magnify-data-pipeline/configs/config.json"
    config = load_config(config_path)
    config["pipeline_request_type"] = "run_pipeline"
#    pipeline_response = handler(config, {})
    trigger_data_pipeline(config)

