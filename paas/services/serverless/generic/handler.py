import re
import os
import io
import sys
import uuid
import json
import boto3
import hashlib
import logging
import datetime
import tempfile
import psycopg2
import numpy as np
import pandas as pd
import sqlalchemy as sa
from threading import Thread
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from autogluon.tabular import TabularDataset, TabularPredictor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

class HandlerService:
    
    """
    Handler service that is executed by the model server.
    Determines specific default inference handlers to use based on model being used.
    This class defines
        - The ``handle`` method is invoked for all incoming inference requests to the model server.
        - The ``initialize`` method is invoked at model server start up.
    """
    
    def __init__(self):
        
        self.error = None
        self._context = None
        self._batch_size = 0
        self.initialized = False

    def download_s3_folder(self, bucket_name, s3_folder, local_dir=None):
        
        """
        self.download_s3_folder(model_repo_bucket, model_repo_prefix, modeldir)
        Download the contents of a folder directory
        Args:
            bucket_name: the name of the s3 bucket
            s3_folder: the folder path in the s3 bucket
            local_dir: a relative or absolute directory path in the local file system
        """
        
        s3 = boto3.resource('s3') # assumes credentials & configuration are handled outside python in .aws directory or environment variables        
        bucket = s3.Bucket(bucket_name)
        for obj in bucket.objects.filter(Prefix=s3_folder):
            if type(local_dir)==type(None):
                target = obj.key
            else:
                target = os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
            if not os.path.exists(os.path.dirname(target)):
                os.makedirs(os.path.dirname(target))
            if obj.key[-1] == '/':
                continue
            bucket.download_file(obj.key, target)

        return
        
    def load_config(self, config_path):

        config = None
        if "s3://" in config_path:
            if config_path.split('.')[-1]=="json":
                s3 = boto3.resource('s3')
                bucket = config_path.split('/')[2]
                key = '/'.join(config_path.split('/')[3:])
                content_object = s3.Object(bucket, key)
                file_content = content_object.get()['Body'].read().decode('utf-8')
                config = json.loads(file_content)
            else:
                raise Exception("config file of unrecognized type!")            
        else:
            raise Exception("config_path location unrecognized!")

        return config

    def load_latest_model(self, model_repo):

        if "s3" in model_repo:
            model_repo_bucket = model_repo.split('/')[2]
            model_repo_prefix = '/'.join([elem for elem in model_repo.split('/')[3:]])
        else:
            model_repo_bucket = model_repo.split('/')[0]
            model_repo_prefix = '/'.join([elem for elem in model_repo.split('/')[1:]])

        modeldir = tempfile.mkdtemp()
        self.download_s3_folder(model_repo_bucket, model_repo_prefix, modeldir)
        print(modeldir)
        model = TabularPredictor.load(modeldir)

        return model

    def get_redshift_credentials(self, user, cluster_identifier, region):

        session = boto3.Session()
        client = boto3.client('redshift',
                              region_name=region)
        response = client.get_cluster_credentials(DbUser=user,
                                                  ClusterIdentifier=cluster_identifier)
        return response, session

    def insert_predictions(self, data, predictions):

        host = data["data"]["database_host"]
        user = data["data"]["database_user"]
        region = data["data"]["database_region"]
        cluster_identifier = data["data"]["redshift_cluster_identifier"]
        port = data["data"]["database_port"]
        database = data["data"]["database_name"]
        schema = data["data"]["database_schema"]
        tablename = "predictions"
        
        creds, session = self.get_redshift_credentials(user, cluster_identifier, region)
        con = psycopg2.connect(dbname=database, host=host, port=port, user=creds["DbUser"], password=creds["DbPassword"])
        cursor = con.cursor()

        print("Inserting predictions into DB table...")
        # customer_id, client_id, config_id, config_path, prediction, prediction_timestamp
        background_thread = Thread(target=cursor.executemany, args=("INSERT INTO {}.{}.{} VALUES(%s,%s,%s,%s,%s,%s)".format(database, schema, tablename), predictions))
        background_thread.start()
        con.commit()

        return
        
    def initialize(self, context, event=None):
        
        self._context = context
        self.initialized = True
        if type(event)!=type(None):
