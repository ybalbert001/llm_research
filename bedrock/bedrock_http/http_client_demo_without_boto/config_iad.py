from urllib.parse import quote

REGION = 'us-east-1'
# REGION = 'eu-central-1'
# REGION = 'us-west-2'

HOST = f'bedrock-runtime.{REGION}.amazonaws.com'
# ORI_MODEL_ID = 'anthropic.claude-v2'

# ORI_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'
ORI_MODEL_ID = 'anthropic.claude-3-haiku-20240307-v1:0'

MODEL_ID = quote(ORI_MODEL_ID, safe='')

# /model/modelId/invoke
BEDROCK_ENDPOINT_URL = f'https://{HOST}/model/{MODEL_ID}/invoke'
BEDROCK_ENDPOINT_STREAM_URL = f'https://{HOST}/model/{MODEL_ID}/invoke-with-response-stream'

ACCESS_KEY = ''
SECRET_KEY = ''

CONTENT_TYPE = 'application/json'
METHOD = 'POST'
SERVICE = 'bedrock'
SIGNED_HEADERS = 'host;x-amz-date'
CANONICAL_QUERY_STRING = ''
ALGORITHM = 'AWS4-HMAC-SHA256'
