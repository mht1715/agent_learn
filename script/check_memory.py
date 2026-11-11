from app.agent.loop import run_agent

print("--- 第一轮对话 ---")
res1 = run_agent("我想问下订单 A1001 状态", session_id="test-1")
print(res1["answer"])

print("\n--- 第二轮对话（重启后模拟，或直接接着跑） ---")
res2 = run_agent("那它还能取消吗？", session_id="test-1")
print(res2["answer"])
