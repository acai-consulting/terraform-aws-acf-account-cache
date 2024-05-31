import boto3

class OrganizationsHelper:
    def __init__(self, logger, org_reader_role_arn):
        self.logger = logger
        self.ou_id_with_path_cache = {}
        self.ou_name_cache = {}
        self.ou_name_with_path_cache = {}
        self.ou_tags_cache = {}
        remote_session = self._assume_remote_role(org_reader_role_arn)
        if remote_session:
            self.organizations_client = remote_session.client('organizations')
        else:
            self.organizations_client = boto3.client('organizations')

    # ¦ list_all_accounts
    def list_all_accounts(self):
        accounts = []
        paginator = self.organizations_client.get_paginator('list_accounts')
        try:
            for page in paginator.paginate():
                accounts.extend(page.get('Accounts', []))
        except Exception as e:
            self.logger.error(f"Error listing accounts: {e}")
        return accounts

    # ¦ CONTEXT CACHE HANDLING
    def get_organization_context(self):
        account_list = self.list_all_accounts()
        return [self.get_member_account_context(account['Id']) for account in account_list]

    # ¦ get_member_account_context
    def get_member_account_context(self, member_account_id):
        account_info = self._describe_account(member_account_id)
        if not account_info:
            return None
        account_name = account_info.get('Account', {}).get('Name', 'n/a')
        account_status = account_info.get('Account', {}).get('Status', 'n/a')
        caller_ou_id, caller_ou_id_with_path = self._get_ou_id_with_path(member_account_id)
        caller_ou_name, caller_ou_name_with_path = self._get_ou_name_with_path(caller_ou_id)
        caller_account_tags = self._get_tags(member_account_id)
        ou_tags = self._get_tags(caller_ou_id) if caller_ou_id else {}

        return {
            'accountId': member_account_id,
            'accountName': account_name,
            'accountStatus': account_status,
            'accountTags': caller_account_tags,
            'ouId': caller_ou_id,
            'ouIdWithPath': caller_ou_id_with_path,
            'ouName': caller_ou_name,
            'ouNameWithPath': caller_ou_name_with_path,
            'ouTags': ou_tags
        }

    # ¦ _get_ou_id_with_path
    def _get_ou_id_with_path(self, account_id):
        try:
            ou_id_path = []
            child_id = account_id
            while True:
                parents = self.organizations_client.list_parents(ChildId=child_id)
                parent = parents['Parents'][0]
                parent_ou_id = parent['Id']
                
                ou_id_path.append(parent_ou_id)
                if parent_ou_id in self.ou_id_with_path_cache:
                    entry = self.ou_id_with_path_cache[parent_ou_id]
                    return entry.get('ou_id'), entry.get('ou_id_path_str')
                else:
                    if parent['Type'] == 'ROOT':
                        ou_id_path_str = "/".join(reversed(ou_id_path))
                        self.ou_id_with_path_cache[parent_ou_id] = (parent_ou_id, ou_id_path_str)
                        return parent_ou_id, ou_id_path_str
                    else:
                        child_id = parent_ou_id
                        
        except Exception as e:
            self.logger.error(f"Error getting OU ID with path for account {account_id}: {e}")
        return "", ""

    # ¦ _get_ou_name
    def _get_ou_name(self, ou_id):
        if ou_id in self.ou_name_cache:
            return self.ou_name_cache[ou_id]

        try:
            response = self.organizations_client.describe_organizational_unit(OrganizationalUnitId=ou_id)
            ou_name = response['OrganizationalUnit'].get('Name', "")
            self.ou_name_cache[ou_id] = ou_name
            return ou_name
        except self.organizations_client.exceptions.OrganizationalUnitNotFoundException:
            self.logger.error(f"Organizational unit not found: {ou_id}")
        except self.organizations_client.exceptions.AWSOrganizationsNotInUseException:
            self.logger.error("AWS Organizations is not in use in this account.")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred while describing organizational unit {ou_id}: {e}")
        return ""

    # ¦ _get_ou_name_with_path
    def _get_ou_name_with_path(self, account_id):
        try:
            ou_name_path = []
            child_id = account_id
            while True:
                parents = self.organizations_client.list_parents(ChildId=child_id)
                parent = parents['Parents'][0]
                parent_ou_id = parent['Id']
                
                if parent_ou_id in self.ou_name_with_path_cache:
                    entry = self.ou_name_with_path_cache[parent_ou_id]
                    return entry.get('ou_name'), entry.get('ou_name_path_str')
                else:
                    parent_type = parent['Type']
                    parent_ou_name = "Root" if parent_type == 'ROOT' else self._get_ou_name(parent_ou_id)

                    if child_id == account_id:
                        ou_name = parent_ou_name

                    ou_name_path.append(parent_ou_name)

                    if parent_type == 'ROOT':
                        ou_name_path_str = "/".join(reversed(ou_name_path))
                        self.ou_name_with_path_cache[parent_ou_id] = (ou_name, ou_name_path_str)
                        return ou_name, ou_name_path_str
                    else:
                        child_id = parent_ou_id
                        
        except Exception as e:
            self.logger.error(f"Error getting OU name with path for account {account_id}: {e}")
        return "", ""

    # ¦ _describe_account
    def _describe_account(self, account_id):
        try:
            response = self.organizations_client.describe_account(AccountId=account_id)
            return response
        except self.organizations_client.exceptions.AccountNotFoundException:
            self.logger.error(f"Account not found: {account_id}")
        except self.organizations_client.exceptions.AWSOrganizationsNotInUseException:
            self.logger.error("AWS Organizations is not in use in this account.")
        except Exception as e:
            self.logger.error(f"Unexpected error occurred while describing account {account_id}: {e}")
        return {}

    # ¦ _get_tags
    def _get_tags(self, resource_id):
        if resource_id in self.ou_tags_cache:
            return self.ou_tags_cache[resource_id]

        tags = {}
        paginator = self.organizations_client.get_paginator('list_tags_for_resource')
        try:
            for page in paginator.paginate(ResourceId=resource_id):
                for entry in page.get('Tags', []):
                    tags[entry['Key']] = entry['Value']
            self.ou_tags_cache[resource_id] = tags
        except Exception as e:
            self.logger.error(f"Error getting tags for resource {resource_id}: {e}")
        return tags

    def _assume_remote_role(self, remote_role_arn):
        try:
            sts_client = boto3.client('sts')
            response = sts_client.assume_role(
                RoleArn=remote_role_arn,
                RoleSessionName='RemoteSession'
            )

            session = boto3.Session(
                aws_access_key_id=response['Credentials']['AccessKeyId'],
                aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                aws_session_token=response['Credentials']['SessionToken']
            )
            return session
        except Exception as e:
            self.logger.exception(f"Was not able to assume role {remote_role_arn}: {e}")
            return None
