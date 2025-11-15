from pydantic import BaseModel, Field, field_validator
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from pathlib import Path
from typing import Optional

class Route(BaseModel):
    student: Optional[str] = Field(default=None)
    intent: str = Field(..., description="One of: student_specific, university_only, mixed")

    @field_validator("intent")
    @classmethod
    def _intent_ok(cls, v: str) -> str:
        allowed = {"student_specific", "university_only", "mixed"}
        if v not in allowed:
            raise ValueError(f"intent must be one of {allowed}")
        return v

def get_known_students(base_dir: str = "data/students") -> list[str]:
    path = Path(base_dir)
    if not path.exists():
        return []
    return [
        p.name.lower().replace(" ", "").replace("_", "")
        for p in path.iterdir() if p.is_dir()
    ]

def detect_route(question: str, known_students:list) -> Route:
    llm = ChatOllama(model="llama3.1:8b", temperature=0)
    parser = PydanticOutputParser(pydantic_object=Route)
    format_instructions = parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You extract routing info for RAG.\n"
            "Known students (case-insensitive): {known_students}\n"
            "If the question clearly references exactly one student, set intent=student_specific and "
            "student to that student's lowercased name with no spaces/underscores.\n"
            "If it is only about the university, intent=university_only and student=null.\n"
            "If both a student and general university info are relevant, intent=mixed and student=that student.\n"
            "{format_instructions}"
        ),
        ("human", "{question}")
    ])

    chain = prompt | llm | parser

    try:
        return chain.invoke({
            "question": question,
            "known_students": ", ".join(known_students) if known_students else "(none found)",
            "format_instructions": format_instructions,
        })
    except Exception:
        return Route(student=None, intent="university_only")

if __name__ == "__main__":
    question1 = "What does Lucas Almeida's admission essay talk about?"
    question2 = "Does Sofia Martinez's admission essay relate to the university values?"
    question3 = "According to university guidelines, how long is the interview supposed to be"
    known_students = get_known_students()
    print(detect_route(question1, known_students))
    print(detect_route(question2, known_students))
    print(detect_route(question3, known_students))
