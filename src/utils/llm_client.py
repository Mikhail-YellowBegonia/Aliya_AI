import os
import litellm
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """LiteLLM 客户端包装类"""
    def __init__(self):
        # 默认配置
        self.default_model = os.getenv("LITELLM_MODEL")
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")

    def ask(self, prompt: str, system_instruction: str = None, model: str = None) -> str:
        """
        同步请求接口
        - model: 如果传入，则覆盖环境变量中的默认模型
        """
        target_model = model or self.default_model
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = litellm.completion(
                model=target_model,
                messages=messages,
                api_key=self.api_key,
                base_url=self.base_url
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[LLM Error] {str(e)}"
