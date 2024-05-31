import os
from context_cache import ContextCache
import logging
LOGLEVEL = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
logging.getLogger().setLevel(LOGLEVEL)
for noisy_log_source in ["boto3", "botocore", "nose", "s3transfer", "urllib3"]:
    logging.getLogger(noisy_log_source).setLevel(logging.WARN)
LOGGER = logging.getLogger()
ORG_READER_ROLE_ARN = os.environ['ORG_READER_ROLE_ARN']
CONTEXT_CACHE_TABLE_NAME = os.environ['CONTEXT_CACHE_TABLE_NAME']

def lambda_handler(event, context):
    try:
        context_cache = ContextCache(LOGGER, ORG_READER_ROLE_ARN, CONTEXT_CACHE_TABLE_NAME)
        if event.get('account_id', None) != None:
            return context_cache.get_member_account_context(event.get('account_id'))
        
    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e
