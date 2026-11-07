import json

from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.agent.loop import run_agent, run_agent_events

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(req: ChatRequest):
    return run_agent(req.message)


@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    def gen():
        try:
            for ev in run_agent_events(req.message):
                yield f"data: {json.dumps(ev, ensure_ascii=False)} \n\n"
        except Exception as exc:
            err = {"type": "error", "message": str(exc)}
            yield f"data: {json.dumps(err, ensure_ascii=False)} \n\n"

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
