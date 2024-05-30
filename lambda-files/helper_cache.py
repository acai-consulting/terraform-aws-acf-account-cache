import json
import time
import os
import boto3
import botocore

REGION = os.environ['AWS_REGION']
TTL_IN_HOURS = 3
CONTEXT_CACHE_CLIENT = boto3.client('dynamodb', region_name=REGION)
CONTEXT_CACHE_RESOURCE = boto3.resource('dynamodb', region_name=REGION)

class ContextCacheHelper:
    def __init__(self, logger, organizations_helper):
        self.logger = logger
        self.organizations_helper = organizations_helper
        self.context_cache_table_name = os.environ['CONTEXT_CACHE_TABLE_NAME']
        # CONTEXT CACHE
        self.context_cache_table = CONTEXT_CACHE_RESOURCE.Table(self.context_cache_table_name)

    # ---------------------------------------------------------------------------------------------------------------------
    # ¦ CONTEXT CACHE HANDLING
    def refresh_cache(self, originating_account_id):
        from_cache = self._context_cache_entry_get(originating_account_id, "AccountContext")
        if from_cache is None:
            from_api = self._get_member_account_context(originating_account_id)
            # store to cache
            self._context_cache_entry_add(originating_account_id, "AccountContext", from_api)
            self.logger.debug("Loaded account-context from api and stored to cache")
            return from_api
        else:
            self.logger.debug("Loaded account-context from cache")
            return from_cache

    # ¦ _context_cache_entry_get
    def _context_cache_entry_get(self, account_id, context_id):
        result_tmp = list()
        paginator = CONTEXT_CACHE_CLIENT.get_paginator('scan')
        for page in paginator.paginate(
            TableName=self.context_cache_table_name,
            ScanFilter= {
                "accountId": {
                    "AttributeValueList": [ 
                        { 
                            "S": account_id
                        }
                    ],
                    "ComparisonOperator": "EQ"
                },
                "contextId": {
                    "AttributeValueList": [ 
                        { 
                            "S": context_id
                        }
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
        # Add value_dict to cache
        entry = {
            'accountId': account_id,
            'contextId': context_id,
            'cacheValue': json.dumps(value_dict),
            'timeToExist': int(time.time()) + TTL_IN_HOURS * 60 * 60
        }
        response = self.context_cache_table.put_item(Item=entry)

