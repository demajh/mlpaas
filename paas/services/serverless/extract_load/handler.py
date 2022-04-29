import os
import sys
import uuid
import boto3
import scipy
import pickle
import psycopg2
import numpy as np
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

EXTRACT_SOURCE = {extract_source}
EXTRACT_SOURCE_NAME = {extract_source_name}
LOAD_TARGET = {load_target}
LOAD_TARGET_NAME = {load_target_name}

DATABASE = {database_name}
DATABASE_REGION = {database_region}
USER = {database_user}
PASSWORD = {database_password}
HOST = {database_host}
PORT = {database_port}
SCHEMA = {database_schema}
IAM_ROLE = {iam_role}

def handler(event, context):

    try:
        {extract_source_code_location}

        {create_load_target_code_location}

        {sync_source_target_code_location}
        
    except Exception as e:
        status_obj = {"status":"FAILED", "message": "Error received: {}".format(str(e))}
        return status_obj
    
    status_obj = {"status":"SUCCEEDED", "message": "extract-load operation executed successfully!"}
    return status_obj

if __name__=="__main__":
    ret = handler({}, {})
    print(ret)