#            self.config_path = event["config_path"]
            self.config_path = os.path.join(event["config_path_prefix"],
                                            '.'.join([event["configuration_id"], "json"]))
            print("\n\n")
            print("self.config_path")
            print(self.config_path)
            print("\n\n")
            self.config = self.load_config(self.config_path)
            self.customer_id = self.config["customer_id"]
            self.endpoint_output_prefix = self.config["endpoint_output_prefix"]
            self.label_columns = self.config["label_columns"]
            self.label_columns = "|".join(self.label_columns)
            self.label_name = hashlib.sha1(self.label_columns.encode()).hexdigest()
            self.config_id = self.config["configuration_id"]
            self.database_type = self.config["dataset_type"]
            self.problem_type = self.config["problem_type"]
            self.model_repo = os.path.join(self.config["model_repo_path_prefix"],
                                           'customer={}/problem_type={}/label_name={}/'.format(self.customer_id, self.problem_type, self.label_name))
            
            self.model = self.load_latest_model(self.model_repo)
            self.response, session = self.get_redshift_credentials(self.config["database_user"],
                                                                   self.config["redshift_cluster_identifier"],
                                                                   self.config["database_region"])
        
        return

    def get_redshift_credentials(self, user, cluster_identifier, region):

        session = boto3.Session()
        client = boto3.client('redshift',
                              region_name=region)
        response = client.get_cluster_credentials(DbUser=user,
                                                  ClusterIdentifier=cluster_identifier)
        return response, session

    def create_sql_dataset(self, session, database, schema, label_col, cursor, cols=None, train_test_partition=[0.75, 0.25], shuffle_rows=False):

        ufr_data_extract = '''SELECT * from {}.{}.ufr'''.format(database, schema)
        cursor.execute(ufr_data_extract)
        columns = [desc[0] for desc in cursor.description]
        ufr_data_out = cursor.fetchall()

        all_rows = []
        for row in ufr_data_out:
            all_rows.append(list(row))
        table = pd.DataFrame(all_rows, columns = columns)

        if type(cols)!=type(None) and type(cols)==type(["list"]):
            if len(cols)>0:
                filt_table = table[cols]
            else:
                filt_table = table
        else:
            filt_table = table

        if shuffle_rows:
            df_shuff = filt_table.sample(frac=1.)
        else:
            df_shuff = filt_table

        columns = list(df_shuff.columns)
        df_shuff = df_shuff.drop_duplicates(subset=df_shuff.columns, keep="first")
        df_shuff = df_shuff[df_shuff[label_col].notna()]
        data = TabularDataset(df_shuff)
        y = data[label_col]
        data_eval = data.drop(columns=[label_col])
        data_eval = data_eval.reindex(columns=[elem for elem in columns if elem!=label_col])

        return data, data_eval
    
    def get_data_sql_db(self, config):

        host = config["host"]
        user = config["user"]
        region = config["region"]
        cluster_identifier = config["cluster_identifier"]
        port = config["port"]
        database = config["database"]
        schema = config["schema"]
        label_col = config["label_col"]
        cols = config["cols"]
        shuffle_rows = True
        
        creds, session = self.get_redshift_credentials(user, cluster_identifier, region)
        con = psycopg2.connect(dbname=database, host=host, port=port, user=creds["DbUser"], password=creds["DbPassword"])
        cur = con.cursor()
        dataset, dataset_eval = self.create_sql_dataset(session, database, schema, label_col, cur, cols=cols, shuffle_rows=shuffle_rows)

        return dataset, dataset_eval

    def put_s3_table(self,
                     df,
                     db_location,
                     db_type,
                     partition_cols=None):

        if db_type=="parquet":
            import pyarrow.parquet as pq
            if type(partition_cols)!=type(None):
                df.to_parquet(db_location, partition_cols=partition_cols, index=False)
            else:
                df.to_parquet(db_location, index=False)

        else:
            raise Exception("Unsupported db type.  Type: {}".format(db_type))

        return

    def get_s3_table(self,
                     db_location,
                     db_type):

        if db_type=="parquet":
            import pyarrow.parquet as pq
            table = pq.read_table(db_location).to_pandas()
        elif db_type=="csv":
            table = pd.read_csv(db_location, sep="|")
        else:
            raise Exception("Unsupported db type.  Type: {}".format(db_type))

        return table        

    def get_label_cols(self,
                       table_cols,
                       table_cols_filt,
                       label_cols,
                       problem_type,
                       label_col_pattern,
                       ignore_col_pattern):

        if label_col_pattern:
            label_col_regex = re.compile(label_col_pattern)
            label_cols_list = []
            for col in table_cols:
                if label_col_regex.search(col):
                    label_cols_list.append(col)

        else:
            label_cols_list = label_cols.split('|')

        ignore_cols_list = []
        if ignore_col_pattern:
            ignore_col_regex = re.compile(ignore_col_pattern)
            for col in table_cols:
                if ignore_col_regex.search(col):
                    ignore_cols_list.append(col)

        table_cols_filt = [col for col in table_cols_filt if col not in ignore_cols_list]
        if problem_type!="regression":
            label = label_cols_list[0]
            label_cols_list = [label]
        else:
            label = label_cols_list[:]
        table_cols_filt = list(set(table_cols_filt+label_cols_list))

        return table_cols_filt, label, label_cols_list

    def create_s3_dataset(self,
                          dataset_location,
                          dataset_type,
                          label_cols,
                          problem_type,
                          cols=None,
                          label_col_pattern="",
                          ignore_col_pattern=""):

        table = self.get_s3_table(dataset_location,
                                  dataset_type)
        table_cols = list(table.columns)
        if type(cols)==type(None) or type(cols)!=type(["list"]):
            cols =  table_cols

        cols, label, label_cols_list = self.get_label_cols(table_cols,
                                                           cols,
                                                           label_cols,
                                                           problem_type,
                                                           label_col_pattern,
                                                           ignore_col_pattern)

        filt_table = table[cols]

        df_shuff = filt_table
        columns = list(df_shuff.columns)
        df_shuff = df_shuff.reindex(columns=columns)
        data = TabularDataset(df_shuff)

        data_nolab = data.drop(columns=label_cols_list)
        data_nolab = data_nolab.reindex(columns=[elem for elem in columns if elem not in label_cols_list])

        return data, data_nolab    
    
    def get_data_s3_db(self, config):
        
        dataset_location = config["dataset_path_prefix"]
        dataset_type = config["dataset_type"]
        problem_type = config["problem_type"]
        label_columns = config["label_columns"]
        label_column_pattern = config["label_column_pattern"]
        ignore_column_pattern = config["ignore_column_pattern"]
        if len(label_columns)>1 and problem_type!="regression":
            raise Exception("Multi-label classification is currently unsupported!!")
        label_cols = "|".join(label_columns)
        label_name = hashlib.sha1(label_cols.encode()).hexdigest()

        dataset, dataset_eval = self.create_s3_dataset(dataset_location,
                                                       dataset_type,
                                                       label_cols,
                                                       problem_type,
                                                       cols=label_cols,
                                                       label_col_pattern=label_column_pattern,
                                                       ignore_col_pattern=ignore_column_pattern)

        return dataset, dataset_eval
    
    def preprocess(self, config, context):

        self.initialize(context, config)
        request_content_type = "application/json"
        if config["dataset_type"] == "json":
            data_json_str = config["data"]
            data_df = pd.read_json(data_json_str)
            input_object = TabularDataset(data_df)
            columns = list(input_object.columns)
            input_object = input_object.drop(columns=[self.label_columns])
            input_object = input_object.reindex(columns=[elem for elem in columns if elem!=self.label_columns])
            
        elif config["dataset_type"] == "sql":
            input_object_label, input_object = self.get_data_sql_db(config)

        elif config["dataset_type"] == "parquet":
            input_object_label, input_object = self.get_data_s3_db(config)
        
        return input_object

    def inference(self, input_object):

        pred_out = self.model.predict(input_object)
        
        return pred_out

    def postprocess(self, all_client_id, pred_out, input_object):

        response_content_type = "application/json"
        out = pred_out.to_list()
        dataset_date = input_object["dataset_date"].to_list()
        predictions = [(self.customer_id,
                        all_client_id[pind],
                        self.config_id,
                        self.label_columns,
                        self.config_path,
                        dataset_date[pind],
                        pred,
                        datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        datetime.datetime.now().strftime("%Y-%m-%d")) for pind, pred in enumerate(out)]                        
        predictions_df = pd.DataFrame(predictions, columns=['customer_id',
                                                            'client_id',
                                                            'config_id',
                                                            'label_name',
                                                            'config_path',
                                                            'dataset_date',
                                                            'predictions',
                                                            'prediction_datetime',
                                                            'prediction_date'])
        
        return out, predictions, predictions_df
    
    def get_prediction(self, data, config_path, context):

        input_object = self.preprocess(data, context)
        if 'client_id' in list(input_object.columns):
            try:
                all_client_id = input_object["client_id"].tolist()
            except KeyError:
                all_client_id = ["None" for rind in range(input_object.shape[0])]
                
        elif 'client_name' in list(input_object.columns):
            try:
                all_client_id = input_object["client_name"].tolist()
            except KeyError:
                all_client_id = ["None" for rind in range(input_object.shape[0])]
                
        else:
            all_client_id = ["None" for rind in range(input_object.shape[0])]

        print(input_object)
        model_out = self.inference(input_object)
        ret, predictions, predictions_df = self.postprocess(all_client_id, model_out, input_object)
        print(predictions_df)
        self.put_s3_table(predictions_df,
                          self.endpoint_output_prefix,
                          self.database_type,
                          partition_cols = ["customer_id", "prediction_date", "config_id"])
        
        ret_val = {"prediction_service_request_type": "inference", "status": "success", "output": predictions}
        
        return ret_val

    def handle(self, data, context):
        
        """
        Call preprocess, inference and post-process functions
        :param data: input data
        :param context: mms context
        """

        print("data")
        print(data)
        print("\n\n")
        all_ret = []
        for sample in data:
            samp_body = json.loads(sample["body"].decode('utf-8'))
            config_location = os.path.join(samp_body["config_path_prefix"],
                                           '.'.join([samp_body["configuration_id"], "json"]))
            if samp_body["prediction_service_request_type"]=="prediction":
                ret_vals = self.get_prediction(samp_body, config_location, context)
                all_ret.append(ret_vals)
            else:
                ret_vals = {"error": "prediction_service_request_type not recognized"}
                all_ret.append(ret_vals)
        
        return all_ret

