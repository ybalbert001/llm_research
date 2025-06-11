# OpenSearch Query Benchmark with Locust

This project contains a Locust script for benchmarking OpenSearch query performance, particularly for vector search (k-NN) operations.

## Prerequisites

Install the required packages:

```bash
pip install locust==2.23.1 opensearch-py boto3 requests_aws4auth
```

## Configuration

Before running the benchmark, update the following variables in `opensearch_locust_benchmark.py`:

- `EMB_MODEL_ENDPOINT`: Your SageMaker embedding model endpoint
- `AOS_ENDPOINT`: Your OpenSearch domain endpoint
- `AOS_INDEX`: The index name to query
- `SAMPLE_QUERIES`: Sample text queries to generate embeddings

## Running the Benchmark

1. Start the Locust web interface:

```bash
locust --host=http://localhost:8080 -f opensearch_locust_benchmark.py --headless --users 20 --spawn-rate 2 --run-time 1m
```

2. Open your browser and go to http://localhost:8089

3. Configure the test parameters:
   - Number of users (concurrent users)
   - Spawn rate (users started/second)
   - Host (can be any value as we're using the OpenSearch client directly)

4. Start the test and monitor the results in real-time

## Understanding the Results

The benchmark includes two types of queries:
- Basic k-NN vector search
- Filtered k-NN search (combining vector search with filters)

Metrics collected include:
- Response time (ms)
- Requests per second
- Failure rate

## Customization

You can modify the script to:
- Add different query types
- Change the number of results returned
- Adjust the wait time between requests
- Add more complex filtering logic
