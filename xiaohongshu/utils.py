from prompt_template import system_template_text, user_template_text
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from xiaohongshu_model import Xiaohongshu
import requests
import json


#封装返回结果
class BailianResponse:
    def __init__(self, content):
        self.content = content


class BailianChatModel:
    def __init__(self, api_key, endpoint, temperature=0.2):
        self.api_key = api_key
        self.endpoint = endpoint if endpoint else "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.temperature = temperature
    #invoke准备请求
    def invoke(self, prompt_text):
        #请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        # 阿里云百炼标准请求体
        data = {
            "model": "qwen-turbo",  # 可选：qwen-plus/qwen-max
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt_text
                    }
                ]
            },
            "parameters": {
                "temperature": self.temperature,
                "max_tokens": 2000,
                "top_p": 0.8
            }
        }

        try:
            # 发送POST请求
            response = requests.post(
                self.endpoint,
                json=data,
                headers=headers,
                timeout=30  # 添加超时保护
            )
            response.raise_for_status()  # 抛出HTTP错误
            result_json = response.json()


            content = ""
            if "output" in result_json:
                # 有text字段直接取
                if "text" in result_json["output"]:
                    content = result_json["output"]["text"]
                else:
                    # 有choice格式时
                    if "choice" in result_json["output"]:
                        content = result_json["output"]["choice"][0]["message"]["content"]
            else:
                content = f"响应解析失败：{json.dumps(result_json, ensure_ascii=False)}"

            # 洗输出，要不然太丑了
            content = content.replace("\\n","\n").replace("\n"," ")
            return BailianResponse(content)

        except requests.exceptions.HTTPError as e:
            raise Exception(f"API调用失败（HTTP错误）：{e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"调用异常：{str(e)}")



def generate_xiaohongshu(theme, api_key):
    # 构造 prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template_text),
        ("user", user_template_text)
    ])
    output_parser = PydanticOutputParser(pydantic_object=Xiaohongshu)
    # 渲染 prompt，生成文本
    prompt_text = prompt.format(
        parser_instructions=output_parser.get_format_instructions(),
        theme=theme
    )
    # 调用百炼模型
    model = BailianChatModel(api_key=api_key, endpoint="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
    response = model.invoke(prompt_text)
    # 解析返回结果（假设 response.content 是 model 的回复字符串）
    result = output_parser.parse(response.content)
    return result