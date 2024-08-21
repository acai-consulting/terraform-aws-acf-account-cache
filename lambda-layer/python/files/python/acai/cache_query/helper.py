from typing import Dict, List, Any

def is_valid_json_key_any(json_object: Dict[str, Any], allowed_keys: List[str]) -> bool:
    """
    Check if the JSON object contains only allowed_keys as keys (case insensitive).
    
    :param json_object: The JSON object to validate.
    :param allowed_keys: The list of allowed keys.
    :return: True if all keys in the JSON object are allowed, False otherwise.
    """
    json_keys_lower = {key.lower() for key in json_object.keys()}
    allowed_keys_lower = {key.lower() for key in allowed_keys}
    return json_keys_lower.issubset(allowed_keys_lower)

def is_valid_json_key_only(json_object: Dict[str, Any], allowed_keys: List[str]) -> bool:
    """
    Check if the JSON object contains any of the allowed_keys and nothing else (case insensitive).
    
    :param json_object: The JSON object to validate.
    :param allowed_keys: The list of allowed keys.
    :return: True if the JSON object contains only allowed keys and nothing else, False otherwise.
    """
    json_keys_lower = {key.lower() for key in json_object.keys()}
    allowed_keys_lower = {key.lower() for key in allowed_keys}
    return json_keys_lower.issubset(allowed_keys_lower) and bool(json_keys_lower)

def str_to_bool(s: str) -> bool:
    """
    Convert a string representation of truth to boolean.
    
    :param s: The string to convert.
    :return: True if the string represents a truth value, False otherwise.
    """
    return s.lower() in ['true', '1', 't', 'y', 'yes']

def contains_key(json_object: Dict[str, Any], key: str) -> bool:
    """
    Check if a key exists in the JSON object (case insensitive).
    
    :param json_object: The JSON object to check.
    :param key: The key to search for.
    :return: True if the key exists in the JSON object, False otherwise.
    """
    return key.lower() in {k.lower() for k in json_object.keys()}

def get_value(json_object: Dict[str, Any], key: str) -> Any:
    """
    Get the value associated with a key in the JSON object (case insensitive).
    
    :param json_object: The JSON object to search.
    :param key: The key whose value is to be retrieved.
    :return: The value associated with the key if it exists, an empty dictionary otherwise.
    """
    for k, v in json_object.items():
        if k.lower() == key.lower():
            return v
    return {}
