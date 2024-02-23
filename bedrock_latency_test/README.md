# 测试方法

```
pip install -r requirements.txt


# 设置ak/sk 以及region
export ak='' 
export sk=''
export region=''

locust --host=http://localhost:8080 --locustfile=cohere_test.py
```