from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama

def is_complex_question(question: str) -> bool:
    """
    Detect if a question is complex enough to warrant decomposition.
    """
    # Keywords that indicate compound/complex questions
    complexity_indicators = [
        " and ", " or ", " also ", " as well as ",
        "compare", "contrast", "relationship", "relate",
        "both", "either", "multiple", "several",
        "how does", "why does", "what is the connection",
        "analyze", "evaluate", "assess"
    ]
    
    question_lower = question.lower()
    
    # Check for multiple question marks or semicolons
    if question.count("?") > 1 or ";" in question:
        return True
    
    # Check for complexity indicators
    complexity_count = sum(1 for indicator in complexity_indicators if indicator in question_lower)
    
    # If 2+ indicators or very long question, it's likely complex
    return complexity_count >= 2 or len(question.split()) > 20

def decompose_question(question: str) -> list[str]:
    """
    Uses LLM to break a complex question into 2-4 simpler sub-questions.
    Only decomposes if the question is detected as complex.
    """
    # First check if decomposition is needed
    if not is_complex_question(question):
        return [question]
    
    template = """You are an expert at breaking down complex questions into simpler sub-questions.

QUESTION: {question}

Break this question into 2-4 simpler sub-questions that together address the main question.
Return one sub-question per line, without numbering or extra text.

If the question is already simple, return just the original question."""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOllama(model="llama3.1:8b", temperature=0.1)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": question})
    sub_questions = [q.strip() for q in response.split("\n") if q.strip()]
    
    # If only one sub-question returned, just use the original
    return sub_questions if len(sub_questions) > 1 else [question]