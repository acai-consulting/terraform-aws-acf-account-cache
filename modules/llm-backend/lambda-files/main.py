import os
import logging
import uuid
import json
import re
import boto3
from botocore.config import Config
import time
from aws_lambda_powertools import Logger
from acai.cache_query.validate_query import ValidateQuery
from boto3.dynamodb.conditions import Key
from typing import Any, Dict, List, Union, Tuple

# Logging setup
def setup_logging() -> Logger:
    log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()
    logger = Logger(
        service="acai-account-cache",
        level=log_level,
    )

    # Set less verbose logging for noisy libraries
    for noisy_log_source in ["boto3", "botocore", "nose", "s3transfer", "urllib3"]:
        logging.getLogger(noisy_log_source).setLevel(logging.WARN)

    return logger

LOGGER: Logger = setup_logging()

# Environment Variables
BEDROCK_SERVICE_REGION = os.environ['BEDROCK_SERVICE_REGION']
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
BEDROCK_SERVICE_NAME = os.environ['BEDROCK_SERVICE_NAME']
CHAT_HISTORY_DDB_TABLE_NAME = os.environ['CHAT_HISTORY_DDB_TABLE_NAME']

# Bedrock client initialization
def get_bedrock_client() -> boto3.client:
    config = Config(
        read_timeout=1000,
        retries={
            'max_attempts': 10,              
            'mode': 'adaptive'               
        }        
    )
    return boto3.client(service_name=BEDROCK_SERVICE_NAME, region_name=BEDROCK_SERVICE_REGION, config=config)

BEDROCK_CLIENT: boto3.client = get_bedrock_client()

# DynamoDB client initialization
DDB_CLIENT = boto3.resource('dynamodb')
DDB_TABLE = DDB_CLIENT.Table(CHAT_HISTORY_DDB_TABLE_NAME)

def get_conversation_history(session_id: str) -> List[Dict[str, str]]:
    response = DDB_TABLE.query(
        KeyConditionExpression=Key('sessionID').eq(session_id)
    )
    return response.get('Items', [])

def store_conversation_history(session_id: str, history: List[Dict[str, str]]) -> None:
    with DDB_TABLE.batch_writer() as batch:
        for entry in history:
            item = {
                'sessionID': session_id,
                'timestamp': entry['timestamp'],
                'user': entry['user'],
                'assistant': entry['assistant'],
                'timeToExist': int(time.time()) + 7 * 24 * 60 * 60  # Current time + 1 week
            }
            batch.put_item(Item=item)

def generate_prompt(chat_query: str, context: str, previous_query: Union[str, Dict[str, Any]], validation_results: List[str], history: List[Dict[str, str]]) -> str:
    validation_messages = "\n".join(validation_results)

    conversation_history = "\n".join([f"Human: {entry['user']}\nAssistant: {entry['assistant']}" for entry in history])
    prompt_without_documentation = f"""Your task is creating a JSON query-policy for the ACAI account-context cache embedded in a ```json ..``` block.
Respond with a rich answer containing the JSON configuration policy in code format.
The human specified values should be exactly preserved including case sensitivity. Statements in quotes must exactly be preserved.

"""

    if conversation_history:
        prompt_without_documentation += f"""
Conversation history:
{conversation_history}

"""

    if validation_messages:
        prompt_without_documentation += f"""
For this suggested query:
<json>{previous_query}</json>
the following validation results apply: {validation_messages}

"""

    prompt_without_documentation += f"""
Human: {chat_query}
Assistant: """
    
    prompt = f"""Here are some documents for you to reference for your task in XML tag <documents>:
<documents>{context}</documents>
""" + prompt_without_documentation

    return prompt, prompt_without_documentation

def invoke_bedrock_model(chat_query: str, session_id: str) -> Tuple[str, Dict[str, Any]]:
    with open('wiki.md', 'r') as file:
        context_content = file.read()
    
    validator = ValidateQuery(LOGGER)
    previous_query: Union[str, Dict[str, Any]] = ""
    validation_results: List[str] = []
    query_json: Dict[str, Any] = {}

    conversation_history = get_conversation_history(session_id)

    for _ in range(3):
        prompt, prompt_without_documentation = generate_prompt(chat_query, context_content, previous_query, validation_results, conversation_history)
        LOGGER.info(f"Invoking model with prompt: {prompt_without_documentation}")
        response = BEDROCK_CLIENT.invoke_model(
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            }),
            modelId=BEDROCK_MODEL_ID,
            accept='application/json',
            contentType='application/json',
        )
        response_content = json.loads(response['body'].read().decode('utf-8'))
        LOGGER.debug(f"response_content={response_content}")

        code_blocks = re.findall(r'```json\n([\s\S]*?)```', response_content.get('content', [{}])[0].get('text', ''))
        try:
            LOGGER.debug(f"code_blocks={code_blocks}")
            if code_blocks:
                query_json = json.loads(code_blocks[0])
                validation = validator.validate_query(query_json)
                validation_results = validation.get("validation_errors", [])

                if len(validation_results) > 0:
                    LOGGER.info(f"Validation results: {validation_results}")
                else:
                    break
                previous_query = query_json
        except Exception as e:
            LOGGER.info(response_content.get('content', [{}])[0].get('text', ''))
            LOGGER.error(f"Unhandled exception: {e}", exc_info=True)

    conversation_history.append({
        'timestamp': int(time.time()),
        'user': chat_query,
        'assistant': response_content['content'][0]['text']
    })

    store_conversation_history(session_id, conversation_history)
    
    return response_content['content'][0]['text'], query_json

def handle_chat_query(event: Dict[str, Any]) -> Dict[str, Any]:
    session_id = event.get('session_id', str(uuid.uuid4()))
    chat_query = event.get('chat_query')
    if not chat_query or not session_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Please provide a JSON with the elements "chat_query" and "session_id"'})
        }
    
    response_text, query_json = invoke_bedrock_model(chat_query, session_id)
    return {
        'statusCode': 200,
        'body': json.dumps({
            'query': chat_query,
            'response': response_text,
            'query_json': query_json
        })
    }

@LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        return handle_chat_query(event)
    except Exception as e:
        LOGGER.error(f"Unhandled exception: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
