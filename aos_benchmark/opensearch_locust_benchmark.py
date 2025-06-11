import json
import random
import boto3
import time
from locust import HttpUser, task, between, events
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

'''
Install these packages first:

pip install locust
pip install opensearch-py
pip install boto3
pip install requests_aws4auth
'''

# Configuration
AOS_ENDPOINT = "vpc-dify-test-vectordb3-einae4woye6qs6g5no2bullf3u.us-west-2.es.amazonaws.com"
AOS_INDEX = "vector_index_62772003_250d_4fb0_bc35_b9d57d20ade3_node"

# Sample queries for embedding
SAMPLE_QUERIES = [
    'RNA crystallization is complicated by inherent difficulties',
    'A major bottleneck in RNA crystallography is often the production of sufficient amounts',
    'This review is meant to be used as a reference for the crystallization of large-structured RNAs',
    'ribozymes and riboswitches',
    'We will discuss the advantages and disadvantages of both traditional and native RNA purification methods',
    'T7 RNA polymerase is commonly used to produce large quantities of RNA by in vitro transcription'
]

def get_embedding(text_arrs):
    """Generate random 1024-dimensional embeddings for each text in the array"""
    embeddings = []
    for _ in text_arrs:
        # Generate a random 1024-dimensional vector
        vector = [random.uniform(-1, 1) for _ in range(1024)]
        
        # Normalize the vector (optional, but recommended for k-NN)
        magnitude = sum(x**2 for x in vector) ** 0.5
        normalized_vector = [x/magnitude for x in vector]
        
        embeddings.append(normalized_vector)
    
    return embeddings

class OpenSearchUser(HttpUser):
    wait_time = between(1, 3)  # Wait between 1-3 seconds between tasks
    
    def on_start(self):
        # Get embeddings for sample queries
        self.embeddings = get_embedding(SAMPLE_QUERIES)
        
        # Initialize OpenSearch client
        credentials = boto3.Session().get_credentials()
        region = boto3.Session().region_name

        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es')
        self.aos_client = OpenSearch(
            hosts=[{'host': AOS_ENDPOINT, 'port': 443}],
            http_auth=('admin', 'Admin_12345'),
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )
    
    @task
    def knn_search_task(self):
        """Perform k-NN search in OpenSearch"""
        # Select a random embedding
        rand_idx = random.randint(0, len(self.embeddings) - 1)
        embedding = self.embeddings[rand_idx]
        
        # Prepare kNN query
        query = {
            "size": 5,  # Return top 5 results
            "query": {
                "knn": {
                    "vector": {
                        "vector": embedding,
                        "k": 5
                    }
                }
            }
        }
        
        # Execute search and record metrics
        try:
            start_time = time.time()
            response = self.aos_client.search(
                body=query,
                index=AOS_INDEX
            )
            response_time = (time.time() - start_time) * 1000
            # Record success using Locust's current API
            events.request.fire(
                request_type="custom_type",
                name="knn_search",
                response_time=response_time, #response['took'],
                response_length=len(json.dumps(response)),  # 可以根据需要设置
                exception=None,     # 成功请求无异常
                context={}
            )
        except Exception as e:
            # Record failure using Locust's current API
            events.request.fire(
                request_type="custom_type",
                name="knn_search",
                response_time=1000,
                response_length=0,  # 可以根据需要设置
                exception=e,     # 成功请求无异常
                context={}
            )


if __name__ == "__main__":
    # This script is designed to be run with the Locust command line
    # Run with: locust -f opensearch_locust_benchmark.py
    pass
