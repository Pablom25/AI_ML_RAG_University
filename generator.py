from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama

def generator(docs:list, question:str) -> str:
    '''Takes documents and question, returns answer with metadata awareness'''

    # Build context with metadata annotations
    context_parts = []
    for doc in docs:
        student = doc.metadata.get("student", "Unknown")
        doc_type = doc.metadata.get("doc_type", "document")
        context_parts.append(f"[{student.upper()} - {doc_type.upper()}]\n{doc.page_content}")
    
    context = "\n---\n".join(context_parts)

    # Advanced reasoning template with chain-of-thought
    template = """You are an admissions assistant with deep analytical capabilities.

CONTEXT DOCUMENTS:
{context}

QUESTION: {question}

REASONING FRAMEWORK:
Use this structured approach to answer:

1. INFORMATION EXTRACTION
   - Identify all relevant facts from the documents
   - List key entities (students, programs, values, skills)
   - Note dates, locations, and achievements

2. PATTERN RECOGNITION
   - Look for common themes, skills, or experiences
   - Identify correlations between student backgrounds and university values
   - Notice trends in educational paths or extracurriculars

3. LOGICAL CONNECTIONS
   - How do different pieces of information relate?
   - What underlying principles connect the facts?
   - Are there cause-effect relationships?

4. SYNTHESIS
   - Combine insights from multiple documents
   - Draw conclusions supported by evidence
   - Identify gaps in reasoning

5. VALIDATION
   - Ensure conclusions are supported by the documents
   - Cite specific evidence for claims
   - Flag assumptions or inferences clearly

RESPONSE GUIDELINES:
- Show your reasoning step-by-step
- Always cite which documents you're referencing
- Distinguish between facts and inferences
- If information is unavailable, explicitly state it
- For aggregate questions: list items before providing counts/patterns
- For comparative questions: present evidence from each source before comparing

ANSWER:"""
    
    prompt = ChatPromptTemplate.from_template(template)

    # Slightly higher temperature to encourage exploration while maintaining accuracy
    llm = ChatOllama(model="llama3.1:8b", temperature=0.1)

    # Chain
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})
    return answer
