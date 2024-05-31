from aws_lambda_powertools import Logger
import os
from context_cache import ContextCache

loglevel = "DEBUG" # os.environ.get('LOG_LEVEL', 'INFO').upper()
LOGGER = Logger(service="acai-account-cache", level=loglevel)
ORG_READER_ROLE_ARN = os.environ['ORG_READER_ROLE_ARN']
CONTEXT_CACHE_TABLE_NAME = os.environ['CONTEXT_CACHE_TABLE_NAME']
DDB_TTL_TAG_NAME = os.environ.get('DDB_TTL_TAG_NAME', 'cache_ttl_in_minutes')

@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        context_cache = ContextCache(LOGGER, ORG_READER_ROLE_ARN, CONTEXT_CACHE_TABLE_NAME)
        if event.get('account_id', None) != None:
            return context_cache.get_member_account_context(event.get('account_id'))
        elif event.get('action', '').lower() == 'reset':
            context_cache.reset_cache()
        else:
            context_cache.refresh_cache()
        
        LOGGER.info(f'Cache {context_cache.local_cache}')

    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e

