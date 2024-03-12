import os
ACCESS_KEY = os.environ.get('ak')
SECRET_KEY = os.environ.get('sk')
REGION = os.environ.get('region')

model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
HOST = f'bedrock-runtime.{REGION}.amazonaws.com'

# replace the url below with the sagemaker endpoint you are load testing
ENDPOINT_URL = f"https://bedrock-runtime.{REGION}.amazonaws.com/model/{model_id}/invoke"
CONTENT_TYPE = 'application/json'
METHOD = 'POST'
SERVICE = 'bedrock'
SIGNED_HEADERS = 'content-type;host;x-amz-date'
CANONICAL_QUERY_STRING = ''
ALGORITHM = 'AWS4-HMAC-SHA256'