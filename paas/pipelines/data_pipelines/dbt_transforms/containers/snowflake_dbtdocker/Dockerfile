# This docker file creates the image that will be executed in AWS FARGATE.
#
# TODO;
#     - Find ways to slim the final docker image
#

FROM python:3.7-slim-buster

COPY ./entrypoint.sh /

ENV PYTHONUNBUFFERED=1

RUN chmod 700 /entrypoint.sh \
      && pip install awscli

# Points to the S3 bucket where the DBT project code is hosted 
ENV S3_CODE_BUCKET_DIR=s3://BUCKET/CODE_FOLDER_FOR_DBT_PROJECT

# The DBT project ,which is tar gzipped and stored in S3 under the "S3_CODE_BUCKET_DIR/dbtdataops".
# Ex: DBT_PROJECT=dbtoncloud
ENV DBT_PROJECT=dbtoncloud

# The shell script to invoke which will run the dbt related transformation pipeline
ENV DBT_RUN_SCRIPT=dbt_run.sh

ENV SFLK_INFO=ARN_FOR_SNOWFLAKE_SECRETS

ENTRYPOINT ["/entrypoint.sh"]
