from langchain_core.tools import tool

from backend.app.rag.index import search


@tool
def search_knowledge_base(query: str) -> str:
    """当用户询问平台规则、退款政策、发票申请、配送时效等内部知识时，使用此工具检索知识库。"""
    hits = search(query, top_k=2)
    if not hits:
        return "知识库中未找到相关内容。"

    # 拼接检索结果，并带上来源，方便模型引用
    results = []
    for hit in hits:
        results.append(f"[来源: {hit['source']}]\n{hit['text']}")

    return "\n\n---\n\n".join(results)
