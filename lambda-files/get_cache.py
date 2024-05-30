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
    def __init__(self, context_logger, context_cache_table_name):
        self.logger = context_logger
        self.context_cache_table_name = context_cache_table_name
        # CONTEXT CACHE
        self.context_cache_table = CONTEXT_CACHE_RESOURCE.Table(context_cache_table_name)

    # ---------------------------------------------------------------------------------------------------------------------
    # ¦ CONTEXT CACHE HANDLING
    def get_member_account_context(self, originating_account_id):
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


    # ¦ _get_member_account_context
    def _get_member_account_context(self, member_account_id):
        account_info_client = boto3.client('organizations')
        account_info = self._organizations_describe_account(account_info_client, member_account_id)
        account_name = 'n/a'
        account_status = 'n/a'
        if 'Account' in account_info:
            if 'Name' in account_info['Account']:
                account_name = account_info['Account']['Name']
            if 'Status' in account_info['Account']:
                account_status = account_info['Account']['Status']
        caller_ou_id = self._organizations_get_ou_id(account_info_client, member_account_id)
        caller_ou_name, caller_ou_name_with_path = self._organizations_get_ou_name_with_path(account_info_client, member_account_id)      
        caller_account_tags = self._organizations_get_tags(account_info_client, member_account_id)

        return {
            'accountId': member_account_id,
            'accountName': account_name,
            'accountStatus': account_status,
            'accountTags': caller_account_tags,
            'ouId': caller_ou_id,
            'ouName': caller_ou_name,
            'ouNameWithPath': caller_ou_name_with_path
        }

    # ¦ _organizations_get_ou_id
    def _organizations_get_ou_id(self, boto_client, account_id):
        response = boto_client.list_parents(ChildId=account_id)
        if 'Parents' in response and len(response['Parents']) == 1:
            return response['Parents'][0]['Id']
        return None

    # ¦ _organizations_get_ou_name
    def _organizations_get_ou_name(self, boto_client, ou_id):
        try:
            response = boto_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
            return response['OrganizationalUnit']['Name']
        except Exception as e:
            return ""

    # ¦ _organizations_get_ou_name_with_path
    def _organizations_get_ou_name_with_path(self, boto_client, account_id):
        try:
            parent_ou_id = ""
            ou_path = ""
            child_id = account_id
            while True:
                parents = boto_client.list_parents(ChildId=child_id)
                parent_ou_id = parents['Parents'][0]['Id']
                if parents['Parents'][0]['Type'] == 'ROOT':
                    parent_ou_name = "Root"
                else:
                    parent_ou_name = self._organizations_get_ou_name(boto_client, parent_ou_id)

                if child_id == account_id:
                    direct_parent_ou_name = parent_ou_name

                ou_path = parent_ou_name + "/" + ou_path
                
                if parents['Parents'][0]['Type'] == 'ROOT':
                    return direct_parent_ou_name, ou_path
                else:
                    # parent is new child
                    child_id = parent_ou_id

        except Exception as e:
            return ""

    # ¦ _organizations_get_ou_name
    def _organizations_get_ou_name(self, boto_client, ou_id):
        try:
            response = boto_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
            return response['OrganizationalUnit']['Name']
        except Exception as e:
            return ""

    # ¦ _organizations_describe_account
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations.html#Organizations.Client.describe_account
    def _organizations_describe_account(self, boto_client, account_id):
        try:
            response = boto_client.describe_account(AccountId=account_id)
            self.logger.info(response)
            return response
        except Exception as e:
            return ""

    # ¦ _organizations_get_tags
    def _organizations_get_tags(self, boto_client, account_id):
        ret_dict = dict()
        paginator = boto_client.get_paginator('list_tags_for_resource')
        for page in paginator.paginate(ResourceId=account_id):
            for entry in page['Tags']:
                ret_dict.update({entry['Key']: entry['Value']})
        return ret_dict