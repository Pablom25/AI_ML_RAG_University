import streamlit as st
from doc_loader import doc_loader
from routing import detect_route, get_known_students
from retriever import retriever
from generator import generator

def main():
    st.title("AI Admissions Helper")

    question = st.text_input("Enter your question:")

    if st.button("Submit"):
        if question.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Build / update the Chroma DB with metadata
            doc_loader("data")

            # Route to relevant student and/or university data
            known_students = get_known_students()
            route = detect_route(question, known_students)

            # Retrieve relevant docs
            docs = retriever(question, route.student, route.intent, known_students)

            # Generate answer
            answer = generator(docs, question)

            st.text_area("Answer:", value=answer, height=200)


if __name__ == "__main__":
    main()
