from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama

def generator(docs:list, question:str) -> str:
    '''Takes documents and question, returns answer'''

    # Print inputs
    print(f"Question being answered: {question}, context: {docs}")

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
    return answer
