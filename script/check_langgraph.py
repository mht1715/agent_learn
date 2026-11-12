from langchain_core.messages import HumanMessage
from backend.app.agent.graph import graph
import uuid

# 每次测试用新的 thread_id，避免脏数据
session_id = f"test-{uuid.uuid4().hex[:6]}"
config = {"configurable": {"thread_id": session_id}}

print("=== 1. 普通查询（不会被中断，直接跑完） ===")
for event in graph.stream(
    {"messages": [HumanMessage(content="订单 A1001 状态")]},
    config=config,
    stream_mode="values"
):
    event["messages"][-1].pretty_print()

print("\n=== 2. 高危操作（会在此挂起） ===")
for event in graph.stream(
    {"messages": [HumanMessage(content="帮我取消订单 A1001")]},
    config=config,
    stream_mode="values"
):
    event["messages"][-1].pretty_print()

print("\n=== 3. 检查状态 ===")
state = graph.get_state(config)
print("当前挂起的下一个节点:", state.next)
# 这里应该输出 ('sensitive_tools',)

print("\n=== 4. 人工审批通过，恢复执行 ===")
# 传入 None 继续执行挂起的图
for event in graph.stream(
    None,
    config=config,
    stream_mode="values"
):
    event["messages"][-1].pretty_print()