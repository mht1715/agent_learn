from backend.app.llm.client import get_chat_client, get_embedding_client

chat = get_chat_client()
reply = chat.invoke("你是谁")
print(reply.content)

embed = get_embedding_client()
vecs = embed.embed_documents(["工单退款流程", "如何申请发票"])
print("dims:", len(vecs[0]), "counts:", len(vecs))
