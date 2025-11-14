from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama

# Question
question = "What topic does anthony talk about in his essay?"

# Retrieve
embedding = OllamaEmbeddings(model="mxbai-embed-large")  # same model as build-time
db = Chroma(persist_directory="chroma", embedding_function=embedding)
retriever = db.as_retriever(search_kwargs={"k": 3})
docs = retriever.get_relevant_documents(question)

# Template Prompt
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# LLM
llm = ChatOllama(model="llama3.1:8b", temperature=0)

# Chain
chain = prompt | llm | StrOutputParser()
answer = chain.invoke({"context": docs, "question": question})
print(answer)
