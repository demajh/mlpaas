import os
import sys
import uuid

class CodeGenerator:

    def __init__(self):

        self.cloud_provider_iac_frameworks = {"aws": "cdk",
                                              "gcp": "pulumi",
                                              "azure": "pulumi"}
        return

    def generate_extract_data(self, extract_source, extract_source_name):

        """
        Prompts:
        s3: "Generate the code to read a csv from S3 and save it to a pandas dataframe."
        """

        if extract_source=="s3":
            source_bucket = extract_source_name.split('/')[2]
            source_prefix = '/'.join(extract_source_name.split('/')[3:])
            code_str = """
        s3_client = boto3.client('s3')
        obj = s3_client.get_object(Bucket= {}, Key= {})
        source_df = pd.read_csv(obj['Body'])
            """.format("'{}'".format(source_bucket), "'{}'".format(source_prefix))
        else:
            raise Exception("Unrecognized source type.  Source given is {}.".format(extract_source))

        return code_str

    def generate_load_target(self, load_target, load_target_name):

        """
        Prompts:
        rds: "Generate the code to create an RDS table and ingest a pandas dataframe called source_df."
        """

        if load_target=="rds":
            code_str = """
        try:
            engine = sa.create_engine('postgresql://{}:{}@{}:{}/{}'.format(USER, PASSWORD, HOST, PORT, DATABASE))
        except:
            raise Exception("I am unable to connect to the database.")

        table_name = str(uuid.uuid4())
        try:
            print(bool(engine)) # <- just to keep track of the process
            source_df.to_sql(name=table_name, con = engine, if_exists = 'replace', index = False)
        except:
            raise Exception("I can't create the requested database table!")
        target_df = pd.read_sql('SELECT * FROM "{}"'.format(table_name), con = engine)
        assert(source_df.shape[0]==target_df.shape[0] and source_df.shape[1]==target_df.shape[1])
        print(target_df)
            """
        else:
            raise Exception("Unrecognized target type.  Target given is {}.".format(load_target))

        return code_str

    def generate_sync_source_target(self, extract_source, extract_source_name, load_target):
        """
        Prompts:
        s3_rds: "Generate the code to upload a CSV file in S3 to an RDS table."
        """

        if extract_source=="s3" and load_target=="rds":
            code_str = """
        try:
            conn = psycopg2.connect(database = DATABASE, user = USER, password = PASSWORD, host = HOST, port = PORT, schema = SCHEMA)
        except:
            raise Exception("I am unable to connect to the database.")
        
        cur = conn.cursor()
        try:
            #--select example
            tele_data_insert = '''COPY {}.{}.'{}' FROM '{}' IAM_ROLE '{}' FORMAT AS CSV DELIMITER '|' QUOTE '"' REGION AS '{}'            
            '''.format(DATABASE, SCHEMA, table_name, EXTRACT_SOURCE_NAME, IAM_ROLE, DATABASE_REGION)
            print("Executing table insertion...")
            tele_data_out = s.execute(tele_data_insert)
            s.commit()
        except:
            raise Exception("I can't create the requested database table!")
        conn.commit() # <--- makes sure the change is shown in the database
        conn.close()
        cur.close()
            """
        else:
            raise Exception("Unrecognized target type.  Target given is {}.".format(load_target))

        return code_str

    def generate_serverless_function(self,
                                     cloud_provider,
                                     iac_framework,
                                     role_name,
                                     role_arn,
                                     function_name,
                                     image_directory):

        """
        Prompts:
        aws_cdk: "Generate the code to create a serverless function on AWS using the CDK."
        """

        if cloud_provider == "aws" and iac_framework == "cdk":
            code_str = """
        role = _iam.Role.from_role_arn(self, "{}", "{}", mutable=False)
        lambda_function_name = "{}"
        curr_image = _lambda.EcrImageCode.from_asset_image(directory = "{}")
        # create lambda function
        function = _lambda.Function(self, lambda_function_name,
                                    function_name=lambda_function_name,
                                    runtime=_lambda.Runtime.FROM_IMAGE,
                                    handler=_lambda.Handler.FROM_IMAGE,
                                    code=curr_image,
                                    role=role,
                                    memory_size=10000,
                                    timeout=Duration.seconds(900),
                                    environment=dict(PYTHONPATH='/'))
            """.format(role_name,
                       role_arn,
                       function_name,
                       image_directory)
        else:
            raise Exception("Unrecognized cloud_provider and iac_framework combination.  Provided values are {}.".format(cloud_provider, iac_framework))

        return code_str

    def generate_service_infrastructure(self,
                                        cloud_provider,
                                        service_type,
                                        service_resource_type,
                                        service_role_identifiers,
                                        service_image_path):

        iac_framework = self.cloud_provider_iac_frameworks[cloud_provider]
        if service_resource_type == "serverless":
            function_name = '-'.join([service_type, str(uuid.uuid4())])
            service_role_name = service_role_identifiers[0]
            service_role_arn = service_role_identifiers[1]
            service_code_str = self.generate_serverless_function(cloud_provider,
                                                                 iac_framework,
                                                                 service_role_name,
                                                                 service_role_arn,
                                                                 function_name,
                                                                 service_image_path)

        else:

            raise Exception("Unrecognized service_resource_type!!  Value given: {}".format(service_resource_type))

        return service_code_str

    def generate_pipeline_infrastructure(self,
                                         cloud_provider,
                                         pipeline_type,
                                         pipeline_resource_type,
                                         pipeline_image_path):

        return ""




