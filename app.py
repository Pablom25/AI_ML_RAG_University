import streamlit as st
from doc_loader import doc_loader
from routing import detect_route, get_known_students
from retriever import retriever
from generator import generator
from decomposer import decompose_question

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

            # Check if complex reasoning needed
            reasoning_keywords = ["most common", "pattern", "relate", "align", "similar", "comparison"]
            is_complex = any(kw in question.lower() for kw in reasoning_keywords)
            
            if is_complex:
                with st.expander("📋 Question Breakdown"):
                    sub_questions = decompose_question(question)
                    for sub_q in sub_questions:
                        st.write(f"• {sub_q}")

            # Retrieve relevant docs
            docs = retriever(question, route.student, route.intent, known_students)
            
            with st.expander("📚 Retrieved Documents"):
                st.write(f"Found {len(docs)} relevant documents")

            # Generate answer
            answer = generator(docs, question)

            st.text_area("Answer:", value=answer, height=300)


if __name__ == "__main__":
    main()
