import sys
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
import pandas as pd

#>>>>>>>> MAKE CHANGES HERE >>>>>>>>
DATABASE = "centerhq"
USER = "brianm"
PASSWORD = sys.argv[1]  #see answer by David Bern https://stackoverflow.com/questions/43136925/create-a-config-file-to-hold-values-like-username-password-url-in-python-behave/43137301
#HOST = "csv-ingest-test.cgre9vcx7lph.us-west-1.redshift.amazonaws.com:5439/dev"
HOST = "magnify-science.cgre9vcx7lph.us-west-1.redshift.amazonaws.com"
PORT = "5439"
SCHEMA = "public"      #default is "public"

########## connection and session creation ##########
connection_string = "redshift+psycopg2://%s:%s@%s:%s/%s" % (USER,PASSWORD,HOST,str(PORT),DATABASE)
#connection_string = "redshift+psycopg2://%s:%s@%s:%s/%s" % (USER,PASSWORD,HOST,str(PORT))
print(connection_string)
engine = sa.create_engine(connection_string)
print("Conencted!")
session = sessionmaker()
session.configure(bind=engine)
s = session()
#SetPath = "SET search_path TO %s" % SCHEMA
#s.execute(SetPath)

#--create database example
#query2 = '''\ 
#create database centerhq with OWNER=brianm 
#'''
#r2 = s.execute(query2)
#sys.exit()

#--create table example
#query2 = '''\ 
#create table public.test (
#id integer encode lzo,
#user_id integer encode lzo,
#created_at timestamp encode delta32k,
#updated_at timestamp encode delta32k
#)
#distkey(id)
#sortkey(id)
#'''
#print("Executing query...")
#r2 = s.execute(query2)
#print("Query executed!")

#--select example
query4 = '''\ 
select * from centerhq.public."sfdc-data-labeled"
'''
r4 = s.execute(query4)

########## create DataFrame from SQL query output ##########
df = pd.read_sql_query(query4, connection_string)

print(df.head(50))

########## close session in the end ##########
s.close()