_service = HandlerService()
def handle(data, context):
    if not _service.initialized:
        _service.initialize(context)

    if data is None:
        return None

    return _service.handle(data, context)

if __name__ == "__main__":

    context = {}
    event = {
      "event_type": "inference",
      "configuration_id": "83c258e6-449d-4a72-8794-bcee08e0f250",
      "notification_slack_channel_name": "ml-ops",
      "customer_id": "centerhq",
      "client_id": "None",
      "step_role_name": "DevLaunchpadRole",
      "service_role_arn": "arn:aws:iam::495303562198:role/DevLaunchpadRole",
      "vpc_name": "vpc-0f92a3601f639fa95",
      "training_results_path_prefix": "s3://static-prediction-service/models/training_results/",
      "dataset_path_prefix": "s3://magnify-science-us-west-1/centerhq/raw_features/granular=account/",
      "endpoint_output_prefix": "s3://static-prediction-service/models/async_endpoint_requests/output/",
      "model_repo_path_prefix": "s3://static-prediction-service/models/artifacts/",
      "feature_engineering_service_type": "glue",
      "feature_engineering_service_name": "feature_generation",
      "dataset_type": "parquet",
      "database_name": "centerhq",
      "database_user": "brianm",
      "database_region": "us-west-1",
      "database_host": "magnify-science.cgre9vcx7lph.us-west-1.redshift.amazonaws.com",
      "redshift_cluster_identifier": "magnify-science",
      "database_port": "5439",
      "database_schema": "public",
      "feature_columns": [],
      "label_columns": [
        "client_revenue_has_churn:l60d"
      ],
      "label_column_pattern": "",
      "ignore_column_pattern": "l[0-9]+d",
      "problem_type": "multiclass",
      "instance_type": "t2.2xlarge",
      "config_path_prefix": "s3://static-prediction-service/configs/athena_store",
      "model_name": "centerhq-churn-60d",
      "training_job_container_url": "495303562198.dkr.ecr.us-west-1.amazonaws.com/static_prediction_training_job:latest",
      "feature_engineering_status_message": "{\"status\": \"SUCCEEDED\", \"message\": \"Feature selection completed!  Proceeding to the next step in the step function.\"}",
      "retrain_status_message": "{\"status\": \"SUCCEEDED\", \"message\": \"Proceeding to next step in pipeline, retraining not needed...\"}"
    }
    
    event = {
      "event_type": "inference",
      "configuration_id": "afd6ff74-8cc5-44cb-827e-932a54825c7c",
      "notification_slack_channel_name": "ml-ops",
      "customer_id": "centerhq",
      "client_id": "None",
      "step_role_name": "DevLaunchpadRole",
      "service_role_arn": "arn:aws:iam::495303562198:role/DevLaunchpadRole",
      "vpc_name": "vpc-0f92a3601f639fa95",
      "training_results_path_prefix": "s3://static-prediction-service/models/training_results/",
      "dataset_path_prefix": "s3://magnify-science-us-west-1/centerhq/raw_features/granular=account/",
      "endpoint_output_prefix": "s3://static-prediction-service/models/async_endpoint_requests/output/",
      "model_repo_path_prefix": "s3://static-prediction-service/models/artifacts/",
      "feature_engineering_service_type": "glue",
      "feature_engineering_service_name": "feature_generation",
      "dataset_type": "parquet",
      "database_name": "centerhq",
      "database_user": "brianm",
      "database_region": "us-west-1",
      "database_host": "magnify-science.cgre9vcx7lph.us-west-1.redshift.amazonaws.com",
      "redshift_cluster_identifier": "magnify-science",
      "database_port": "5439",
      "database_schema": "public",
      "feature_columns": [],
      "label_columns": [
        "client_revenue_has_churn:l90d"
      ],
      "label_column_pattern": "",
      "ignore_column_pattern": "l[0-9]+d",
      "problem_type": "multiclass",
      "instance_type": "t2.2xlarge",
      "config_path_prefix": "s3://static-prediction-service/configs/athena_store",
      "model_name": "centerhq-churn-90d",
      "training_job_container_url": "495303562198.dkr.ecr.us-west-1.amazonaws.com/static_prediction_training_job:latest"
    }

    event = {
      "event_type": [
        "inference"
      ],
      "configuration_id": "78f3e0a3-51b9-48a3-8855-07222c73e60c",
      "notification_slack_channel_name": "ml-ops",
      "customer_id": "centerhq",
      "client_id": "None",
      "step_role_name": "DevLaunchpadRole",
      "service_role_arn": "arn:aws:iam::495303562198:role/DevLaunchpadRole",
      "vpc_name": "vpc-0f92a3601f639fa95",
      "training_results_path_prefix": "s3://static-prediction-service/models/training_results/",
      "dataset_path_prefix": "s3://magnify-science-us-west-1/centerhq/raw_features/granular=account/",
      "endpoint_output_prefix": "s3://static-prediction-service/models/async_endpoint_requests/output/",
      "model_repo_path_prefix": "s3://static-prediction-service/models/artifacts/",
      "feature_engineering_service_type": "glue",
      "feature_engineering_service_name": "feature_generation_center",
      "dataset_type": "parquet",
      "database_name": "centerhq",
      "database_user": "brianm",
      "database_region": "us-west-1",
      "database_host": "magnify-science.cgre9vcx7lph.us-west-1.redshift.amazonaws.com",
      "redshift_cluster_identifier": "magnify-science",
      "database_port": "5439",
      "database_schema": "public",
      "feature_columns": [],
      "label_columns": [
        "client_revenue_has_churn:l30d"
      ],
      "label_column_pattern": "",
      "ignore_column_pattern": "l[0-9]+d",
      "problem_type": "multiclass",
      "instance_type": "t2.2xlarge",
      "config_path_prefix": "s3://static-prediction-service/configs/athena_store",
      "model_name": "centerhq-churn-30d",
      "endpoint_service_type": "sagemaker",
      "endpoint_container_url": "495303562198.dkr.ecr.us-west-1.amazonaws.com/static_prediction_endpoint:latest",
      "train_service_type": "sagemaker",
      "train_service_name": "static_prediction_training_job",
      "training_job_container_url": "495303562198.dkr.ecr.us-west-1.amazonaws.com/static_prediction_training_job:latest",
      "retrain_status_message": "{\"status\": \"SUCCEEDED\", \"message\": \"Proceeding to next step in pipeline, retraining not needed...\"}",
      "retrain_job_status": "SUCCEEDED",
      "redeploy_status_message": "{\"status\": \"SUCCEEDED\", \"message\": \"Proceeding to next step in pipeline, redeployment not needed...\"}",
      "redeploy_job_status": "SUCCEEDED"
    }

    event["config_path"] = os.path.join(event["config_path_prefix"],
                                        '.'.join([event["configuration_id"], "json"]))
    event["prediction_service_request_type"] = "prediction"

#    data = {"request_type":"prediction",
#            "data":event,
#            "config_path": event["config_path"]}
    body_bytestr = json.dumps(event).encode()
    data = [{'body': bytearray(body_bytestr)}]
    _service.initialize(context)
    rets = _service.handle(data, context)
    
#    print(rets)
