import json
import time
import os
import boto3

REGION = os.environ['AWS_REGION']
CACHE_TTL_IN_MINUTES =  os.environ['CACHE_TTL_IN_MINUTES']
CONTEXT_CACHE_CLIENT = boto3.client('dynamodb', region_name=REGION)
CONTEXT_CACHE_RESOURCE = boto3.resource('dynamodb', region_name=REGION)

class ContextCacheHelper:
    def __init__(self, logger, organizations_helper):
        self.logger = logger
        self.organizations_helper = organizations_helper
        self.context_cache_table_name = os.environ['CONTEXT_CACHE_TABLE_NAME']
        self.context_cache_table = CONTEXT_CACHE_RESOURCE.Table(self.context_cache_table_name)

    # ¦ CONTEXT CACHE HANDLING
    def refresh_cache(self, originating_account_id):
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
        from_cache = self._context_cache_entry_get(originating_account_id, "AccountContext")
        if from_cache is None:
            from_api = self.organizations_helper.get_member_account_context(originating_account_id)
            self._context_cache_entry_add(originating_account_id, "AccountContext", from_api)
            self.logger.debug("Loaded account-context from API and stored to cache")
            return from_api
        else:
            self.logger.debug("Loaded account-context from cache")
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
            'timeToExist': int(time.time()) + CACHE_TTL_IN_MINUTES * 60
        }
        self.context_cache_table.put_item(Item=entry)
