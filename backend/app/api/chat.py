import json

from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler

load_dotenv()
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from backend.app.agent.graph import graph

router = APIRouter()
langfuse_handler = CallbackHandler()


class ChatRequest(BaseModel):
    message: str | None = None
    session_id: str
    action: str = "chat"  # chat: 正常对话, resume: 审批继续


@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    config = {
        "configurable": {"thread_id": req.session_id},
        "callbacks": [langfuse_handler],
        "metadata": {"langfuse_session_id": req.session_id},
    }

    def gen():
        try:
            # 判断是正常对话还是审批恢复
            inputs = {"messages": [HumanMessage(content=req.message)]} if req.action == "chat" else None

            # 如果是 resume，先确认状态里确实有挂起
            if req.action == "resume":
                state = graph.get_state(config)
                if not state.next:
                    yield f"data: {json.dumps({'type': 'error', 'message': '当前没有挂起的任务'}, ensure_ascii=False)}\n\n"
                    return

            for event in graph.stream(inputs, config=config, stream_mode="values"):
                last_msg = event["messages"][-1]
                msg_type = getattr(last_msg, "type", "")

                if msg_type == "human":
                    continue

                # 1. 如果是 AI 决定调用工具
                if msg_type == "ai" and getattr(last_msg, "tool_calls", None):
                    for tc in last_msg.tool_calls:
                        ev = {"type": "tool_call", "name": tc["name"], "args": tc["args"]}
                        yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"

                    # 【新增逻辑】：立刻检查是否因为高危工具挂起了
                    state = graph.get_state(config)
                    if state.next and "sensitive_tools" in state.next:
                        ev = {
                            "type": "interrupt",
                            "answer": "检测到高危操作，需要人工审批。",
                            "tool": last_msg.tool_calls[0]["name"]
                        }
                        yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"

                # 2. 如果是工具执行结果
                elif msg_type == "tool":
                    ev = {"type": "tool_result", "name": last_msg.name, "result": str(last_msg.content)}
                    yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"

                # 3. 如果是 AI 的最终回答
                elif msg_type == "ai" and not getattr(last_msg, "tool_calls", None):
                    ev = {"type": "final", "status": "ok", "answer": last_msg.content}
                    yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"

        except Exception as exc:
            err = {"type": "error", "message": str(exc)}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
