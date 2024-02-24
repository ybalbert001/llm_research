# 测试方法

```
pip install -r requirements.txt


# 设置ak/sk 以及region
export ak='AKIA2AIJZ3XPLX5RXB5B' 
export sk='YgoadZFFUDCzpg356ZoKg08aoRIOubVNynY12c6o'
export region='us-west-2'

locust -f cohere_test.py --headless --users 10 --spawn-rate 2 --run-time 5m
```