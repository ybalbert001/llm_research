# -*- coding: utf-8 -*-
from authorizer import authorize, get_payload_hash
import config_iad as conf
import json


PAYLOAD_0 =  json.dumps({
    "system": '',
    "messages": [{"role": "user", "content": [{"type": "text", "text": """don't use any tool and write a 800 words text about yellow river."""}]}],
    "anthropic_version":"bedrock-2023-05-31",
    "max_tokens": 120,
    "stop_sequences": ["\n\nHuman:", "\n\nAssistant"],
    "top_p": 0.999,
    "temperature": 1,
})


payload_hash = get_payload_hash(PAYLOAD_0)

def local_test():
    import http.client
    conn = http.client.HTTPSConnection(conf.HOST)
    headers = authorize(PAYLOAD_0, payload_hash)
    # print(headers)

    # conn.request('POST', '/model/anthropic.claude-v2/invoke', PAYLOAD, headers)
    conn.request('POST', f'/model/{conf.MODEL_ID}/invoke', PAYLOAD_0, headers)

    response = conn.getresponse()
    resp_body = json.loads(response.read().decode())
    # print(resp_body)
    print(resp_body['content'][0]['text'])
    # usage = resp_body['usage']
    # print(usage)

def local_test_stream():

    import http.client
    conn = http.client.HTTPSConnection(conf.HOST)
    headers = authorize(PAYLOAD_0, payload_hash, True)
    # print(headers)

    conn.request('POST', f'/model/{conf.MODEL_ID}/invoke-with-response-stream', PAYLOAD_0, headers)

    response = conn.getresponse()
    resp = response.read()
    print(resp)

if __name__ == '__main__':
    import logging

    logger = logging.getLogger('my-authorizer')
    logger.setLevel(logging.WARNING)
    # logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)
    # 添加处理器到记录器
    logger.addHandler(console_handler)

    local_test_stream()
    print('**' * 10)
    local_test()