from typing import List, Dict, Any, Union
from acai.cache_query.json_pattern_engine import JsonPatternEngine
from acai.cache_query.validate_query import ValidateQuery
from acai.cache_query.account_in_scope import AccountInScope

class ContextCacheQuery:
    def __init__(self, logger, context_cache):
        self.logger = logger
        self.context_cache = context_cache
        self.json_engine = JsonPatternEngine(logger)
        self.validation = ValidateQuery(logger)
        self.account_in_scope = AccountInScope(logger)

    def get_context_cache(self):
        return self.context_cache
    
    """
    query can be a query-dict or a list of query-dict 

    query-dict = {
        "exclude": "*",
        "forceInclude": {account_context_query}
    }
    
    query-dict = {
        "exclude": [{account_context_query} and {account_context_query}],
        "forceInclude": [{account_context_query}]
    }
    """    
    # ¦ query_cache
    def query_cache(self, query: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        if query != "*":
            validation = self.validation.validate_query(query)
            validation_errors = validation.get("validation_errors", [])
            self.logger.info(f"Validation: {validation}")

            if validation_errors:
                raise ValueError(validation)

        result = {
            'account_context_list': [],
            'account_ids': [],
            'info': ''
        }

        try:
            cache_items = self.context_cache.get_all_account_contexts()
        except Exception as e:
            self.logger.error(f"Failed to retrieve account contexts: {str(e)}")
            return result  # Return an empty result or handle differently based on requirements.
        
        counter = 0
        for account_id, details in cache_items.items():
            account_context = details.get("cacheObject", {})
            if query == "*" or self.account_in_scope.account_in_scope(account_context, query):
                self.logger.debug(f'In Scope account: {account_context}')
                result['account_context_list'].append(account_context)
                result['account_ids'].append(account_id)
                counter += 1
            else:
                self.logger.debug(f'Not in Scope account: {account_context}')

        result['info'] = f"Selected {counter} of {len(cache_items)} cache-items."
        return result

