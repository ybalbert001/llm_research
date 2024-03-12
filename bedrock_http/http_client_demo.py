import requests
import base64
import json
import os
from authorizer import authorize
import config as conf

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

os.system('wget https://cats.com/wp-content/uploads/2020/10/tabby-maine-coon-768x384.jpg')
image_path='tabby-maine-coon-768x384.jpg'
base64_image = encode_image(image_path)
input_body = {
    "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
    "contentType": "application/json",
    "accept": "application/json",
    "body": {
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
                        "text": f"What’s in this image?"
                    }
                ]
            }
        ]
    }
}

PAYLOAD = json.dumps(input_body)

headers = authorize(PAYLOAD)

print(headers)
r = requests.post(conf.ENDPOINT_URL, json=PAYLOAD, headers=headers)

print(r.text)