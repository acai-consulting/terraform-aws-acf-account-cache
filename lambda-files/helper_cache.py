import json
import time
import os
import boto3
from helper_organizations import OrganizationsHelper

REGION = os.environ['AWS_REGION']
CONTEXT_CACHE_CLIENT = boto3.client('dynamodb', region_name=REGION)
CONTEXT_CACHE_RESOURCE = boto3.resource('dynamodb', region_name=REGION)
LOCAL_CACHE = {}  # Define local cache at the module level

class ContextCacheHelper:
    def __init__(self, logger, org_reader_role_arn, context_cache_table_name, cache_ttl_in_minutes):
        self.logger = logger
        self.organizations_helper = OrganizationsHelper(logger, org_reader_role_arn)
        self.context_cache_table_name = context_cache_table_name
        self.cache_ttl_in_minutes = int(cache_ttl_in_minutes)  # Ensure this is an integer
        self.context_cache_table = CONTEXT_CACHE_RESOURCE.Table(self.context_cache_table_name)
        self.local_cache = LOCAL_CACHE

    def refresh_cache(self):
        self.logger.debug(f"Items in local cache {len(self.local_cache)}")
        all_accounts = self.organizations_helper.list_all_accounts()

        for account in all_accounts:
            account_id = account['Id']
            self.get_member_account_context(account_id)

    def get_all_account_contexts(self):
        self.refresh_cache()
        return self.local_cache

    def get_member_account_context(self, account_id):
        # If not in local cache or expired, check DynamoDB cache
        cache_entry = self._context_cache_entry_get(account_id, "AccountContext")
        if cache_entry is None:
            # If not in DynamoDB cache, get from API and update both caches
            from_api = self.organizations_helper.get_member_account_context(account_id)
            self._context_cache_entry_add(account_id, "AccountContext", from_api)
            self.logger.debug("Loaded account-context from API and stored to cache-store and local-cache")
            return from_api
        return cache_entry

    def get_local_cache(self):
        return self.local_cache

    # ¦ _context_cache_entry_get
    def _context_cache_entry_get(self, account_id, context_id):
        if account_id in self.local_cache:
            local_entry = self.local_cache[account_id]
            if local_entry['timeToExist'] > time.time():
                self.logger.debug(f"Loaded account-context from local cache {account_id}")
                return local_entry['cacheValue']
            else:
                # remove entry from local cache
                del self.local_cache[account_id]
                return None
        else:
            self.logger.debug(f"Account-context for {account_id} not in local cache. Will load from DDB.")
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
                self.logger.debug(f"Loaded account-context from cache-store {account_id}")
                # Update local cache
                self.local_cache[account_id] = {
                    'cacheValue': cache_entry,
                    'timeToExist': int(result_tmp[0]['timeToExist']['N'])
                }                
                self.logger.debug(cache_entry)
                return cache_entry
            else:
                self.logger.debug(f"Account-context for {account_id} not found in cache-store.")
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
