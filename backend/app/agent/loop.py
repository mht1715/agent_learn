from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage

from app.agent.tools.registry import TOOLS, TOOL_MAP
from app.llm.client import get_chat_client

MAX_STEPS = 5


def run_agent(user_input: str) -> str:
    llm = get_chat_client().bind_tools(TOOLS)
    messages = [
        SystemMessage(content="你是工单助手，需要时调用工具，不要编造数据。"),
        HumanMessage(content=user_input),
    ]

    for i in range(MAX_STEPS):
        ai = llm.invoke(messages)
        messages.append(ai)
        print(f"第{i + 1}轮-消息记录：", ai)

        if not ai.tool_calls:
            return ai.content

        for call in ai.tool_calls:
            tool = TOOL_MAP.get(call["name"])
            result = (
                tool.invoke(call["args"])
                if tool
                else f"错误：不存在工具 {call['name']}"
            )
            messages.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )
    return f"{MAX_STEPS}次已执行完成"
