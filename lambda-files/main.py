import sourcedefender
import evaluate
from semper.python_helper import logger as helper_logger
import os
import logging
LOGLEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.getLogger().setLevel(LOGLEVEL)
LOGGER = logging.getLogger()
CONTEXT_LOGGER = helper_logger.CustomLogger(level=os.environ.get('LOG_LEVEL', 'INFO').upper())
CONTEXT_LOGGER_CACHE = helper_logger.CustomLogger(level=os.environ.get('CACHE_LOG_LEVEL', 'ERROR').upper())

import os
from datetime import datetime

"""
This lambda has two purposes:
1. Evaluate JSON-Pattern against JSON-Source
For this use-case, the event-JSON must not contain {"accountScope":...}

2. Evaluate Account-Scope-JSON against Context-Cache
For this use-case, the event-JSON must contain {"accountScope":...}
Sample:
{
  "accountScope": {
    "exclude": {
        "accountTags": {
          "environment": "nonprod"
      }
    }
  }
}
"""
def lambda_handler(event, context):
    try:
        evaluator = evaluate.Evaluator(CONTEXT_LOGGER, CONTEXT_LOGGER_CACHE)
        if 'accountScope' in event:
            return evaluator.process_account_scope(event["accountScope"])
        else:
            return evaluator.process_source_pattern()
        
    except Exception as e:
        LOGGER.exception(f'Unexpected error: {e}')
        raise e

