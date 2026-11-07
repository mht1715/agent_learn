# 目标

- 把 Agent 从脚本变成可被前端消费的服务，尝试实现事件流传输
- 写评测集和评测脚本进行评测，观察和分析评测结果，调用的工具、参数、步数。结果与期望的工具、参数、状态比较

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
- 创建评测脚本，遍历评测集，将每一个评测与对应的事件进行比较，将评测中的期望与事件中的真实值对比，返回通过/失败，统计通过率、平均步数等

# 踩坑

- 要用`fastapi.responses`的`StreamingResponse`,ide自动导入的包可能是错的
- 流式返回要设置正确的类型和头：
- 评测集文件的格式要正确，读取时的处理方法
- 要用到的字段名比较多，一些地方写错了

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
- 如何进行评测：创建一个评测集，包含评测期待的工具、回答、状态，与事件流中返回的事件一一进行比较，返回评测id、是否通过、错误地方等信息