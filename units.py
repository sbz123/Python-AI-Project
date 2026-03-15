from prompt_template import system_template_text, user_template_text
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
import requests
import json
from xiaohongshu_model import Xiaohongshu

class BailianResponse:
    def __init__(self, content):
        self.content = content

class BailianChatModel:
    def __init__(self, api_key, endpoint=None, temperature=0.2):
        self.api_key = api_key
        self.endpoint = endpoint if endpoint else "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.temperature = temperature

    def invoke(self, prompt_text):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": "qwen-turbo",
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
            response = requests.post(
                self.endpoint,
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result_json = response.json()
            content = ""
            if "output" in result_json:
                if "text" in result_json["output"]:
                    content = result_json["output"]["text"]
                elif "choice" in result_json["output"]:
                    content = result_json["output"]["choice"][0]["message"]["content"]
            else:
                content = f"响应解析失败：{json.dumps(result_json, ensure_ascii=False)}"
            content = content.replace("\\n", "\n").replace("\n", " ")
            return BailianResponse(content)
        except requests.exceptions.HTTPError as e:
            raise Exception(f"API调用失败（HTTP错误）：{e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"调用异常：{str(e)}")

def generate_xhs(theme, api_key):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template_text),
        ("user", user_template_text)
    ])
    output_parser = PydanticOutputParser(pydantic_object=Xiaohongshu)
    prompt_text = prompt.format(
        parser_instructions=output_parser.get_format_instructions(),
        theme=theme
    )
    model = BailianChatModel(api_key=api_key)
    response = model.invoke(prompt_text)
    result = output_parser.parse(response.content)
    return result

if __name__ == "__main__":
    print(generate_xhs("大模型", "sk-1e88a356808944c495a1a5e932a06064"))