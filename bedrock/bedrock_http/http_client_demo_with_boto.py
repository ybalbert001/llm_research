import requests
import base64
import json
import os
import config as conf
from botocore.awsrequest import AWSRequest
import botocore.session

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

os.system('wget https://cats.com/wp-content/uploads/2020/10/tabby-maine-coon-768x384.jpg')
image_path='tabby-maine-coon-768x384.jpg'
base64_image = encode_image(image_path)
input_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64_image
                    }
                },
                {
                    "type": "text",
                    "text": f"What's in this image?"
                }
            ]
        }
    ]
}


PAYLOAD = json.dumps(input_body)

session = botocore.session.Session()
session.set_credentials(conf.ACCESS_KEY, conf.SECRET_KEY)
signer = botocore.auth.SigV4Auth(session.get_credentials(), 'bedrock', 'us-west-2')
headers = {'Content-Type': 'application/json'}

request = AWSRequest(method='POST', url=conf.ENDPOINT_URL, data=PAYLOAD, headers=headers)
signer.add_auth(request)
prepped = request.prepare()

r = requests.post(prepped.url, headers=prepped.headers, data=PAYLOAD)

print(r.url)
print(r.headers)
print(r.text)