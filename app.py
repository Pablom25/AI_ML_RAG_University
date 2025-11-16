import os

import streamlit as st

from doc_loader import doc_loader
from routing import get_known_students, detect_route
from retriever import retriever
from generator import generator


def _student_name_to_id(name: str) -> str:
    """
    Very simple rule for MVP:
    - Remove spaces
    - Leave other characters as-is

    Example:
      "Lucas Almeida" -> "LucasAlmeida"
    """
    return "".join(name.split())


def save_student_files(student_name: str,
                       cv_file,
                       essay_file,
                       rec_file):
    """
    Save uploaded files for a given student into:
      data/students/<StudentID>/

    File names :
      - cv.txt
      - admission_essay.txt
      - recommendation_1.txt
    """
    student_id = _student_name_to_id(student_name)

    base_dir = os.path.join("data", "students", student_id)
    os.makedirs(base_dir, exist_ok=True)

    # Helper to write a single uploaded file
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

    tab_ask, tab_add = st.tabs(["Ask Questions", "Add Student"])

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
                    # Rebuild or update Chroma from the data/ folder
                    doc_loader("data")

                with st.spinner("Routing your question..."):
                    known_students = get_known_students()
                    route = detect_route(question, known_students)

                with st.spinner("Retrieving relevant documents..."):
                    docs = retriever(
                        question=question,
                        student=route.student,
                        intent=route.intent,
                        known_students=known_students,
                    )

                with st.spinner("Generating answer..."):
                    answer = generator(docs, question)

                st.text_area("Answer:", value=answer, height=250)

    # ----------------------------
    # TAB 2: Add Student (new feature)
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


if __name__ == "__main__":
    main()
