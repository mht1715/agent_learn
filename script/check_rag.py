from backend.app.rag.index import search

for hit in search("退款需要多久到账", top_k=3):
    print(f"{hit['score']:.3f}  {hit['source']}#{hit['chunk_id']}  {hit['text'][:60]}")
