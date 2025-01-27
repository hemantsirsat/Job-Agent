from openai import OpenAI
from config import DEEPSEEK_API

client = OpenAI(api_key=DEEPSEEK_API, base_url="http://localhost:11434/v1")
response = client.chat.completions.create(
    model="deepseek-r1:1.5b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"},
    ],
    stream=False,
)

print(response.choices[0].message.content)