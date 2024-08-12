import json
import re
import logging
from typing import Dict, List, Any, Union

"""
source_json = {
    "accountId": "654654551430",
    "accountName": "aws-testbed-core-backup",
    "accountTags": {
        "owner": "Foundation Security Backup Team"
    },
    "ouId": "ou-s2bx-wq9eltfy",
    "ouIdWithPath": "o-5l2vzue7ku/r-s2bx/ou-s2bx-1rsmt2o1/ou-s2bx-wq9eltfy",
    "ouName": "Security",
    "ouNameWithPath": "Root/Core/Security",
    "ouTags": {
        "owner": "Foundation Security"
    }
}

pattern_json = {
    "accountName": [
        {
            "contains": "bu1-"
        }
    ]
}
"""
class JsonPatternEngine:
    def __init__(self, logger: logging.Logger):
        self.version = "1.0"
        self.logger = logger
        logger.info(f"JsonPatternEngine v{self.version}")

    # ¦ json_pattern_match_check
    def json_pattern_match_check(self, source_json: Dict[str, Any], pattern_json: Dict[str, Any]) -> bool:
        if not pattern_json:
            return False
        source_dict_lowered_keys = self._lower_keys(source_json)
        pattern_dict_lowered_keys = self._lower_keys(pattern_json)

        return self._check_pattern_to_source_match(
            source=source_dict_lowered_keys,
            pattern=pattern_dict_lowered_keys
        )

    # ¦ _check_pattern_to_source_match
    def _check_pattern_to_source_match(self, source: Dict[str, Any], pattern: Dict[str, Any]) -> bool:
        self.logger.debug(f"_check_pattern_to_source_match> source: {json.dumps(source)}")
        self.logger.debug(f"_check_pattern_to_source_match> pattern: {json.dumps(pattern)}")

        if not isinstance(source, Dict):
            return False

        # go through all items of the current pattern-level
        for pattern_key_lowered, pattern_value in pattern.items():
            self.logger.debug(f"_check_pattern_to_source_match> pattern_key: {pattern_key_lowered} pattern_value: {pattern_value}")
            
            if pattern_key_lowered in source:
                source_value = source[pattern_key_lowered]
                self.logger.debug(f"_check_pattern_to_source_match> source_key: {pattern_key_lowered} source_value: {source_value}")

                # Check for 'accountTags' and 'ouTags'
                if pattern_key_lowered in {'accounttags', 'outags'}:
                    if not self._check_pattern_to_source_match(source_value, pattern_value):
                        return False

                elif isinstance(source_value, str):
                    if not self._process_pattern_value(source_value, pattern_value):
                        return False
                else:
                    self.logger.debug(f"_check_pattern_to_source_match> source_value is not a string, returning False")
                    return False
            else:
                if isinstance(pattern_value, list):
                    for pattern_item in pattern_value:
                        if isinstance(pattern_item, dict):
                            for logic_key, logic_value in pattern_item.items():
                                if logic_key == "exists":
                                    if logic_value == False:
                                        return True

                self.logger.debug(f"_check_pattern_to_source_match> pattern_key {pattern_key_lowered} not found in source")
                return False

        return True

    # ¦ _process_pattern_value
    def _process_pattern_value(self, source_value: str, pattern_value: Any) -> bool:
        if isinstance(pattern_value, str):
            return pattern_value == source_value
        elif isinstance(pattern_value, list):
            return self._process_pattern_list(source_value, pattern_value)
        return False

    # ¦ _process_pattern_list
    def _process_pattern_list(self, source_value: str, pattern_list: List[Any]) -> bool:
        self.logger.debug(f"_process_pattern_list> {source_value=}, {pattern_list=}")
        for pattern_item in pattern_list:
            if isinstance(pattern_item, str):
                if pattern_item == source_value:
                    self.logger.debug(f"Match found: {pattern_item} == {source_value}")
                    return True
            elif isinstance(pattern_item, dict):
                if self._process_logic(source_value, pattern_item):
                    return True
            else:
                raise ValueError(f"Unknown pattern element type: {type(pattern_item).__name__}")
        self.logger.debug("No match found in pattern list")
        return False

    # ¦ _process_logic
    def _process_logic(self, source_value: str, pattern_item: Dict[str, Any]) -> bool:
        for logic_key, logic_value in pattern_item.items():
            self.logger.debug(f"_process_logic> Logic-Check: {logic_key=} {logic_value=} {source_value=}")
            if logic_key == "prefix":
                if source_value.startswith(logic_value):
                    return True
            elif logic_key == "contains":
                if logic_value in source_value:
                    return True
            elif logic_key == "suffix":
                if source_value.endswith(logic_value):
                    return True
            elif logic_key == "exists":
                if logic_value:
                    return True
            elif logic_key == "regex-match":
                if re.match(logic_value, source_value):
                    return True
            elif logic_key == "anything-but":
                if logic_value != source_value:
                    return True
            elif logic_key == "regex-not-match":
                if not re.match(logic_value, source_value):
                    return True
            elif logic_key == "contains-not":
                if logic_value not in source_value:
                    return True
            else:
                raise ValueError(f"Unknown logic condition: {logic_key}")
        return False


    # ¦ _lower_keys
    def _lower_keys(self, source_dict: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        if not isinstance(source_dict, dict):
            raise ValueError(f"Expected a dictionary, but got {type(source_dict).__name__}")
        
        new_dict = {}
        for key, value in source_dict.items():
            if isinstance(value, dict):
                new_dict[key.lower()] = self._lower_keys(value)
            elif isinstance(value, list):
                new_dict[key.lower()] = [
                    self._lower_keys(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                new_dict[key.lower()] = value
        
        return new_dict
