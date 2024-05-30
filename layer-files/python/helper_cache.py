import json
import time
import os
import boto3
from helper_organizations import OrganizationsHelper

REGION = os.environ['AWS_REGION']
CONTEXT_CACHE_CLIENT = boto3.client('dynamodb', region_name=REGION)
CONTEXT_CACHE_RESOURCE = boto3.resource('dynamodb', region_name=REGION)

class ContextCacheHelper:
    def __init__(self, logger, org_reader_role_arn, context_cache_table_name, cache_ttl_in_minutes):
        self.logger = logger
        self.organizations_helper = OrganizationsHelper(logger, org_reader_role_arn)
        self.context_cache_table_name = context_cache_table_name
        self.cache_ttl_in_minutes = cache_ttl_in_minutes
        self.context_cache_table = CONTEXT_CACHE_RESOURCE.Table(self.context_cache_table_name)
        self.local_cache = {}

    def refresh_cache(self):
        all_accounts = self.organizations_helper._list_all_accounts()
        expired_accounts = []

        for account in all_accounts:
            account_id = account['Id']
            cache_entry = self._context_cache_entry_get(account_id, "AccountContext")
            if cache_entry is None:
                expired_accounts.append(account_id)

        for account_id in expired_accounts:
            context_data = self.organizations_helper.get_member_account_context(account_id)
            self._context_cache_entry_add(account_id, "AccountContext", context_data)
            self.logger.debug(f"Refreshed cache for account {account_id}")

    def get_member_account_context(self, originating_account_id):
        # Check local cache first
        if originating_account_id in self.local_cache:
            local_entry = self.local_cache[originating_account_id]
            if local_entry['timeToExist'] > time.time():
                self.logger.debug("Loaded account-context from local cache")
                return local_entry['cacheValue']

        # If not in local cache or expired, check DynamoDB cache
        from_cache = self._context_cache_entry_get(originating_account_id, "AccountContext")
        if from_cache is None:
            # If not in DynamoDB cache, get from API and update both caches
            from_api = self.organizations_helper.get_member_account_context(originating_account_id)
            self._context_cache_entry_add(originating_account_id, "AccountContext", from_api)
            self.logger.debug("Loaded account-context from API and stored to caches")
            return from_api
        else:
            # Update local cache
            self.local_cache[originating_account_id] = {
                'cacheValue': from_cache,
                'timeToExist': int(time.time()) + self.cache_ttl_in_minutes * 60
            }
            self.logger.debug("Loaded account-context from DynamoDB cache and updated local cache")
            return from_cache

    # ¦ _context_cache_entry_get
    def _context_cache_entry_get(self, account_id, context_id):
        result_tmp = []
        paginator = CONTEXT_CACHE_CLIENT.get_paginator('scan')
        for page in paginator.paginate(
            TableName=self.context_cache_table_name,
            ScanFilter={
                "accountId": {
                    "AttributeValueList": [
                        {"S": account_id}
                    ],
                    "ComparisonOperator": "EQ"
                },
                "contextId": {
                    "AttributeValueList": [
                        {"S": context_id}
                    ],
                    "ComparisonOperator": "EQ"
                },
            }):

            for item in page['Items']:
                if int(item['timeToExist']['N']) > int(time.time()):
                    result_tmp.append(item)

        if len(result_tmp) > 0:
            cache_entry = json.loads(result_tmp[0]['cacheValue']['S'])
            if 'ouNameWithPath' in cache_entry:
                return cache_entry
            else:
                return None

        return None

    # ¦ _context_cache_entry_add
    def _context_cache_entry_add(self, account_id, context_id, value_dict):
        entry = {
            'accountId': account_id,
            'contextId': context_id,
            'cacheValue': json.dumps(value_dict),
            'timeToExist': int(time.time()) + self.cache_ttl_in_minutes * 60
        }
        self.context_cache_table.put_item(Item=entry)
        # Update local cache as well
        self.local_cache[account_id] = {
            'cacheValue': value_dict,
            'timeToExist': entry['timeToExist']
        }
