import json
import time
import os
import boto3
import logging
from typing import Dict, Any, List
from acai.cache.helper_organizations import OrganizationsHelper

# Environment setup
REGION = os.environ['AWS_REGION']
CONTEXT_CACHE_CLIENT = boto3.client('dynamodb', region_name=REGION)
CONTEXT_CACHE_RESOURCE = boto3.resource('dynamodb', region_name=REGION)
STS_CLIENT = boto3.client('sts')
LOCAL_CACHE: Dict[str, Dict[str, Any]] = {}

class ContextCache:
    def __init__(self, logger: logging.Logger, org_reader_role_arn: str, context_cache_table_name: str, drop_attributes: list = []):
        self.logger = logger
        self.organizations_helper = OrganizationsHelper(logger, org_reader_role_arn)
        self.context_cache_table_name = context_cache_table_name
        self.drop_attributes = drop_attributes
        self.cache_ttl_in_minutes = self._get_ttl_from_dynamodb_tags()
        self.context_cache_table = CONTEXT_CACHE_RESOURCE.Table(self.context_cache_table_name)
        self.local_cache = LOCAL_CACHE
        self.logger.info(f"Registered for cache-store {context_cache_table_name} with TTL {self.cache_ttl_in_minutes} minutes and local-cache with {len(self.local_cache)} items")
        self.get_all_account_contexts()
        
    # ¦ refresh_cache
    def refresh_cache(self) -> None:
        all_accounts = self.organizations_helper.list_all_accounts()
        for account in all_accounts:
            account_id = account['Id']
            self.get_member_account_context(account_id, load_from_api=True)
        self.logger.info(f"Items in cache-store {self.context_cache_table_name}: {len(self.local_cache)}")

    # ¦ reset_cache
    def reset_cache(self) -> None:
        self.local_cache.clear()
        self.logger.info("Local cache cleared.")

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

    # ¦ get_all_account_contexts
    def get_all_account_contexts(self) -> Dict[str, Any]:
        # Load Cache from DDB
        all_accounts = self.organizations_helper.list_all_accounts()
        for account in all_accounts:
            account_id = account['Id']
            self.get_member_account_context(account_id)
        return self.local_cache

    # ¦ get_member_account_context
    def get_member_account_context(self, account_id: str, load_from_api: bool = False) -> Any:
        cache_entry = None
        if not load_from_api:
            cache_entry = self._context_cache_entry_get(account_id, "AccountContext")
        if cache_entry is None:
            from_api = self.organizations_helper.get_member_account_context(account_id)
            if self.drop_attributes:
                for attribute in self.drop_attributes:
                    self._remove_nested_attribute(from_api, attribute)
            if from_api is not None:
                self._context_cache_entry_add(account_id, "AccountContext", from_api)
                self.logger.debug("Loaded account-context from API and stored to cache-store and local-cache")
            else:
                self.logger.info(f"Account {account_id} was not found.")
            return from_api
        return cache_entry

    # ¦ get_local_cache
    def get_local_cache(self) -> Dict[str, Any]:
        return self.local_cache

    # ¦ _context_cache_entry_get
    def _context_cache_entry_get(self, account_id: str, context_id: str) -> Any:
        if account_id in self.local_cache:
            local_entry = self.local_cache[account_id]
            if local_entry['timeToExist'] > time.time():
                self.logger.debug(f"Loaded account-context from local cache {account_id}")
                return local_entry['cacheObject']
            else:
                self.logger.debug(f"Local cache entry for {account_id} expired. Removing from local cache.")
                del self.local_cache[account_id]
                return None
        
        self.logger.debug(f"Account-context for {account_id} not in local cache. Will load from DDB.")
        cache_entry = self._load_from_dynamodb(account_id, context_id)
        return cache_entry

    # ¦ _load_from_dynamodb
    def _load_from_dynamodb(self, account_id: str, context_id: str) -> Any:
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

        if result_tmp:
            cache_entry = json.loads(result_tmp[0]['cacheObject']['S'])
            self.logger.debug(f"Loaded account-context from cache-store {account_id}")
            self.local_cache[account_id] = {
                'cacheObject': cache_entry,
                'timeToExist': int(result_tmp[0]['timeToExist']['N'])
            }
            self.logger.debug(cache_entry)
            return cache_entry

        self.logger.debug(f"Account-context for {account_id} not found in cache-store.")
        return None

    # ¦ _context_cache_entry_add
    def _context_cache_entry_add(self, account_id: str, context_id: str, value_dict: Dict[str, Any]) -> None:
        entry = {
            'accountId': account_id,
            'contextId': context_id,
            'cacheObject': json.dumps(value_dict),
            'timeToExist': int(time.time()) + self.cache_ttl_in_minutes * 60
        }
        self.context_cache_table.put_item(Item=entry)
        self.local_cache[account_id] = {
            'cacheObject': value_dict,
            'timeToExist': entry['timeToExist']
        }

    # ¦ _get_account_id
    def _get_account_id(self) -> str:
        response = STS_CLIENT.get_caller_identity()
        return response['Account']
    
    # ¦ _get_ttl_from_dynamodb_tags
    def _get_ttl_from_dynamodb_tags(self) -> int:
        response = CONTEXT_CACHE_CLIENT.list_tags_of_resource(
            ResourceArn=f'arn:aws:dynamodb:{REGION}:{self._get_account_id()}:table/{self.context_cache_table_name}'
        )
        tags = response['Tags']
        for tag in tags:
            if tag['Key'] == 'cache_ttl_in_minutes':
                return int(tag['Value'])
        return 60  # Default TTL if tag is not found

    # ¦ remove_nested_attribute
    def _remove_nested_attribute(self, data, nested_key):
        keys = nested_key.split('.')
        current = data
        for key in keys[:-1]:  # Navigate to the parent dictionary of the key to be removed
            if key in current:
                current = current[key]
            else:
                return  # Key path does not exist, exit the function
        if keys[-1] in current:
            del current[keys[-1]]  # Delete the key if it exists
            
