##############################################################################
#
# This simple python script is used to retrieve specific keys from the passed in secrets manager key
# and return the result
##############################################################################

import boto3
from botocore.exceptions import ClientError
import os ,sys, json
import dbt.main
import logging

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.basicConfig(tream=sys.stdout ,level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_secret_by_arn(secret_arn):
    text_secret_data = ''
    binary_secret_data = '' #TODO correct to appropriate binary data declaration
    client = boto3.client('secretsmanager')

    try:
        logging.info('Retreiving secrets ...')
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            text_secret_data = get_secret_value_response['SecretString']
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']

    return text_secret_data
 
if __name__ == "__main__":
    secret_name=sys.argv[1]
    
    text_secret_data = get_secret_by_arn(secret_name)
    print("__SECRETS__ " + text_secret_data)
