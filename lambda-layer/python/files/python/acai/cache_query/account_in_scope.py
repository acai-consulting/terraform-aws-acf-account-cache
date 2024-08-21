from typing import List, Dict, Any, Union
from acai.cache_query.json_pattern_engine import JsonPatternEngine

"""
account_scope_policy = {
    "exclude": "*",
    "forceInclude": {account_context_query}
}

account_scope_policy = {
    "exclude": {account_context_query},
    "forceInclude": {account_context_query}
}

account_scope_policy = {
    "exclude": [{account_context_query_A} AND {account_context_query_A}],
    "forceInclude": [{account_context_query_C} AND {account_context_query_D}]
}

# Logical AND connection of the accounts matching to either the 1st or the 2nd account_scope_policy
account_scope_policy = [
    {
        "exclude": "*",
        "forceInclude": {account_context_query}
    },
    {
        "exclude": "*",
        "forceInclude": {account_context_query}
    }    
]
"""

class AccountInScope:
    def __init__(self, logger):
        self.logger = logger
        self.json_engine = JsonPatternEngine(logger)

    def account_in_scope(self, account_context, account_scope_policy):
        account_context_lowered = self._dict_lower_all_keys(account_context)
        account_scope_policy_lowered = self._dict_lower_all_keys(account_scope_policy)
        """
        TODO check if 1st keys are sufficient
        account_context_lowered = dict((x.lower(), y) for x,y in account_context.items())
        account_scope_policy_lowered = dict((x.lower(), y) for x,y in account_scope_policy.items())
        """
        
        self.logger.debug(f'type(account_scope_policy_lowered) {type(account_scope_policy_lowered)}')
        if type(account_scope_policy_lowered) == dict:
            return self._account_in_scope_internal(account_context_lowered, account_scope_policy_lowered)
            
        elif type(account_scope_policy_lowered) == list:
            object_in_scope = False
            for scope_object_dict in account_scope_policy_lowered:
                if type(scope_object_dict) == dict:
                    if self._account_in_scope_internal(account_context_lowered, scope_object_dict):
                        self.logger.debug(f'Matched {scope_object_dict} on {account_context_lowered}')
                        return True
                    else:
                        self.logger.debug(f'Did not match {scope_object_dict} on {account_context_lowered}')
                        
                else:
                    raise Exception("Account-Scope List-Element was not a valid scope-object")
            return object_in_scope
            
        else:
            raise Exception("AccountScope was not a valid scope-object")


    # ¦ __check_context_to_inner_policy_scope
    def _account_in_scope_internal(self, account_context_lowered, account_scope_policy_lowered):
        # First assume the object is in scope
        account_in_scope = True
        if 'exclude' in account_scope_policy_lowered:        
            exclude_query = account_scope_policy_lowered['exclude']
            # check for "exclude": "*"
            if isinstance(exclude_query, str) and exclude_query == "*":
                account_in_scope = False                
            else:
                account_in_scope = not self._matches_query(account_context_lowered, exclude_query)

        if not account_in_scope and 'forceinclude' in account_scope_policy_lowered:
            force_include_query = account_scope_policy_lowered['forceinclude']
            account_in_scope = self._matches_query(account_context_lowered, force_include_query)

        return account_in_scope

    # ¦ _matches_query
    def _matches_query(self, account_context_lowered: Dict[str, Any], query: Union[Dict[str, Any], List[Dict[str, Any]], str]) -> bool:
        if isinstance(query, dict):
            return self.json_engine.json_pattern_match_check(account_context_lowered, query)
        if isinstance(query, list):
            return any(self.json_engine.json_pattern_match_check(account_context_lowered, pat) for pat in query)
        return False

    def _dict_lower_all_keys(self, in_dict):
        """
        Description:
        The dict_lower_all_keys function is a recursive utility designed to convert all dictionary keys in the input dictionary (in_dict) to lowercase. 
        If the input dictionary contains nested dictionaries or lists with dictionaries, it will process them as well to ensure all dictionary keys at all nested levels are transformed to lowercase. 
        For any other data types encountered within the dictionary, they are returned as-is without modification.

        Parameters:
        in_dict: A dictionary that can contain other nested dictionaries, lists, or other data types.

        Returns:
        A new dictionary with all keys converted to lowercase. If nested dictionaries or lists with dictionaries are encountered, they are transformed recursively.
        Behavior:
        """
        if isinstance(in_dict, dict):
            return {key.lower(): self._dict_lower_all_keys(item) for key, item in in_dict.items()}
        elif isinstance(in_dict, list):
            return [self._dict_lower_all_keys(obj) for obj in in_dict]
        else:
            return in_dict
