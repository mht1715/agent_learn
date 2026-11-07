# 目标

- 把 Agent 从脚本变成可被前端消费的服务，尝试实现事件流传输

# 学习内容

- 使用`yield`+`Iterator`实现事件流传输
- 使用`fastapi`启用服务以及设置路由
- 学会使用fastapi的流式返回，示例：

```text
@router.post("/chat/stream")
def chat_stream(req: ChatRequest):
    def gen():
        try:
            for ev in run_agent_event(req.message):
                yield f"data: {json.dumps(ev, ensure_ascii=False)} \n\n"
        except Exception as exc:
            err = {"type": "error", "message": str(exc)}
            yield f"data: {json.dumps(err, ensure_ascii=False)} \n\n"

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
```
- 创建前端，`sse.js`处理sse请求和响应，添加一个聊天测试页面
# 踩坑

- 要用`fastapi.responses`的`StreamingResponse`,ide自动导入的包可能是错的
- 流式返回要设置正确的类型和头：

```text
StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
)
```

- SSE 每帧必须是 data: ...\n\n 双换行结尾，少一个前端就解析不到；X-Accel-Buffering: no 是给以后上 Nginx 时防缓冲用的

# 思考

- 把`return`改为`yield`再加上`Iterator`就可以实现流式传输的效果
- sse比较复杂，直接让ai封装了一个sse工具，主要是学习langchain，防止学习进度卡在这里，之后再研究