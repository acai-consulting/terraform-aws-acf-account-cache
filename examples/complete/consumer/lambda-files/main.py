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
        context_cache.get_all_account_contexts()
        LOGGER.info(f'Cache {context_cache.local_cache}')

        context_cache.refresh_cache()
        LOGGER.info(f'Cache after refresh {context_cache.local_cache}')

        context_cache.reset_cache()
        LOGGER.info(f'Cache after reset {context_cache.local_cache}')

        context_cache.refresh_cache()
        LOGGER.info(f'Cache after refresh {context_cache.local_cache}')

        LOGGER.info(context_cache.get_member_account_context("1234"))
    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e
