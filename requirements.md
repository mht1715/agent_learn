langchain; langchain-openai;# 依赖说明

本项目的 Python 依赖分两类： **阶段必需** 和 **后续阶段预留**。  
安装命令：`pip install -r requirements.txt`

## LLM 客户端 + 配置加载

| 包                  | 用途                                   | 为什么需要                                                               |
|---------------------|----------------------------------------|--------------------------------------------------------------------------|
| `langchain-openai`  | 提供 `ChatOpenAI` / `OpenAIEmbeddings` | 一套客户端同时接入 DeepSeek 和 DashScope 的 OpenAI 兼容接口              |
| `langchain`         | LangChain 元包                         | 后续 LangGraph、工具调用、消息类型都依赖它；当前阶段装上避免后续版本漂移 |
| `python-dotenv`     | 加载 `.env`                            | `pydantic-settings` 底层用它读 `.env` 文件                               |
| `pydantic-settings` | 类型化配置                             | `config.py` 中的 `BaseSettings` 来自它，缺了它 `Settings` 无法运行       |

## 版本约束

```text
langchain-openai>=1.0,<2.0
langchain>=1.0,<2.0
pydantic-settings>=2.0,<3.0
python-dotenv>=1.0,<2.0