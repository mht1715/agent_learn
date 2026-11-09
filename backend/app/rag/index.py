from functools import lru_cache
from pathlib import Path

import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.app.llm.client import get_embedding_client

CORPUS_DIR = Path(__file__).parent.joinpath("corpus")


@lru_cache(maxsize=1)
def build_index():
    docs = []
    for p in sorted(CORPUS_DIR.glob("*.md")):
        docs.append({"source": p.name, "text": p.read_text(encoding="utf-8")})

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, chunk_overlap=60, separators=["\n\n", "\n", "。", ""]
    )
    chunks = []
    for d in docs:
        for i, piece in enumerate(splitter.split_text(d["text"])):
            chunks.append({"source": d["source"], "chunk_id": i, "text": piece})

    embed = get_embedding_client()
    texts = [c["text"] for c in chunks]
    # DashScope 单次 10 条，分批
    vecs = []
    for i in range(0, len(texts), 10):
        vecs.extend(embed.embed_documents(texts[i:i + 10]))

    mat = np.array(vecs, dtype=np.float32)
    mat /= np.linalg.norm(mat, axis=1, keepdims=True) + 1e-8  # 归一化，用点积当余弦
    return {"chunks": chunks, "matrix": mat, "embed": embed}


def search(query: str, top_k: int = 3) -> list[dict]:
    idx = build_index()
    q = np.array(idx["embed"].embed_query(query), dtype=np.float32)
    q /= np.linalg.norm(q) + 1e-8
    scores = idx["matrix"] @ q
    order = np.argsort(-scores)[:top_k]
    return [
        {**idx["chunks"][i], "score": float(scores[i])}
        for i in order
    ]


def search_all(query: str) -> list[dict]:
    """返回全部块的分数，用于调试排序。"""
    idx = build_index()
    q = np.array(idx["embed"].embed_query(query), dtype=np.float32)
    q /= np.linalg.norm(q) + 1e-8
    scores = idx["matrix"] @ q
    order = np.argsort(-scores)
    return [{**idx["chunks"][i], "score": float(scores[i])} for i in order]
