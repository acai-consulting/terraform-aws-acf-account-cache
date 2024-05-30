from aws_lambda_powertools import Logger
import json
from datetime import datetime
from helper_organizations import OrganizationsHelper

LOGGER = Logger()

@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    try:
        organizations = OrganizationsHelper(LOGGER)
        org_info = organizations.get_organization_context()
        LOGGER.info(f'Organization Info: {org_info}')
                
    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e

