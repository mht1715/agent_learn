# 目标

- 全栈闭环，把 LangGraph 的审批流接入 FastAPI 和 Vue 前端
- --
- 用langfuse实现简单的可观测性

# 学习内容

- 修改 `chat.py`，添加审批功能
- 修改 `ChatRequest`，添加会话id和消息类型，用于判断是聊天还是审批
- 在每次对话中带上会话id
- --
- 准备好langfuse的配置，公钥、私钥放在 `.env`
- 准备好 `CallbacksHandler`，在llm请求的config中配置好即可：
```python
config = {
    "configurable": {"thread_id": req.session_id},
    "callbacks": [langfuse_handler],
    "metadata": {"langfuse_session_id": req.session_id},
}
```

# 踩坑

- 

# 思考

- 目前实现的是简单的可观测，简单配置好langfuse就可以了