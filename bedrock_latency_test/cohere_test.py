from locust import HttpUser, task
import json
import boto3
import os

text= 'CT核磁是否需要预授权？'
input_body = {}
input_body["texts"] = [ text[:2048] ]
input_body["input_type"] = 'search_query'
# input_body["truncate"] = 'RIGHT'
body = json.dumps(input_body)
content_type = "application/json"
accepts = "application/json"
model_id = 'cohere.embed-multilingual-v3'
ak = os.environ.get('ak')
sk = os.environ.get('sk')
region = os.environ.get('region')

class WebsiteUser(HttpUser):
    min_wait = 1
    max_wait = 5  # time in ms
    self.client = boto3.client(service_name='bedrock-runtime', region_name=region)

    @task
    def test_post(self):
        response = self.client.invoke_model(
            body=body,
            modelId=model_id,
            accept=accepts,
            contentType=content_type,
        )
        response_body = json.loads(response.get("body").read())
        embeddings = response_body.get("embeddings")