from aws_lambda_powertools import Logger
import json
import os
from datetime import datetime
from helper_cache import ContextCacheHelper

LOGGER = Logger()
ORG_READER_ROLE_ARN = os.environ['ORG_READER_ROLE_ARN']
CONTEXT_CACHE_TABLE_NAME = os.environ['CONTEXT_CACHE_TABLE_NAME']
CACHE_TTL_IN_MINUTES = os.environ['CACHE_TTL_IN_MINUTES']

@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        cache_helper = ContextCacheHelper(LOGGER, ORG_READER_ROLE_ARN, CONTEXT_CACHE_TABLE_NAME, CACHE_TTL_IN_MINUTES)
        cache_helper.refresh_cache()
        LOGGER.info(f'Cache {cache_helper.local_cache}')
                
    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e

