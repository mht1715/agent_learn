import sqlite3
from typing import TypedDict, Annotated
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

from app.agent.memory import DB_PATH
from backend.app.agent.tools.registry import TOOLS
from backend.app.llm.client import get_chat_client


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


llm = get_chat_client().bind_tools(TOOLS)


def agent_node(state: AgentState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        sys_msg = SystemMessage(content=(
            "你是工单助手。\n"
            "1. 实时数据（订单、物流）用工具查。\n"
            "2. 规则政策必须调 search_knowledge_base。\n"
            "3. 涉及取消订单等敏感操作，请调用对应的取消工具。"
        ))
        messages = [sys_msg] + messages

    response = llm.invoke(messages)
    return {"messages": [response]}


# 分离普通工具和高危工具
sensitive_tool_names = ["cancel_order"]
normal_tools = [t for t in TOOLS if t.name not in sensitive_tool_names]
sensitive_tools = [t for t in TOOLS if t.name in sensitive_tool_names]


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END

    # 检查是否有高危工具
    for tool_call in last_message.tool_calls:
        if tool_call["name"] in sensitive_tool_names:
            return "sensitive_tools"

    return "tools"


# 构建图
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(normal_tools))
# 给敏感工具也建一个节点
builder.add_node("sensitive_tools", ToolNode(sensitive_tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", "sensitive_tools": "sensitive_tools", END: END}
)
builder.add_edge("tools", "agent")
builder.add_edge("sensitive_tools", "agent")

# 持久化
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
checkpointer = SqliteSaver(conn)

# 只拦截 sensitive_tools 节点
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["sensitive_tools"]
)
