import json
import time
import os
import boto3
import botocore

REGION = os.environ['AWS_REGION']
TTL_IN_HOURS = 3

BOTO3_ORGANIZATIONS =  boto3.client('organizations')

class OrganizationsHelper:
    def __init__(self, logger):
        self.logger = logger
        self.organizations_client = self.organizations_client

    # ---------------------------------------------------------------------------------------------------------------------
    # ¦ CONTEXT CACHE HANDLING

    def get_organization_context(self):
        #iterate through all accounts of the organization and call get_member_account_context
        return list of get_member_account_context



    # ¦ get_member_account_context
    def get_member_account_context(self, member_account_id):
        account_info = self._organizations_describe_account(member_account_id)
        account_name = 'n/a'
        account_status = 'n/a'
        if 'Account' in account_info:
            if 'Name' in account_info['Account']:
                account_name = account_info['Account']['Name']
            if 'Status' in account_info['Account']:
                account_status = account_info['Account']['Status']
        caller_ou_id = self._organizations_get_ou_id(member_account_id)
        caller_ou_name, caller_ou_name_with_path = self._organizations_get_ou_name_with_path(member_account_id)      
        caller_account_tags = self._organizations_get_tags(member_account_id)

        return {
            'accountId': member_account_id,
            'accountName': account_name,
            'accountStatus': account_status,
            'accountTags': caller_account_tags,
            'ouId': caller_ou_id,
            'ouName': caller_ou_name,
            'ouNameWithPath': caller_ou_name_with_path,
            'ouTags': ot_tags
        }

    # ¦ _organizations_get_ou_id
    def _organizations_get_ou_id(self, account_id):
        response = self.organizations_client.list_parents(ChildId=account_id)
        if 'Parents' in response and len(response['Parents']) == 1:
            return response['Parents'][0]['Id']
        return None

    # ¦ _organizations_get_ou_name
    def _organizations_get_ou_name(self, ou_id):
        try:
            response = self.organizations_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
            return response['OrganizationalUnit']['Name']
        except Exception as e:
            return ""

    # ¦ _organizations_get_ou_name_with_path
    def _organizations_get_ou_name_with_path(self, account_id):
        try:
            parent_ou_id = ""
            ou_path = ""
            child_id = account_id
            while True:
                parents = self.organizations_client.list_parents(ChildId=child_id)
                parent_ou_id = parents['Parents'][0]['Id']
                if parents['Parents'][0]['Type'] == 'ROOT':
                    parent_ou_name = "Root"
                else:
                    parent_ou_name = self._organizations_get_ou_name(parent_ou_id)

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
    def _organizations_get_ou_name(self, ou_id):
        try:
            response = self.organizations_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
            return response['OrganizationalUnit']['Name']
        except self.organizations_client.exceptions.OrganizationalUnitNotFoundException:
            self.logger.error(f"Organizational unit not found: {ou_id}")
            return ""
        except self.organizations_client.exceptions.AWSOrganizationsNotInUseException:
            self.logger.error("AWS Organizations is not in use in this account.")
            return ""
        except Exception as e:
            self.logger.error(f"Unexpected error occurred while describing organizational unit {ou_id}: {e}")
            return ""

    # ¦ _organizations_describe_account
    def _organizations_describe_account(self, account_id):
        try:
            response = self.organizations_client.describe_account(AccountId=account_id)
            self.logger.info(f"Account description: {response}")
            return response
        except self.organizations_client.exceptions.AccountNotFoundException:
            self.logger.error(f"Account not found: {account_id}")
            return {}
        except self.organizations_client.exceptions.AWSOrganizationsNotInUseException:
            self.logger.error("AWS Organizations is not in use in this account.")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error occurred while describing account {account_id}: {e}")
            return {}
        
        
    # ¦ _organizations_get_tags
    def _organizations_get_tags(self, resource_id):
        ret_dict = {}
        paginator = self.organizations_client.get_paginator('list_tags_for_resource')
        try:
            for page in paginator.paginate(ResourceId=resource_id):
                for entry in page.get('Tags', []):
                    ret_dict[entry['Key']] = entry['Value']
        except Exception as e:
            self.logger.error(f"Error getting tags for resource {resource_id}: {e}")
        return ret_dict