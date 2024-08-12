import os
import logging
from aws_lambda_powertools import Logger
from acai.cache.context_cache import ContextCache
from acai.cache_query.context_cache_query import ContextCacheQuery
from typing import Any, Dict

# Logging setup
def setup_logging() -> Logger:
    log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
    logger = Logger(
        service="acai-account-cache",
        level=log_level,
    )

    # Set less verbose logging for noisy libraries
    for noisy_log_source in ["boto3", "botocore", "nose", "s3transfer", "urllib3"]:
        logging.getLogger(noisy_log_source).setLevel(logging.WARN)

    return logger

LOGGER: Logger = setup_logging()

# Environment Variables
ORG_READER_ROLE_ARN = os.environ['ORG_READER_ROLE_ARN']
CONTEXT_CACHE_TABLE_NAME = os.environ['CONTEXT_CACHE_TABLE_NAME']
DROP_ATTRIBUTES = os.environ.get('DROP_ATTRIBUTES', '').split(",")

def is_scheduled_event(event: Dict[str, Any]) -> bool:
    return event.get('source') == 'aws.events'

def handle_scheduled_event(context_cache: ContextCache) -> Dict[str, Any]:
    context_cache.refresh_cache()
    LOGGER.info("Cache refreshed by scheduled event")
    return {"status": "cache refreshed by scheduled event"}

def handle_action_event(event: Dict[str, Any], context_cache: ContextCache) -> Dict[str, Any]:
    action = event.get('action', '').lower()
    account_id = event.get('account_id')
    query = event.get('query')
    query_full = event.get('query_full')

    if account_id:
        return context_cache.get_member_account_context(account_id)
    
    if action == 'refresh':
        context_cache.refresh_cache()
        return {"status": "cache refreshed"}

    if action == 'reset':
        context_cache.reset_cache()
        return {"status": "cache reset"}

    if action == 'all':
        return context_cache.get_all_account_contexts()

    if query:
        context_cache_query = ContextCacheQuery(LOGGER, context_cache)
        result = context_cache_query.query_cache(query)
        del result['account_context_list']
        return {"query": query, "result": result}

    if query_full:
        context_cache_query = ContextCacheQuery(LOGGER, context_cache)
        result = context_cache_query.query_cache(query_full)
        return {"query": query_full, "result": result}

    cache_items_count = len(context_cache.get_local_cache())
    LOGGER.info(f"Items in cache-store {CONTEXT_CACHE_TABLE_NAME}: {cache_items_count}")
    return {"status": f"items in cache: {cache_items_count}"}

@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        context_cache = ContextCache(
            logger=LOGGER, 
            org_reader_role_arn=ORG_READER_ROLE_ARN, 
            context_cache_table_name=CONTEXT_CACHE_TABLE_NAME, 
            drop_attributes = DROP_ATTRIBUTES
        )

        if is_scheduled_event(event):
            return handle_scheduled_event(context_cache)

        return handle_action_event(event, context_cache)

    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}', exc_info=True)
        raise e
