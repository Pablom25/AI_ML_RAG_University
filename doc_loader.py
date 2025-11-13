from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

loader = DirectoryLoader(
    "data",
    glob="*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)
docs = loader.load()
print("docs:", len(docs))

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
chunks = splitter.split_documents(docs)
print("chunks:", len(chunks))

embedding = OllamaEmbeddings(model="mxbai-embed-large")
db = Chroma.from_documents(chunks, embedding, persist_directory="chroma")
print("Chroma DB created at ./chroma")
