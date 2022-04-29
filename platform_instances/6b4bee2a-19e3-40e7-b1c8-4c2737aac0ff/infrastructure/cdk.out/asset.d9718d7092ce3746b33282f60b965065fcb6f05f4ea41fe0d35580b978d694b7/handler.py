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

EXTRACT_SOURCE = 's3'
EXTRACT_SOURCE_NAME = 's3://mission-clients/client_id=bigchange/object_type=data/data_small.csv'
LOAD_TARGET = 'rds'
LOAD_TARGET_NAME = 'None'

DATABASE = 'postgres'
DATABASE_REGION = 'us-west-2'
USER = 'postgres'
PASSWORD = 'Tele-underwear9'
HOST = 'bigchange-eda.chdniwnlwedn.us-west-2.rds.amazonaws.com'
PORT = '5432'
SCHEMA = 'public'
IAM_ROLE = 'arn:aws:iam::545555405821:role/model-dev'

def handler(event, context):

#    try:
    
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket= 'mission-clients', Key= 'client_id=bigchange/object_type=data/data_small.csv')
    source_df = pd.read_csv(obj['Body'])
            

    
    #try:
    #conn = psycopg2.connect(database = DATABASE, user = USER, password = PASSWORD, host = HOST, port = PORT)
    #except:
    #raise Exception("I am unable to connect to the database.")

    table_name = str(uuid.uuid4())
    #cur = conn.cursor()
    #try:
    #source_df.to_sql(name=table_name, con = conn, if_exists = 'replace', index = False)
    engine = sa.create_engine('postgresql://{}:{}@{}:{}/{}'.format(USER, PASSWORD, HOST, PORT, DATABASE))
    print(bool(engine)) # <- just to keep track of the process                                            
    #with engine.connect() as conn:
    source_df.to_sql(name=table_name, con = engine, if_exists = 'replace', index = False)
    target_df = pd.read_sql('SELECT * FROM "{}"'.format(table_name), con = engine)
    assert(source_df.shape[0]==target_df.shape[0] and source_df.shape[1]==target_df.shape[1])
    print(target_df)
    #except:
    #raise Exception("I can't create the requested database table!")
    #conn.commit() # <--- makes sure the change is shown in the database
    #conn.close()
    #cur.close()
            

    
#    except Exception as e:
#        status_obj = {"status":"FAILED", "message": "Error received: {}".format(str(e.__str__))}
#        return status_obj
    
    status_obj = {"status":"SUCCEEDED", "message": "extract-load operation executed successfully!"}
    return status_obj

if __name__=="__main__":
    ret = handler({}, {})
    print(ret)
