# 第一天学习内容

- 创建`.env`，进行环境配置
- 创建`config.py`，封装配置，方便装配使用
- 创建`client.py`客户端，方便管理模型，调用模型服务
- 使用`functools.lru_cache`缓存函数的计算结果，提高函数的执行效率,确保只创建一次，不会重复初始化，处理多线程安全问题。
  `functools.cache`
  无最大限制，但是占用内存大

# 踩坑

- `OpenAIEmbeddings`配置时的兼容问题，需要设置一些参数,否则报错:

```text
    dimensions=settings.embedding_dimensions,
    check_embedding_ctx_length=False,
    chunk_size=10
```

# 思考

难度适中，进行一些简单的配置，封装客户端，了解 `lru_cache`