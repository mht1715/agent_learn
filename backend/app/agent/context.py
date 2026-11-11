from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from backend.app.llm.client import get_chat_client

MAX_RECENT_MESSAGES = 6  # 保留最近 3 轮对话（1轮=1个Human+1个AI）


def compress_history(messages: list) -> list:
    """传入全量历史，返回压缩后的历史。"""
    # 将系统提示词剥离出来
    sys_msg = messages[0]
    history = messages[1:]

    if len(history) <= MAX_RECENT_MESSAGES:
        return messages  # 历史很短，不压缩

    # 切分：旧的、新的
    to_summarize = history[:-MAX_RECENT_MESSAGES]
    recent = history[-MAX_RECENT_MESSAGES:]

    # 让 LLM 总结旧的对话
    summary_prompt = "请用一句话总结以下客服对话的核心意图和已确认的事实：\n"
    for m in to_summarize:
        role = "用户" if isinstance(m, HumanMessage) else "助手"
        summary_prompt += f"{role}: {m.content}\n"

    llm = get_chat_client()
    summary_resp = llm.invoke(summary_prompt)

    # 用一条特殊的 SystemMessage 替代旧历史
    summary_msg = SystemMessage(content=f"【历史对话摘要】{summary_resp.content}")

    # 返回：原始 System + 摘要 + 最近几轮
    return [sys_msg, summary_msg] + recent
