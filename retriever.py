# retriever.py
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
import difflib
from routing import get_known_students

def _normalize_name(s: Optional[str]) -> Optional[str]:
    return s.lower().replace(" ", "").replace("_", "") if s else None

def _unique_by_key(docs: List, key_fn) -> List:
    seen = set()
    out = []
    for d in docs:
        k = key_fn(d)
        if k in seen:
            continue
        seen.add(k)
        out.append(d)
    return out

def _resolve_student_name(routed_name: str | None, known_students: list[str]) -> str | None:
    if not routed_name:
        return None
    routed_name = routed_name.lower().replace(" ", "").replace("_", "")
    best = difflib.get_close_matches(routed_name, known_students, n=1, cutoff=0.75)
    return best[0] if best else None

def retriever(question: str, student: Optional[str], intent: str, known_students: list[str]) -> List:
    """
    Takes question + routed student/intent and returns a list[Document].
    - student: normalized student name or None
    - intent: 'student_specific' | 'university_only' | 'mixed'
    """

    student = _resolve_student_name(student, known_students)
    student = _normalize_name(student)

    # Vector store
    embedding = OllamaEmbeddings(model="mxbai-embed-large")
    db = Chroma(persist_directory="chroma", embedding_function=embedding)

    # Build filtered retrievers
    if student:
        student_filter = {"$and": [{"scope": "student"}, {"student": student}]}
    else:
        student_filter = None  # won’t be used if no student

    univ_filter = {"scope": "university"}

    student_ret = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 24, "lambda_mult": 0.5, "filter": student_filter},
    )
    univ_ret = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 6, "fetch_k": 24, "lambda_mult": 0.5, "filter": univ_filter},
    )

    # Multi-query prompt — preserve the student token if present
    template = (
        "Generate 4 alternative phrasings that preserve any named entities "
        "(do NOT change or drop the student name if present). "
        "Return one per line.\n\nOriginal: {q}"
    )
    prompt_perspectives = ChatPromptTemplate.from_template(template)

    # If we have a student, prepend a hard tag to make sure it flows through every variant
    seeded_q = f"[student={student}] {question}" if student else question

    generate_queries = (
        prompt_perspectives
        | ChatOllama(model="llama3.1:8b", temperature=0)
        | StrOutputParser()
        | (lambda x: [ln.strip() for ln in x.split("\n") if ln.strip()])
    )
    queries: List[str] = generate_queries.invoke({"q": seeded_q})

    # Retrieve
    student_docs: List = []
    univ_docs: List = []

    if intent in ("student_specific", "mixed") and student:
        for q in queries:
            student_docs.extend(student_ret.invoke(q))

    if intent in ("university_only", "mixed") or not student:
        for q in queries:
            univ_docs.extend(univ_ret.invoke(q))

    # Deduplicate by stable metadata; fall back to content if missing
    key_fn = lambda d: (d.metadata.get("source_path"), d.metadata.get("chunk_id"), d.page_content[:64])
    student_docs = _unique_by_key(student_docs, key_fn)
    univ_docs    = _unique_by_key(univ_docs, key_fn)

    # Compose final set (bias to student when applicable)
    if intent == "student_specific" and student:
        combined = student_docs[:8] + univ_docs[:4]
    elif intent == "mixed" and student:
        combined = student_docs[:6] + univ_docs[:6]
    else:  # university_only or no student detected
        combined = univ_docs[:10]

    return combined

if __name__ == "__main__":
    from routing import detect_route
    question1 = "What does Lucas Almeida's admission essay talk about?"
    question2 = "Does Sofia Martinez's admission essay relate to the university values?"
    question3 = "According to university guidelines, how long is the interview supposed to be"
    question4 = "Would you say Michael Jackson's cv is good"
    question5 = "What does Luca Almieda's admission essay talk about?"
    questions = [question1, question2, question3, question4, question5]
    for question in questions:
        known_students = get_known_students()
        route = detect_route(question, known_students)
        print(retriever(question, route.student, route.intent, known_students))
