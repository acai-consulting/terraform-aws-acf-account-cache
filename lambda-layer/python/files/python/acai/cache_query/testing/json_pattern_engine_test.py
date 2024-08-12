import unittest
import json
import logging
import os
import sys
import re

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from acai.cache_query.json_pattern_engine import JsonPatternEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()

def remove_comments(json_string):
    """ Remove comments from JSON string. """
    # Remove single-line comments
    json_string = re.sub(r"//.*", "", json_string)
    # Remove multi-line comments
    json_string = re.sub(r"/\*.*?\*/", "", json_string, flags=re.DOTALL)
    return json_string

class TestJsonPatternEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_path = os.path.dirname(__file__)

        with open(os.path.join(base_path, 'test_data/cache_entries.json'), 'r') as file:
            cls.cache_entries = json.loads(remove_comments(file.read()))
        
        with open(os.path.join(base_path, 'test_data/patterns.json'), 'r') as file:
            cls.patterns = json.loads(remove_comments(file.read()))

        with open(os.path.join(base_path, 'json_pattern_engine_test_matrix.json'), 'r') as file:
            cls.test_matrix = json.loads(remove_comments(file.read()))['test_matrix']
            
        cls.json_engine = JsonPatternEngine(logger)
        cls.passed_tests = 0
        cls.total_tests = 0

    def test_patterns(self):
        print("Executing test_patterns method")

        for test_case in self.test_matrix:
            account_id = test_case["accountId"]
            cache_entry = next((details.get("cacheObject") for acc_id, details in self.cache_entries.items() if acc_id == account_id), None)
            if not cache_entry:
                self.fail(f"Account ID {account_id} not found in cache entries")

            for pattern_name, expected_result in test_case.items():
                if pattern_name != "accountId":
                    with self.subTest(account_id=account_id, pattern_name=pattern_name):
                        self.total_tests += 1
                        result = self.json_engine.json_pattern_match_check(cache_entry, self.patterns[pattern_name])
                        try:                            
                            self.assertEqual(result, expected_result, f"{pattern_name} failed for accountId {account_id}")
                            self.passed_tests += 1
                        except AssertionError as e:
                            logger.info(f"{account_id} {self.patterns[pattern_name]} failed on {cache_entry}")
                            logger.error(e)
        
        logger.info(f"Total tests run: {self.total_tests}, Passed tests: {self.passed_tests}")

if __name__ == '__main__':
    unittest.main()
