import json
import logging
from time import perf_counter
from typing import Iterator, Any

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from app.agent.tools.registry import TOOLS, TOOL_MAP
from app.llm.client import get_chat_client

logging.getLogger("httpx2").setLevel(logging.WARNING)
logging.getLogger("langchain_openai").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
MAX_STEPS = 5
MAX_REPEAT_CALLS = 2  # 同一工具+同一参数调用超过这个次数就终止
# 用内存字典模拟数据库存储：{session_id: [消息列表]}
MEMORY_STORE = {}


def _call_signature(call: dict) -> str:
    logger.info(f"tool_call name=%s args=%s", call["name"], json.dumps(call["args"], ensure_ascii=False))
    return f"{call['name']}:{json.dumps(call['args'], sort_keys=True, ensure_ascii=False)}"


def run_agent_events(user_input: str, session_id: str = "default") -> Iterator[dict]:
    llm = get_chat_client().bind_tools(TOOLS)
    if session_id not in MEMORY_STORE:
        MEMORY_STORE[session_id] = [
            SystemMessage(content=(
                "你是工单助手。你需要严格遵守以下规则：\n"
                "1. 涉及订单状态、物流、天气等实时数据时，调用对应工具查询，不要编造。\n"
                "2. 涉及平台规则、退款政策、发票、售后流程等内部知识时，必须先调用 search_knowledge_base 检索知识库。\n"
                "3. 如果工具查不到，如实告知用户，不要自行发挥。"
            ))
        ]

    messages = MEMORY_STORE[session_id]
    messages.append(HumanMessage(content=user_input))
    call_counts: dict[str, int] = {}
    for step in range(1, MAX_STEPS + 1):
        yield {
            "type": "step_start",
            "step": step
        }
        t0 = perf_counter()
        ai = llm.invoke(messages)
        latency_ms = int((perf_counter() - t0) * 1000)
        logger.info(
            "step=%d latency_ms=%d tool_calls=%d content_len=%d",
            step,
            latency_ms,
            len(ai.tool_calls or []),
            len(ai.content or ""),
        )
        messages.append(ai)

        if not ai.tool_calls:
            yield {
                "type": "final",
                "status": "ok",
                "answer": ai.content,
                "steps": step
            }
            return None

        for call in ai.tool_calls:
            sin = _call_signature(call)
            call_counts[sin] = call_counts.get(sin, 0) + 1
            if call_counts[sin] > MAX_REPEAT_CALLS:
                logger.error(f"repeat_call_abort sin=%s", sin)
                yield {
                    "type": "final",
                    "status": "aborted",
                    "reason": "repeat_call_abort",
                    "answer": "同一工具重复多次调用",
                    "steps": step,
                }
                return None
            yield {
                "type": "tool_call",
                "step": step,
                "name": call["name"],
                "args": call["args"]
            }
            tool = TOOL_MAP.get(call["name"])
            if tool is None:
                result = f"错误：不存在工具 {call['name']}"
                logger.warning("unknown_tool name=%s", call["name"])
            else:
                try:
                    result = tool.invoke(call["args"])
                except Exception as e:
                    result = f"工具{call['name']}执行失败"
                    logger.exception("unknown_tool name=%s", call["name"])
            yield {
                "type": "tool_result",
                "step": step,
                "name": call["name"],
                "result": str(result)
            }
            messages.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )
    logger.warning("max_steps_reached steps=%d", MAX_STEPS)
    yield {
        "type": "final",
        "status": "aborted",
        "reason": "max_steps",
        "answer": f"达到最大步数 {MAX_STEPS}，任务未完成。",
        "steps": MAX_STEPS,
    }


def run_agent(user_input: str, session_id: str = "default") -> dict[str, str] | dict[Any, Any]:
    final = {"type": "error", "message": "no event produced"}
    for ev in run_agent_events(user_input, session_id):
        if ev["type"] in ("final", "error"):
            final = ev
    return final
