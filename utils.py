from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
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



def generate_script(subject, video_length, creativity, bailian_api_key, bailian_endpoint):
    title_template = ChatPromptTemplate.from_messages(
        [
            ("human", "请为'{subject}'这个主题的视频想一个吸引人的标题，仅返回标题文本，不要多余内容")
        ]
    )
    script_template = ChatPromptTemplate.from_messages(
        [
            ("human",
             """你是一位短视频频道的博主。根据以下标题和相关信息，为短视频频道写一个视频脚本。
             视频标题：{title}，视频时长：{duration}分钟，生成的脚本的长度尽量遵循视频时长的要求。
             要求开头抓住眼球，中间提供干货内容，结尾有惊喜，脚本格式也请按照【开头、中间，结尾】分隔。
             整体内容的表达方式要尽量轻松有趣，吸引年轻人。
             脚本内容可以结合以下维基百科搜索出的信息，但仅作为参考，只结合相关的即可，对不相关的进行忽略：
             ```{wikipedia_search}```
             请仅返回脚本内容，不要多余的解释性文字。"""
             )
        ]
    )

    # 初始化自定义模型
    model = BailianChatModel(
        api_key=bailian_api_key,
        endpoint=bailian_endpoint,
        temperature=creativity
    )

    # 生成标题
    title_prompt = title_template.format_prompt(subject=subject).to_string()
    title = model.invoke(title_prompt).content.strip()  # 去除首尾空格

    # 维基百科搜索
    search = WikipediaAPIWrapper(lang="zh")
    search_result = search.run(subject)

    # 生成脚本
    script_prompt = script_template.format_prompt(
        title=title,
        duration=video_length,
        wikipedia_search=search_result
    ).to_string()
    script = model.invoke(script_prompt).content.strip()

    return search_result, title, script

# print(generate_script("面试技巧",1.00,0.7,'sk-1e88a356808944c495a1a5e932a06064','https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'))

