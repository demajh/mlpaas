import os
import sys
import boto3
import scipy
import pickle
import numpy as np
import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

INSTANCE_CONFIG = os.environ("INSTANCE_CONFIG")

fname_telemetry = "/home/ubuntu/bigchange_eda/data/bigchange_data_small.csv"
outfname_telemetry = "/home/ubuntu/bigchange_eda/data/bigchange_data_small_telemetry.csv"

out_s3_dir = "s3://demajh-pipelines/data/customer=bigchange/problem_type=transform_input/"
out_s3_bucket = "demajh-pipelines"
out_s3_prefix_telemetry = "data/customer=bigchange/problem_type=transform_input/bigchange_data_small_telemetry.csv"

s3_client = boto3.client('s3')
df_card_cases_telemetry = pd.read_excel(fname_card_cases_telemetry)
df_card_cases_telemetry.to_csv(outfname_card_cases_telemetry, sep="|", index=False)

try:
    response = s3_client.upload_file(outfname_card_cases_telemetry, out_s3_bucket, out_s3_prefix_card_ca\
ses_telemetry)
except ClientError as e:
    print(e)
    sys.exit()

#>>>>>>>> MAKE CHANGES HERE >>>>>>>>
DATABASE = "bigchange"
USER = sys.argv[1]
PASSWORD = sys.argv[2]  #see answer by David Bern https://stackoverflow.com/questions/43136925/create-a-\
config-file-to-hold-values-like-username-password-url-in-python-behave/43137301
HOST = "bigchange.cgre9vcx7lph.us-west-1.redshift.amazonaws.com"
PORT = "5439"
SCHEMA = "public"

########## connection and session creation ##########
connection_string = "redshift+psycopg2://%s:%s@%s:%s/%s" % (USER,PASSWORD,HOST,str(PORT),DATABASE)
print(connection_string)
engine = sa.create_engine(connection_string)
print("Conencted!")
session = sessionmaker()
session.configure(bind=engine)
s = session()

#--select example
create_tele_table = '''CREATE TABLE bigchange.public."telemetry-data"                                    
(                                                                                                        
  "CustomerId"        nvarchar(max)   default  '',                                                       
  "ResourceGroupId"            nvarchar(max)   default  '',                                              
  "ResourceId"           nvarchar(max)   default  '',                                                    
  "CustomerId"       nvarchar(max)   default  '',                                                        
  "SectorId"     nvarchar(max)   default  '',                                                            
  "Sector"             nvarchar(max)   default  '',                                                      
  "JobTypeId"   nvarchar(max)   default  '',                                                             
  "JobType"      nvarchar(max)   default  '',                                                            
  "JobCreationDate"           nvarchar(max)   default  '',                                               
  "PlannedJourneyStartLat"               nvarchar(max)   default  '',                                    
  "PlannedJourneyStartLong"         nvarchar(max)   default  '',                                         
  "JobLat"            nvarchar(max)   default  '',                                                       
  "JobLong"              nvarchar(max)   default  '',                                                    
  "JobPlannedStart"      nvarchar(max)   default  '',                                                    
  "JobPlannedWorkDuration"                  nvarchar(max)   default  '',
  "JobActualStart"              nvarchar(max)   default  '',                                             
  "JobActualWorkDuration"           nvarchar(max)   default  ''                                          
  "JobPlannedDrivingDistance"           nvarchar(max)   default  ''                                      
  "JobActualDrivingDistance"           nvarchar(max)   default  ''                                       
  "JobPlannedDrivingDuration"           nvarchar(max)   default  ''                                      
  "JobActualDrivingDuration"           nvarchar(max)   default  ''                                       
  "JobSuccess"           nvarchar(max)   default  ''                                                     
  "JobComment"           nvarchar(max)   default  ''                                                     
  "JobIsRecurring"           nvarchar(max)   default  ''                                                 
)                                                                                                        
'''

print("Executing table creation...")
create_table_out = s.execute(create_cct_table)
s.commit()

#--select example
tele_data_insert = '''COPY bigchange.public."telemetry-data" FROM 's3://demajh-pipelines/data/customer=bigchange/problem_type=transform_input/bigchange_data_small_telemetry.csv' IAM_ROLE 'arn:aws:iam::495303562198:role/redshift-elt-incoming' FORMAT AS CSV DELIMITER '|' QUOTE '"' REGION AS 'us-west-1'            
'''
print("Executing table insertion...")
tele_data_out = s.execute(tele_data_insert)
s.commit()

#--select example
tele_data_extract = '''SELECT * from bigchange.public."telemetry-data"'''
print("Executing table extraction...")
tele_data_out = s.execute(tele_data_extract)
rows = s.commit()
print(tele_data_out)
print(rows)
for row in tele_data_out:
    print(row)

drop_telemetry_table = '''DROP TABLE bigchange.public."telemetry-data"'''
print("Executing table extraction...")
drop_telemetry_table_out = s.execute(drop_telemetry_table)
s.commit()








