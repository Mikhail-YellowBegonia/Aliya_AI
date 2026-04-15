import os
import litellm
from dotenv import load_dotenv

# 加载 .env 文件中的配置
load_dotenv()

def test_llm_request(user_input: str):
    """
    使用 LiteLLM 发送一个简单的聊天请求
    """
    model = os.getenv("LITELLM_MODEL", "openai/gpt-4o")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")

    print(f"\n[系统] 正在请求模型: {model}")
    print(f"[系统] Base URL: {base_url}")
    
    try:
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": user_input}],
            api_key=api_key,
            base_url=base_url
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"请求失败: {str(e)}"

def main():
    print("="*40)
    print("Aliya LLM 连通性测试工具")
    print("="*40)
    print("提示: 请确保已经在 .env 文件中填入了正确的 API Key 和 Model。")
    
    while True:
        user_input = input("\n测试输入 (输入 'exit' 退出): ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        if not user_input.strip():
            continue
            
        reply = test_llm_request(user_input)
        print("-" * 20)
        print(f"Aliya 回复:\n{reply}")
        print("-" * 20)

if __name__ == "__main__":
    main()
