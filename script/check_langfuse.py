import os
from dotenv import load_dotenv
from pathlib import Path

# 1. 加载 .env 文件（关键步骤）
BASE_DIR = Path(__file__).resolve().parents[1]  # 根据你的目录层级调整
load_dotenv(BASE_DIR / ".env")

# 2. 检查环境变量是否已正确加载（可选，用于排查）
print("Public Key:", os.getenv("LANGFUSE_PUBLIC_KEY")[:10] if os.getenv("LANGFUSE_PUBLIC_KEY") else "Not set")

# 3. 导入 CallbackHandler 并实例化（此时它会自动读取环境变量）
from langfuse.langchain import CallbackHandler
from langfuse import get_client
from app.llm.client import get_chat_client

langfuse_handler = CallbackHandler()  # 不再传任何参数

llm = get_chat_client()
response = llm.invoke(
    input="你是谁",
    config={"callbacks": [langfuse_handler]}
)
print(f"结果：{response}")

# 4. 强制刷新，确保数据发送
get_client().flush()
print("Langfuse 数据已刷新。")
