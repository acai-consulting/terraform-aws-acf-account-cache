from typing import List, Dict, Any, Union
import logging
import acai.cache_query.helper as helper

class ValidateQuery:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def validate_queries(self, query: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        validation_results: List[Dict[str, Any]] = []
        queries = query if isinstance(query, list) else [query]
        for item in queries:
            validation_result = self.validate_query(item)
            if validation_result.get("validation_errors"):
                validation_results.append(validation_result)
        return validation_results

    def validate_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        validation_errors, validation_hints = self._validate(query)
        return {"query": query, "validation_errors": validation_errors, "validation_hints": validation_hints}

    def _validate(self, query: Dict[str, Any]) -> List[str]:
        
        def evaluate_query(validation_errors: List[str], validation_hints: List[str], prefix: str, query: Dict[str, Any]) -> None:
            valid_keys = ['accountId', 'accountName', 'accountTags', 'ouId', 'ouIdWithPath', 'ouName', 'ouNameWithPath', 'ouTags']
            if not helper.is_valid_json_key_only(query, valid_keys):
                validation_errors.append(
                    f'Section "{prefix}": An account-context may only contain the keys "accountId", "accountName", "accountTags", "ouId", '
                    '"ouIdWithPath", "ouName", "ouNameWithPath", "ouTags". Please be aware, that the elements are treated with a logical AND.'
                )

        def evaluate_exclude(validation_errors: List[str], validation_hints: List[str], exclude_json: Any) -> None:
            if exclude_json == ['*']:
                validation_hints.append(
                    '{"exclude": ["*"]} can be written as {"exclude": "*"}.'
                )
            elif isinstance(exclude_json, list):
                for account_scope_element in exclude_json:
                    if isinstance(account_scope_element, dict):
                        evaluate_query(validation_errors, validation_hints, "exclude", account_scope_element)
            elif isinstance(exclude_json, dict):
                evaluate_query(validation_errors, validation_hints, "exclude", exclude_json)
            elif exclude_json != '*':
                validation_errors.append(
                    'The "exclude"-value may only be "*" for excluding all accounts, a single account-context '
                    'or a list of account-contexts that will be evaluated with a logical OR.'
                )

        def evaluate_force_include(validation_errors: List[str], validation_hints: List[str], force_include_json: Any) -> None:
            if isinstance(force_include_json, list):
                for account_scope_element in force_include_json:
                    if isinstance(account_scope_element, dict):
                        evaluate_query(validation_errors, validation_hints, "forceInclude", account_scope_element)
            elif isinstance(force_include_json, dict):
                evaluate_query(validation_errors, validation_hints, "forceInclude", force_include_json)
            else:
                validation_errors.append(
                    'The "forceInclude"-value may only be a single account-context or a list of account-context that will be evaluated with a logical OR.'
                )

        validation_errors = []
        validation_hints = []
        if query != "*":
            if 'exclude' not in query:
                validation_errors.append(
                    'The cache query section must contain an "exclude"-section.'
                )

            if helper.get_value(query, 'forceInclude') in ['*', ['*']]:
                validation_hints.append(
                    '"forceInclude": "*" or "forceInclude": ["*"] is not required, as by default all entities are in scope.'
                )

            if helper.contains_key(query, 'forceInclude') and not helper.contains_key(query, 'exclude'):
                validation_errors.append(
                    'By default all AWS accounts are in scope. A Cache-Query the wants to forceInclude AWS accounts, first must exclude AWS accounts.'
                )

            if helper.contains_key(query, 'exclude'):
                evaluate_exclude(validation_errors, validation_hints, helper.get_value(query, 'exclude'))

            if helper.contains_key(query, 'forceInclude'):
                evaluate_force_include(validation_errors, validation_hints, helper.get_value(query, 'forceInclude'))

        return validation_errors, validation_hints
