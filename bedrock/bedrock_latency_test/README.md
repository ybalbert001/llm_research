# 测试方法

```
pip install -r requirements.txt


# 设置ak/sk 以及region
export ak='' 
export sk=''
export region='us-west-2'

locust --host=http://localhost:8080 --locustfile locustfile.py  --headless --users 20 --spawn-rate 2 --run-time 5m

# For titan Testing
locust --host=http://localhost:8080 --locustfile titan_locustfile.py  --headless --users 20 --spawn-rate 2 --run-time 5m
```