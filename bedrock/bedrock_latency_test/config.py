import os
ACCESS_KEY = os.environ.get('ak')
SECRET_KEY = os.environ.get('sk')
REGION = os.environ.get('region')

model_id = 'cohere.embed-multilingual-v3'
HOST = f'bedrock-runtime.{REGION}.amazonaws.com'

# replace the url below with the sagemaker endpoint you are load testing
SAGEMAKER_ENDPOINT_URL = f"https://bedrock-runtime.{REGION}.amazonaws.com/model/{model_id}/invoke"
# ACCESS_KEY = '<USE YOUR AWS ACCESS KEY HERE>'
# SECRET_KEY = '<USE YOUR AWS SECRET KEY HERE>'
# replace the context type below as per your requirements
# CONTENT_TYPE = 'text/csv'
CONTENT_TYPE = 'application/json'
METHOD = 'POST'
SERVICE = 'bedrock'
SIGNED_HEADERS = 'content-type;host;x-amz-date'
CANONICAL_QUERY_STRING = ''
ALGORITHM = 'AWS4-HMAC-SHA256'