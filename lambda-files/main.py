import boto3
from aws_lambda_powertools import Logger
import os
from datetime import datetime

LOGGER = Logger()
REGION = os.environ['AWS_REGION']

@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        _assume_remote_role()
        
    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e

