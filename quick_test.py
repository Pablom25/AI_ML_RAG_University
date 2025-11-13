from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

embedding = OllamaEmbeddings(model="mxbai-embed-large")  # same model as build-time
db = Chroma(persist_directory="chroma", embedding_function=embedding)

query = "What are the main themes of the essays?"
docs = db.similarity_search(query, k=3)
for i, d in enumerate(docs, 1):
    print(f"\nResult {i}:\n{d.page_content[:300]}...")
