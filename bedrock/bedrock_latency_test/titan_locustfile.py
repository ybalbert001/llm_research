from locust import HttpUser, task, constant, between
from authorizer import authorize
import json
import config as conf

text= 'CT核磁是否需要预授权？'
input_body = {}
input_body["inputText"] = [ text[:2048] ]
PAYLOAD = json.dumps(input_body)

class WebsiteUser(HttpUser):
    # min_wait = 1
    # max_wait = 5  
    # wait_time = constant(3)
    wait_time = between(3, 5) # 3-5 ms wait time

    @task
    def test_post(self):
        """
        Load Test SageMaker Endpoint (POST request)
        """
        headers = authorize(PAYLOAD)
        response = self.client.post(conf.SAGEMAKER_ENDPOINT_URL, data=PAYLOAD, headers=headers, name='Post Request')