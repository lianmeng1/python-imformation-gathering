import openai

api_url = ''
api_key = ''
# 查询 ChatGPT API 密钥对应的模型

model = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'What is the model id?'}
    ]
)

# 提取模型信息
model_id = model['model']
print(f"Model ID: {model_id}")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
article=''
content_sent = '总结以下文章：' + article
openai.api_key = ''
response = openai.Completion.create(
    engine="gpt-3.5-turbo-0301",
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': content_sent}
    ],
    temperature=0,
)
print(response["choices"][0]["message"]["content"])

# # 提取生成的回复
# reply = response.choices[0].text.strip()
#
# # 输出回复
# print(reply)
