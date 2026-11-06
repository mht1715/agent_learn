import json
import logging
from time import perf_counter
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage

from app.agent.tools.registry import TOOLS, TOOL_MAP
from app.llm.client import get_chat_client

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("langchain_openai").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
MAX_STEPS = 5
MAX_REPEAT_CALLS = 2  # 同一工具+同一参数调用超过这个次数就终止


def _call_signature(call: dict) -> str:
    logger.info(f"tool_call name=%s args=%s", call["name"], json.dumps(call["args"], ensure_ascii=False))
    return f"{call['name']}:{json.dumps(call['args'], sort_keys=True, ensure_ascii=False)}"


def run_agent(user_input: str) -> dict:
    llm = get_chat_client().bind_tools(TOOLS)
    messages = [
        SystemMessage(content="你是工单助手，需要时调用工具，不要编造数据。"),
        HumanMessage(content=user_input),
    ]
    call_counts: dict[str, int] = {}
    for step in range(1, MAX_STEPS + 1):
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
            return {"status": "ok", "answer": ai.content, "steps": step}

        for call in ai.tool_calls:
            sin = _call_signature(call)
            call_counts[sin] = call_counts.get(sin, 0) + 1
            if call_counts[sin] > MAX_REPEAT_CALLS:
                logger.error(f"repeat_call_abort sin=%s", sin)
                return {
                    "status": "aborted",
                    "reason": "repeat_call_abort",
                    "answer": "同一工具重复多次调用",
                    "steps": step,
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

            messages.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )
    logger.warning("max_steps_reached steps=%d", MAX_STEPS)
    return {
        "status": "aborted",
        "reason": "max_steps",
        "answer": f"达到最大步数 {MAX_STEPS}，任务未完成。",
        "steps": MAX_STEPS,
    }
