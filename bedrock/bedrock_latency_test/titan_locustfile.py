from locust import HttpUser, task, constant, between
# from authorizer import authorize
import json
import config as conf

import botocore.auth
import botocore.awsrequest
import botocore.credentials
from botocore.session import Session
from urllib.parse import urlparse

text= 'CT核磁是否需要预授权？'
input_body = {}
input_body["inputText"] = text[:2048]
PAYLOAD = json.dumps(input_body)

def get_botocore_auth_headers(url, payload):
    """
    使用 botocore 生成授权头
    
    Args:
        url: API 端点 URL
        payload: 请求体
    
    Returns:
        包含授权信息的请求头字典
    """
    # 创建凭证
    session = Session()
    credentials = botocore.credentials.Credentials(
        access_key=conf.ACCESS_KEY,
        secret_key=conf.SECRET_KEY
    )
    
    # 解析 URL
    parsed_url = urlparse(url)
    
    # 创建请求对象
    request = botocore.awsrequest.AWSRequest(
        method=conf.METHOD,
        url=url,
        data=payload,
        headers={
            'Content-Type': conf.CONTENT_TYPE,
            'Host': parsed_url.netloc
        }
    )
    
    # 创建签名器并签名请求
    signer = botocore.auth.SigV4Auth(credentials, conf.SERVICE, conf.REGION)
    signer.add_auth(request)
    
    # 返回签名后的请求头
    return dict(request.headers)

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
        headers = get_botocore_auth_headers(conf.SAGEMAKER_ENDPOINT_URL, PAYLOAD)

        response = self.client.post(conf.SAGEMAKER_ENDPOINT_URL, data=PAYLOAD, headers=headers, name='Post Request')