import boto3
import random
import asyncio
import time
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from ratelimit import limits, RateLimitException, sleep_and_retry
import concurrent.futures

'''
Install these packages at first

pip3 install opensearch-py
pip3 install boto3
pip3 install requests_aws4auth
pip3 install ratelimit
'''

EMB_MODEL_ENDPOINT = "paraphrase-node10-g4dn-x-2023-07-15-03-04-33-415-endpoint"
AOS_ENDPOINT = "vpc-domain66ac69e0-kqxmakmg46s4-vp4czze4lwiccd2ge2au2pvlui.us-west-2.es.amazonaws.com"
AOS_INDEX = "chatbot-index"

def get_embedding(smr_client, text_arrs, endpoint_name=EMB_MODEL_ENDPOINT):
    parameters = {
      #"early_stopping": True,
      #"length_penalty": 2.0,
      "max_new_tokens": 50,
      "temperature": 0,
      "min_length": 10,
      "no_repeat_ngram_size": 2,
    }

    response_model = smr_client.invoke_endpoint(
                EndpointName=endpoint_name,
                Body=json.dumps(
                {
                    "inputs": text_arrs,
                    "parameters": parameters
                }
                ),
                ContentType="application/json",
            )
    
    json_str = response_model['Body'].read().decode('utf8')
    json_obj = json.loads(json_str)
    embeddings = json_obj["sentence_embeddings"]
    
    return embeddings

def search_using_aos_knn(client, q_embedding, index, size=1):

    #Note: 查询时无需指定排序方式，最临近的向量分数越高，做过归一化(0.0~1.0)
    query = {
        "size": size,
        "query": {
            "knn": {
                "embedding": {
                    "vector": q_embedding,
                    "k": size
                }
            }
        }
    }

    query_response = client.search(
        body=query,
        index=index
    )
    return query_response['took']

smr_client = boto3.client("sagemaker-runtime")
querys = ['RNA crystallization is complicated by inherent difficulties, such as vulnerability to degradation by RNases and susceptibility to misfolding', ' A major bottleneck in RNA crystallography is often the production of sufficient amounts of high-quality, homogeneously folded RNA', ' This review is meant to be used as a reference for the crystallization of large-structured RNAs such as', 'ribozymes and riboswitches. We will discuss the advantages and disadvantages of both traditional and native RNA purification methods. Furthermore, examples of crystallization strategies using both RNA-dependent and protein-driven modules will be discussed. Finally, strategies for phasing—including molecular replacement and general tools for heavy metal soaking to obtain anomalous', 'ribozymes and riboswitches', ' We will discuss the advantages and disadvantages of both traditional and native RNA purification methods', ' Furthermore, examples of crystallization strategies using both RNA-dependent and protein-driven modules will be discussed', ' Finally, strategies for phasing—including molecular replacement and general tools for heavy metal soaking to obtain anomalous', 'diffraction data—will be presented.', 'diffraction data—will be presented', '2. RNA Purification and Folding', ' RNA Purification and Folding', 'T7 RNA polymerase is commonly used to produce large quantities of RNA by in vitro transcription [1]. Despite the versatility of this common method, there are several important caveats to consider. T7 RNA polymerase is prone to non-templated additions of 1–3 nucleotides to the 3′ end of the RNA transcript. These non-templated additions can be circumvented by the incorporation of two', 'T7 RNA polymerase is commonly used to produce large quantities of RNA by in vitro transcription [1]', ' Despite the versatility of this common method, there are several important caveats to consider', ' T7 RNA polymerase is prone to non-templated additions of 1–3 nucleotides to the 3′ end of the RNA transcript', ' These non-templated additions can be circumvented by the incorporation of two', 'sequential 2′-O-methyl substitutions in the last two nucleotides of the 5′ end of the DNA template strand [2]. Template slippage is also known to occur with T7 RNA polymerase when it encounters polyA sequences during transcription [3]. This polymerase also requires the 5′ end of the RNA sequence to contain at least two sequential guanosine residues for efficient promoter firing', 'sequential 2′-O-methyl substitutions in the last two nucleotides of the 5′ end of the DNA template strand [2]', ' Template slippage is also known to occur with T7 RNA polymerase when it encounters polyA sequences during transcription [3]']
embeddings = get_embedding(smr_client, querys, EMB_MODEL_ENDPOINT)

credentials = boto3.Session().get_credentials()
region = boto3.Session().region_name
access_key = ''
secret_key = ''

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es')
aos_client = OpenSearch(
        hosts=[{'host': AOS_ENDPOINT, 'port': 443}],
        http_auth = awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

rand_max = len(querys)-1

@sleep_and_retry
@limits(calls=300, period=1)
def test_knn_search():
    rand_idx = random.randint(0, rand_max)
    opensearch_knn_respose = search_using_aos_knn(aos_client, embeddings[rand_idx], AOS_INDEX)
    return opensearch_knn_respose

with concurrent.futures.ThreadPoolExecutor() as executor:
    # 提交任务并获取 Future 对象列表
    futures = [executor.submit(test_knn_search) for i in range(6000)]

    # 等待所有任务完成
    concurrent.futures.wait(futures)

    # 获取结果
    results = [future.result() for future in futures]
    
    print("avg latency: {}".format(sum(results) / len(results)))