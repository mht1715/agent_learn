import logging

from app.agent.loop import run_agent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

cases = ["北京天气怎么样", "订单 A1001 到哪了", "你好"]
for q in cases:
    print("=" * 40)
    print("Q:", q)
    print("A:", run_agent(q))