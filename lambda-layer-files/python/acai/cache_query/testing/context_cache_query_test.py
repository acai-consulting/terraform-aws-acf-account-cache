import unittest
import json
import logging
import os
import sys
import re

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from acai.cache_query.context_cache_query import ContextCacheQuery

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()

class ContextCacheMock:
    def __init__(self):
        base_path = os.path.dirname(__file__)
        with open(os.path.join(base_path, 'test_data/cache_entries.json'), 'r') as file:
            self.local_cache = json.loads(remove_comments(file.read()))

    def get_all_account_contexts(self):
        return self.local_cache

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
        context_cache = ContextCacheMock()

        base_path = os.path.dirname(__file__)

        with open(os.path.join(base_path, 'test_data/queries.json'), 'r') as file:
            cls.queries = json.loads(remove_comments(file.read()))

        with open(os.path.join(base_path, 'context_cache_query_test_matrix.json'), 'r') as file:
            cls.test_matrix = json.loads(remove_comments(file.read()))['test_matrix']
            
        cls.json_engine = ContextCacheQuery(logger, context_cache)
        cls.passed_tests = 0
        cls.total_tests = 0

    def test_queried(self):
        print("Executing test_queried method")

        for test_case in self.test_matrix:
            query_name = test_case["query"]
            expected_account_ids = set(test_case["account_ids"])

            query_pattern = self.queries.get(query_name)
            if not query_pattern:
                self.fail(f"Query {query_name} not found in queries.json")

            result = self.json_engine.query_cache(query_pattern)
            result_account_ids =  set(result.get('account_ids',[]))

            with self.subTest(query=query_name):
                self.total_tests += 1
                try:
                    self.assertEqual(result_account_ids, expected_account_ids, f"{query_name} failed")
                    self.passed_tests += 1
                except AssertionError as e:
                    logger.error(e)
        
        logger.info(f"Total tests run: {self.total_tests}, Passed tests: {self.passed_tests}")

if __name__ == '__main__':
    unittest.main()
