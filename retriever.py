from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain.load import dumps, loads

# Get unique documents
def __get_unique_union(documents: list[list]) -> list:
    """ Unique union of retrieved docs """
    # Flatten list of lists, and convert each Document to string
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    # Get unique documents
    unique_docs = list(set(flattened_docs))
    # Return
    return [loads(doc) for doc in unique_docs]

def retriever(question:str) -> list:
    '''Takes question, returns context'''

    # Retriever
    embedding = OllamaEmbeddings(model="mxbai-embed-large")  # same model as build-time
    db = Chroma(persist_directory="chroma", embedding_function=embedding)
    retriever = db.as_retriever(search_kwargs={"k": 3})

    # Multi Query: Different Perspectives
    template = """You are an AI language model assistant. Your task is to generate five 
    different versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search. 
    Provide these alternative questions separated by newlines. Original question: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)

    generate_queries = (
        prompt_perspectives 
        | ChatOllama(model="llama3.1:8b") 
        | StrOutputParser() 
        | (lambda x: x.split("\n"))
    )

    # Chain
    retrieval_chain = generate_queries | retriever.map() | __get_unique_union
    docs = retrieval_chain.invoke({"question":question})
    
    return docs
