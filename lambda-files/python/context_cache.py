import json
import time
import os
import boto3
from helper_organizations import OrganizationsHelper

REGION = os.environ['AWS_REGION']
CONTEXT_CACHE_CLIENT = boto3.client('dynamodb', region_name=REGION)
CONTEXT_CACHE_RESOURCE = boto3.resource('dynamodb', region_name=REGION)
STS_CLIENT = boto3.client('sts')
LOCAL_CACHE = {}  # Define local cache at the module level

class ContextCache:
    def __init__(self, logger, org_reader_role_arn, context_cache_table_name, ddb_ttl_tag_name = 'cache_ttl_in_minutes'):
        self.logger = logger
        self.organizations_helper = OrganizationsHelper(logger, org_reader_role_arn)
        self.context_cache_table_name = context_cache_table_name
        self.ddb_ttl_tag_name = ddb_ttl_tag_name
        self.cache_ttl_in_minutes = self._get_ttl_from_dynamodb_tags()
        self.context_cache_table = CONTEXT_CACHE_RESOURCE.Table(self.context_cache_table_name)
        self.local_cache = LOCAL_CACHE
        self.logger.info(f"Registered for cache-store {context_cache_table_name} with TTL {self.cache_ttl_in_minutes} minutes and local-cache with {len(self.local_cache)} items")

    def reset_cache(self):
        # Clear the local cache
        self.local_cache.clear()
        self.logger.info("Local cache cleared.")

        # Scan the DynamoDB table to get all items
        scan_response = CONTEXT_CACHE_CLIENT.scan(
            TableName=self.context_cache_table_name,
            ProjectionExpression='accountId, contextId'
        )
        
        with self.context_cache_table.batch_writer() as batch:
            for item in scan_response['Items']:
                batch.delete_item(
                    Key={
                        'accountId': item['accountId']['S'],
                        'contextId': item['contextId']['S']
                    }
                )
        self.logger.info(f"DynamoDB table {self.context_cache_table_name} cleared.")

    def refresh_cache(self):
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
                # Remove expired entry from local cache
                self.logger.debug(f"Local cache entry for {account_id} expired. Removing from local cache.")
                del self.local_cache[account_id]
                return None
        
        self.logger.debug(f"Account-context for {account_id} not in local cache. Will load from DDB.")
        
        # If not in local cache or expired, check DynamoDB cache
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
                # If item exists and has not expired, use it
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


    def _get_account_id(self):
        response = STS_CLIENT.get_caller_identity()
        return response['Account']
    
    # Method to get TTL from DynamoDB tags
    def _get_ttl_from_dynamodb_tags(self):
        response = CONTEXT_CACHE_CLIENT.list_tags_of_resource(
            ResourceArn=f'arn:aws:dynamodb:{REGION}:{self._get_account_id()}:table/{self.context_cache_table_name}'
        )
        tags = response['Tags']
        for tag in tags:
            if tag['Key'] == self.ddb_ttl_tag_name:
                return int(tag['Value'])
        # Default TTL if tag is not found
        return 60
        