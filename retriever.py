from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

embedding = OllamaEmbeddings(model="mxbai-embed-large")  # same model as build-time
db = Chroma(persist_directory="chroma", embedding_function=embedding)

retriever = db.as_retriever(search_kwargs={"k": 3})