import boto3
from aws_lambda_powertools import Logger
import os
from datetime import datetime

LOGGER = Logger()

@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        _assume_remote_role()
    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e


def _assume_remote_role(remote_role_arn):
    try:
        # Assumes the provided role in the auditing member account and returns a session
        # Beginning the assume role process for account
        sts_client = boto3.client('sts')

        response = sts_client.assume_role(
            RoleArn=remote_role_arn,
            RoleSessionName='RemoteSession'
        )

        # Storing STS credentials
        session = boto3.Session(
            aws_access_key_id=response["Credentials"]["AccessKeyId"],
            aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
            aws_session_token=response["Credentials"]["SessionToken"]
        )
        return session

    except Exception as e:
        print(f'Was not able to assume role {remote_role_arn}')
        print(e)
        return None
