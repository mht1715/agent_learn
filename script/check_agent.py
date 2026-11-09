import logging

from app.agent.loop import run_agent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ------测试简单问答
# cases = ["北京天气怎么样", "订单 A1001 到哪了", "你好"]
# for q in cases:
#     print("=" * 40)
#     print("Q:", q)
#     print("A:", run_agent(q))

# -------测试agentic-rag
# print(run_agent("退款大概多久能到账？"))
# print(run_agent("订单 A1001 什么时候发货？顺便告诉我开票规则"))

#--------测试带上下文的问答
print("--- 第一轮 ---")
print(run_agent("我想问下订单 A1001 状态", session_id="user-1")["answer"])

print("\n--- 第二轮，测试记忆 ---")
print(run_agent("那它还能取消吗？", session_id="user-1")["answer"])

print("\n--- 第三轮，测试隔离（另一个人） ---")
print(run_agent("它还能取消吗？", session_id="user-2")["answer"])