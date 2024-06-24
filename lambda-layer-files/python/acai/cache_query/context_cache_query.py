from typing import List, Dict, Any, Union
import logging
from acai.cache_query.json_pattern_engine import JsonPatternEngine
from acai.cache_query.validate_query import ValidateQuery

class ContextCacheQuery:
    def __init__(self, logger: logging.Logger, context_cache):
        self.logger = logger
        self.context_cache = context_cache
        self.json_engine = JsonPatternEngine(logger)
        self.validation = ValidateQuery(logger)

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
        self.logger.debug(f'type(query): {type(query)}')

        validation = self.validation.validate_query(query)
        validation_errors = validation.get("validation_errors", [])

        if len(validation_errors) > 0:
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
            if query == "*" or self._account_in_scope(account_context, query):
                self.logger.debug(f'In Scope account: {account_context}')
                result['account_context_list'].append(account_context)
                result['account_ids'].append(account_id)
                counter += 1
            else:
                self.logger.debug(f'Not in Scope account: {account_context}')

        result['info'] = f"Selected {counter} of {len(cache_items)} cache-items."
        return result


    # ¦ _account_in_scope
    def _account_in_scope(self, account: Dict[str, Any], query: Union[Dict[str, Any], List[Dict[str, Any]]]) -> bool:
        queries = query if isinstance(query, list) else [query]
        return any(self._account_in_scope_inner(account, q) for q in queries)

    # ¦ _account_in_scope_inner
    def _account_in_scope_inner(self, account: Dict[str, Any], query: Dict[str, Any]) -> bool:
        query_lowered_keys = {k.lower(): v for k, v in query.items()}

        account_in_scope = True

        if 'exclude' in query_lowered_keys:
            exclude_query = query_lowered_keys['exclude']
            if isinstance(exclude_query, str) and exclude_query == "*":
                account_in_scope = False
            else:
                account_in_scope = not self._matches_query(account, exclude_query)

        if not account_in_scope and 'forceinclude' in query_lowered_keys:
            force_include_query = query_lowered_keys['forceinclude']
            account_in_scope = self._matches_query(account, force_include_query)

        return account_in_scope

    # ¦ _matches_query
    def _matches_query(self, account: Dict[str, Any], query: Union[Dict[str, Any], List[Dict[str, Any]], str]) -> bool:
        if isinstance(query, dict):
            return self.json_engine.json_pattern_match_check(account, query)
        if isinstance(query, list):
            return any(self.json_engine.json_pattern_match_check(account, pat) for pat in query)
        return False
