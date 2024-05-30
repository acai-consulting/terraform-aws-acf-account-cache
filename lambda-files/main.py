from aws_lambda_powertools import Logger
import json
import os
from datetime import datetime
from helper_cache import OrganizationsHelper
from helper_organizations import ContextCacheHelper

LOGGER = Logger()
CONTEXT_CACHE_TABLE_NAME = os.environ['CONTEXT_CACHE_TABLE_NAME']
ORG_READER_ROLE_ARN = os.environ['ORG_READER_ROLE_ARN']

@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        org_helper = OrganizationsHelper(LOGGER, ORG_READER_ROLE_ARN)
        cache_helper = ContextCacheHelper(LOGGER, org_helper)
        cache_helper.refresh_expired_cache_entries()
        org_info = org_helper.get_organization_context()
        LOGGER.info(f'Organization Info: {org_info}')
                
    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e

