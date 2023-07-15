import boto3
import json
import time
import re

prompt_data1 = """
请参考反引号中的FAQ回复客户的问题, 如果客户描述信息不明确，请提供一些备选让客户确认，以"请明确问题"结尾
```
Question: 销售的核心数据是？
Answer: 
1. AC1 Order Actual (Statistic Currency)：AC1 订单实际金额（统计货币）
2. AC1 Sales_Billing (Statistic Currency)：AC1 销售开票金额（统计货币）
3. Sales Growth%：销售增长率
4. Order Growth%：订单增长率
5. Target：年度指标

Question: AC1 包含哪些指标？
Answer: 订单实际金额AC1 Order Actual和销售开票金额AC1 Sales_Billing
```
客户: {}
AI:
"""

prompt_data2 = """[问题]介绍下AC1 Order Actual
=>明确

[问题]介绍下AC1 Sales_Billing
=>明确

[问题]介绍下AC1 Sales_Billing的业务定义
=>不明确

[问题]介绍下AC1
=>不明确

[问题]AC2是啥
=>不明确

[问题]Sales Growth是定义是啥
=>明确

[问题]Target是啥KPI
=>明确

[问题]KPI是啥？
=>不明确

[问题]销售核心数据是啥
=>不明确

[问题]年度指标是什么
=>明确

[问题]AC1 订单实际金额是什么
=>明确

[问题]{}
=>"""

prompt_data3 = """请依据表格中的信息回答客户的问题

| 序号 | 数据标准类型 | Data  Owner   | Indicator/Field名称                     | L1一级主题域 | L2二级主题域        | 数据集类别          | 数据类别 | 中文名称   | 英文名称                                | 数据别名 | 业务定义       | 业务规则                                                     | 值域 | 度量单位 |
| ---- | ------------ | ------------- | --------------------------------------- | ------------ | ------------------- | ------------------- | -------- | ---------- | --------------------------------------- | -------- | -------------- | ------------------------------------------------------------ | ---- | -------- |
| 1    | Indicator    | Shirley Zhang | AC1: Order Actual (Statistic  Currenry) | Sales        | Pricing & Discount  | Business Dimensions | KPI      | AC1 Order  | AC1: Order Actual (Statistic  Currenry) | 无       | Net Order      | Order: 列表价 - 折扣     （标准折扣，特折，3PA,财务前返...） | 无   | 本位币   |
| 2    | Indicator    | Shirley Zhang | AC1:  Sales_Billing(Statistic Currency) | Sales        | Pricing &  Discount | Business Dimensions | KPI      | AC1 Sales  | AC1:  Sales_Billing(Statistic Currency) | 无       | Net Sales      | Sales: 列表价 - 折扣     （标准折扣，特折，3PA,财务前返...） | 无   | 本位币   |
| 3    | Indicator    | Shirley Zhang | AC2: Order  Actual(Statistic Currency)  | Sales        | Pricing &  Discount | Business Dimensions | KPI      | AC2 Order  | AC2: Order  Actual(Statistic Currency)  | 无       | Net Net Order  | Order: AC1 - 分销商返点计提                                  | 无   | 本位币   |
| 4    | Indicator    | Shirley Zhang | AC2:  Sales_Billing(Statistic Currency) | Sales        | Pricing &  Discount | Business Dimensions | KPI      | AC2 Sales  | AC2:  Sales_Billing(Statistic Currency) | 无       | Net Net Sales  | Sales: AC1 - 分销商返点计提                                  | 无   | 本位币   |
| 5    | Indicator    | Shirley Zhang | Sales Growth%                           | Sales        | Pricing &  Discount | Business Dimensions | KPI      | 销量增长率 | Sales Growth%                           | 无       | 销售增长率     | （YTD Sales / YTD-1  Sales -1）%                             | 无   | 百分比   |
| 6    | Indicator    | Shirley Zhang | Order Growth%                           | Sales        | Pricing &  Discount | Business Dimensions | KPI      | 订单增长率 | Order Growth%                           | 无       | 销售订单增长率 | （YTD Order / YTD-1  Order -1）%                             | 无   | 百分比   |
| 7    | Indicator    | Shirley Zhang | Target                                  | Sales        | Pricing &  Discount | Business Dimensions | KPI      | 年度指标   | Yearly Target                           | 无       | 年度签约指标   | Yearly Target                                                | 无   | 本位币   |


客户: {}
回答: """

def bedrock_generate(prompt_data, stop):
    bedrock = boto3.client(
        service_name="bedrock",
        region_name="us-east-1",
        endpoint_url="https://bedrock.us-east-1.amazonaws.com",
    )
    
    body = json.dumps({"prompt": prompt_data,
                       "max_tokens_to_sample": 250,
                       "temperature": 0.0,
                       "stop_sequences": [stop,]})
                       #,'\n'
                       
    modelId = "anthropic.claude-v1"  # change this to use a different version from the model provider
    accept = "application/json"
    contentType = "application/json"
    
    response = bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())
    time.sleep(2)
    return response_body.get("completion")
 
def enforce_stop_tokens(text: str, stop: List[str]) -> str:
    """Cut off the text as soon as any stop words occur."""
    if stop is None:
        return text
    
    return re.split("|".join(stop), text)[0]

def chatglm2_generate(prompt_data, stop):
    endpoint_name = "chatglm2-2023-06-27-06-53-41-986-endpoint"
    smr_client = boto3.client("sagemaker-runtime")

    parameters = {
      "max_length": 2048,
      "temperature": 0.01,
      "num_beams": 1, # >1可能会报错，"probability tensor contains either `inf`, `nan` or element < 0"； 即使remove_invalid_values=True也不能解决
      "do_sample": False,
      "top_p": 0.7,
      "logits_processor" : None,
      # "remove_invalid_values" : True
    }

    response_model = smr_client.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=json.dumps(
            {
                "inputs": prompt_data,
                "parameters": parameters,
                "history" : []
            }
            ),
            ContentType="application/json",
        )

    json_ret = json.loads(response_model['Body'].read().decode('utf8'))
    answer = json_ret['outputs']
    answer = enforce_stop_tokens(answer, [stop,])
    return answer


query1 = "AC1 Order Actual是啥？"
query2 = "AC1 介绍下"

print("[判断query是否明确] query: {} result: {}".format(query1, bedrock_generate(prompt_data2.format(query1), stop= '\n')))
print("[直接回复] answer: {}".format(bedrock_generate(prompt_data3.format(query1), stop='客户:')))
print("==============")
print("[判断query是否明确] query: {} result: {}".format(query2, bedrock_generate(prompt_data2.format(query2), stop= '\n')))
print("[继续询问] ask: {}".format(bedrock_generate(prompt_data1.format(query2), stop='客户:')))
# print(bedrock_generate(prompt_data3, stop='客户:'))