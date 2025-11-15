from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

def decompose_question(question: str) -> list[str]:
    """Break complex questions into sub-questions for better reasoning"""
    
    template = """Break this complex question into 2-4 simpler sub-questions that together address the main question.
    
QUESTION: {question}

Return one sub-question per line, without numbering."""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOllama(model="llama3.1:8b", temperature=0.1)
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": question})
    
    sub_questions = [q.strip() for q in response.split("\n") if q.strip()]
    return sub_questions if sub_questions else [question]