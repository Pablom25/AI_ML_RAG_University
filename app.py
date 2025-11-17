import os

import streamlit as st

from doc_loader import doc_loader
from routing import get_known_students, detect_route
from retriever import retriever
from generator import generator
from decomposer import decompose_question


def _student_name_to_id(name: str) -> str:
    return "".join(name.split())


def save_student_files(student_name: str,
                       cv_file,
                       essay_file,
                       rec_file):
    student_id = _student_name_to_id(student_name)
    base_dir = os.path.join("data", "students", student_id)
    os.makedirs(base_dir, exist_ok=True)
    def _save_uploaded(uploaded_file, filename: str):
        if uploaded_file is None:
            return
        target_path = os.path.join(base_dir, filename)
        with open(target_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    _save_uploaded(cv_file, "cv.txt")
    _save_uploaded(essay_file, "admission_essay.txt")
    _save_uploaded(rec_file, "recommendation_1.txt")
    return student_id, base_dir


def main():
    st.title("AI Admissions Helper")

    tab_ask, tab_add, tab_fit = st.tabs(["Ask Questions", "Add Student", "Student Fit Test"])

    # ----------------------------
    # TAB 1: Ask Questions (existing flow)
    # ----------------------------
    with tab_ask:
        st.header("Ask questions about students and the university")
        question = st.text_input("Enter your question:")
        if st.button("Submit", type="primary"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Building / updating knowledge base..."):
                    doc_loader("data")
                with st.spinner("Routing your question..."):
                    known_students = get_known_students()
                    route = detect_route(question, known_students)
                sub_questions = decompose_question(question)
                if len(sub_questions) > 1:
                    st.markdown("**Decomposed Sub-Questions:**")
                    for sq in sub_questions:
                        st.markdown(f"- {sq}")
                answers = []
                for sq in sub_questions:
                    docs = retriever(
                        question=sq,
                        student=route.student,
                        intent=route.intent,
                        known_students=known_students,
                    )
                    ans = generator(docs, sq)
                    answers.append(ans)
                if len(answers) == 1:
                    final_answer = answers[0]
                else:
                    final_answer = "Combined answer:\n" + "\n\n".join(
                        [f"Sub-question: {sub_questions[i]}\nAnswer: {answers[i]}" for i in range(len(answers))]
                    )
                st.text_area("Answer:", value=final_answer, height=250)

    # ----------------------------
    # TAB 2: Add Student (existing flow)
    # ----------------------------
    with tab_add:
        st.header("Add a new student ")
        st.markdown(
            "Fill in the student's name and upload **.txt** files. "
            "They will be stored under `data/students/<StudentID>/`."
        )
        student_name = st.text_input("Student name (e.g. Lucas Almeida)")
        cv_file = st.file_uploader(
            "Upload CV (.txt)", type=["txt"], key="cv_uploader"
        )
        essay_file = st.file_uploader(
            "Upload admission essay (.txt)", type=["txt"], key="essay_uploader"
        )
        rec_file = st.file_uploader(
            "Upload recommendation letter (.txt, optional)",
            type=["txt"],
            key="rec_uploader",
        )
        if st.button("Save student"):
            if not student_name.strip():
                st.error("Please enter a student name.")
            elif not any([cv_file, essay_file, rec_file]):
                st.error("Please upload at least one file for this student.")
            else:
                student_id, folder = save_student_files(
                    student_name=student_name,
                    cv_file=cv_file,
                    essay_file=essay_file,
                    rec_file=rec_file,
                )
                st.success(
                    f"Student **{student_name}** saved as folder "
                    f"`{student_id}` in `{folder}`.\n\n"
                    "You can now go to **Ask Questions** and query this student."
                )

    # ----------------------------
    # TAB 3: Student Fit Test (new feature)
    # ----------------------------
    with tab_fit:
        st.header("Test Student Fit for University")
        with st.spinner("Loading students..."):
            known_students = get_known_students()
        if not known_students:
            st.warning("No students found in the database.")
        else:
            student_display_names = [name.replace("_", " ").title() for name in known_students]
            selected_student = st.selectbox("Select a student to evaluate:", student_display_names)
            if st.button("Evaluate Fit"):
                student_id = _student_name_to_id(selected_student)
                fit_question = (
                    "Evaluate how well this student fits the university. "
                    "Consider their grades, alignment of goals and values with the university, "
                    "and relevance of their experience to their chosen degree. "
                    "Classify the fit as 'bad fit', 'medium fit', or 'good fit'. "
                    "Provide a summary of their profile and explain the rating."
                )
                docs = retriever(
                    question=fit_question,
                    student=student_id,
                    intent="mixed",
                    known_students=known_students,
                )
                fit_prompt = """You are an admissions expert. 
Given the following student documents and university information, evaluate the student's fit for the university.

CONTEXT:
{context}

INSTRUCTIONS:
- Assess grades, goals, values, and relevant experience.
- Classify the fit as 'bad fit', 'medium fit', or 'good fit'.
- Provide a concise summary of the student's profile.
- Explain clearly why you gave this rating.

Your answer should start with: "Fit: <bad fit/medium fit/good fit>"
Then provide the summary and explanation.
"""
                context = "\n\n".join([doc.page_content for doc in docs])
                from langchain.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import StrOutputParser
                from langchain_community.chat_models import ChatOllama
                prompt = ChatPromptTemplate.from_template(fit_prompt)
                llm = ChatOllama(model="llama3.1:8b", temperature=0)
                chain = prompt | llm | StrOutputParser()
                fit_answer = chain.invoke({"context": context})
                st.text_area("Student Fit Evaluation:", value=fit_answer, height=300)


if __name__ == "__main__":
    main()
