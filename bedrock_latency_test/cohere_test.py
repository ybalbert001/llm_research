from locust import HttpUser, task
from authorizer import authorize
import json
import config as conf

text= 'CT核磁是否需要预授权？'
input_body = {}
input_body["texts"] = [ text[:2048] ]
input_body["input_type"] = 'search_query'
# input_body["truncate"] = 'RIGHT'
PAYLOAD = json.dumps(input_body)

class WebsiteUser(HttpUser):
    min_wait = 1
    max_wait = 5  # time in ms

    @task
    def test_post(self):
        """
        Load Test SageMaker Endpoint (POST request)
        """
        headers = authorize(PAYLOAD)
        response = self.client.post(conf.SAGEMAKER_ENDPOINT_URL, data=PAYLOAD, headers=headers, name='Post Request')